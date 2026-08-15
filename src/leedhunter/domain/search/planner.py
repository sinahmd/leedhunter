"""
Search Planner

This module implements the search planning pipeline:
Intent → Concepts → Query Families → Queries

It generates multiple search queries from a user's prospecting objective.
"""

from dataclasses import dataclass, field
from enum import Enum

from leedhunter.domain.models import SearchIntent
from leedhunter.domain.search.query import (
    Query,
    QueryBuilder,
)


class ConceptType(str, Enum):
    """Types of concepts extracted from intent"""

    INDUSTRY = "industry"
    LOCATION = "location"
    ACTION = "action"
    TARGET = "target"
    PLATFORM = "platform"
    MODIFIER = "modifier"


@dataclass
class Concept:
    """A concept extracted from the user's intent"""

    type: ConceptType
    value: str
    normalized: str
    confidence: float = 1.0

    def __str__(self) -> str:
        return f"{self.type.value}: {self.value}"


@dataclass
class IntentAnalysis:
    """Result of analyzing a search intent"""

    original_intent: SearchIntent
    concepts: list[Concept] = field(default_factory=list)
    industry: str | None = None
    location: str | None = None
    actions: list[str] = field(default_factory=list)
    targets: list[str] = field(default_factory=list)
    platforms: list[str] = field(default_factory=list)
    modifiers: list[str] = field(default_factory=list)

    def get_concepts_by_type(self, concept_type: ConceptType) -> list[Concept]:
        """Get all concepts of a specific type"""
        return [c for c in self.concepts if c.type == concept_type]


class IntentAnalyzer:
    """
    Analyzes user intent to extract concepts

    Extracts:
    - Industry (automotive, food, tech, etc.)
    - Location (city, province, country)
    - Action (import, export, manufacture, etc.)
    - Target (businesses, companies, shops)
    - Platform (instagram, linkedin, website)
    - Modifiers (new, used, wholesale, retail)
    """

    # Persian industry keywords
    INDUSTRY_KEYWORDS = {
        "automotive": ["خودرو", "automotive", "car", "auto", "vehicle", "ماشین"],
        "food": ["غذایی", "food", "restaurant", "cafe", "رستوران", "کافه"],
        "technology": ["فناوری", "technology", "tech", "IT", "نرم‌افزار", "software"],
        "construction": ["ساختمان", "construction", "building", "real estate", "ملک"],
        "clothing": ["پوشاک", "clothing", "fashion", "apparel", "لباس"],
        "electronics": ["الکترونیک", "electronics", "gadget", "device"],
        "healthcare": ["پزشکی", "healthcare", "medical", "hospital", "بیمارستان"],
        "education": ["آموزشی", "education", "school", "university", "دانشگاه"],
        "agriculture": ["کشاورزی", "agriculture", "farming", "crop"],
        "manufacturing": ["تولیدی", "manufacturing", "factory", "کارخانه"],
    }

    # Persian action keywords
    ACTION_KEYWORDS = {
        "import": ["واردات", "import", "importer", "واردکننده", "واردکنندگان"],
        "export": ["صادرات", "export", "exporter", "صادرکننده", "صادرکنندگان"],
        "manufacture": ["تولید", "manufacture", "producer", "تولیدکننده"],
        "wholesale": ["عمده‌فروشی", "wholesale", "wholesaler", "عمده"],
        "retail": ["خرده‌فروشی", "retail", "retailer", "خرده"],
        "distribute": ["توزیع", "distribute", "distributor", "توزیع‌کننده"],
        "supply": ["تأمین", "supply", "supplier", "تأمین‌کننده"],
    }

    # Persian location keywords (provinces)
    LOCATION_KEYWORDS = {
        "tehran": ["تهران", "tehran"],
        "mazandaran": ["مازندران", "mazandaran", "mazanderaan"],
        "isfahan": ["اصفهان", "isfahan"],
        "fars": ["فارس", "fars", "shiraz", "شیراز"],
        "khorasan": ["خراسان", "khorasan", "mashhad", "مشهد"],
        "azarbaijan": ["آذربایجان", "azarbaijan", "tabriz", "تبریز"],
        "gilan": ["گیلان", "gilan", "rasht", "رشت"],
        "kerman": ["کرمان", "kerman"],
        "khuzestan": ["خوزستان", "khuzestan", "ahvaz", "اهواز"],
        "alborz": ["البرز", "alborz", "karaj", "کرج"],
    }

    # Platform keywords
    PLATFORM_KEYWORDS = {
        "instagram": ["اینستاگرام", "instagram", "insta"],
        "linkedin": ["لینکدین", "linkedin"],
        "website": ["وب‌سایت", "website", "site", "سایت"],
        "telegram": ["تلگرام", "telegram"],
    }

    # Target keywords
    TARGET_KEYWORDS = {
        "business": ["کسب‌وکار", "business", "company", "شرکت"],
        "shop": ["فروشگاه", "shop", "store"],
        "factory": ["کارخانه", "factory"],
        "office": ["دفتر", "office"],
        "store": ["مغازه", "store"],
    }

    def analyze(self, intent: SearchIntent) -> IntentAnalysis:
        """
        Analyze a search intent and extract concepts

        Returns an IntentAnalysis with extracted concepts.
        """
        analysis = IntentAnalysis(original_intent=intent)
        text = intent.objective.lower()

        # Extract industry
        industry = self._extract_industry(text)
        if industry:
            analysis.industry = industry
            analysis.concepts.append(
                Concept(
                    type=ConceptType.INDUSTRY,
                    value=industry,
                    normalized=industry,
                )
            )

        # Extract location
        location = self._extract_location(text)
        if location:
            analysis.location = location
            analysis.concepts.append(
                Concept(
                    type=ConceptType.LOCATION,
                    value=location,
                    normalized=location,
                )
            )

        # Extract actions
        actions = self._extract_actions(text)
        analysis.actions = actions
        for action in actions:
            analysis.concepts.append(
                Concept(
                    type=ConceptType.ACTION,
                    value=action,
                    normalized=action,
                )
            )

        # Extract targets
        targets = self._extract_targets(text)
        analysis.targets = targets
        for target in targets:
            analysis.concepts.append(
                Concept(
                    type=ConceptType.TARGET,
                    value=target,
                    normalized=target,
                )
            )

        # Extract platforms
        platforms = self._extract_platforms(text)
        analysis.platforms = platforms
        for platform in platforms:
            analysis.concepts.append(
                Concept(
                    type=ConceptType.PLATFORM,
                    value=platform,
                    normalized=platform,
                )
            )

        # Use explicit location from intent if not found in text
        if not analysis.location and intent.location:
            analysis.location = intent.location.lower()
            analysis.concepts.append(
                Concept(
                    type=ConceptType.LOCATION,
                    value=intent.location,
                    normalized=intent.location,
                )
            )

        # Use explicit industry from intent if not found in text
        if not analysis.industry and intent.industry:
            analysis.industry = intent.industry.lower()
            analysis.concepts.append(
                Concept(
                    type=ConceptType.INDUSTRY,
                    value=intent.industry,
                    normalized=intent.industry,
                )
            )

        return analysis

    def _extract_industry(self, text: str) -> str | None:
        """Extract industry from text"""
        for industry, keywords in self.INDUSTRY_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    return industry
        return None

    def _extract_location(self, text: str) -> str | None:
        """Extract location from text"""
        for location, keywords in self.LOCATION_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    return location
        return None

    def _extract_actions(self, text: str) -> list[str]:
        """Extract actions from text"""
        actions = []
        for action, keywords in self.ACTION_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    if action not in actions:
                        actions.append(action)
                    break
        return actions

    def _extract_targets(self, text: str) -> list[str]:
        """Extract targets from text"""
        targets = []
        for target, keywords in self.TARGET_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    if target not in targets:
                        targets.append(target)
                    break
        return targets

    def _extract_platforms(self, text: str) -> list[str]:
        """Extract platforms from text"""
        platforms = []
        for platform, keywords in self.PLATFORM_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    if platform not in platforms:
                        platforms.append(platform)
                    break
        return platforms


class QueryGenerator:
    """
    Generates search queries from concepts

    Uses templates to create multiple query variations.
    """

    # Query templates for different scenarios
    TEMPLATES = [
        # Industry + Location + Action
        "{action} {industry} {location}",
        "{action} {industry} in {location}",
        "{location} {industry} {action}",
        # Industry + Location (Persian)
        "{industry} {location}",
        "{industry} در {location}",
        # Action + Industry + Platform
        "site:{platform}.com {action} {industry}",
        "site:{platform}.com {industry} {location}",
        # Persian variations
        "{action} {industry} {location}",
        "{industry} {action} {location}",
    ]

    # Platform-specific templates
    PLATFORM_TEMPLATES = {
        "instagram": [
            "site:instagram.com {industry} {location}",
            "site:instagram.com {action} {industry}",
            "site:instagram.com {industry} {action} {location}",
        ],
        "linkedin": [
            "site:linkedin.com {industry} {location}",
            "site:linkedin.com {action} {industry}",
        ],
        "website": [
            "{industry} {location} {action}",
            "{action} {industry} {location}",
        ],
    }

    def generate_queries(self, analysis: IntentAnalysis, max_queries: int = 10) -> list[Query]:
        """
        Generate search queries from intent analysis

        Returns a list of queries to execute.
        """
        queries = []

        # Get concepts
        industry = analysis.industry or ""
        location = analysis.location or ""
        actions = analysis.actions or ["find"]
        platforms = analysis.platforms or ["instagram", "linkedin", "website"]

        # Generate queries for each action
        for action in actions:
            # Basic queries
            queries.extend(self._generate_basic_queries(industry, location, action))

            # Platform-specific queries
            for platform in platforms:
                queries.extend(
                    self._generate_platform_queries(industry, location, action, platform)
                )

        # Add constraints as exclusions
        constraints = analysis.original_intent.constraints
        if constraints:
            for query in queries[:]:  # Copy list
                for constraint in constraints:
                    enhanced = QueryBuilder()
                    for term in query.terms:
                        enhanced.add_term(term.value)
                    for phrase in query.exact_phrases:
                        enhanced.add_exact_phrase(phrase.value)
                    for op in query.operators:
                        enhanced.add_operator(op.type, op.value)
                    enhanced.add_exclusion(constraint)
                    queries.append(enhanced.build())

        # Limit number of queries
        return queries[:max_queries]

    def _generate_basic_queries(
        self,
        industry: str,
        location: str,
        action: str,
    ) -> list[Query]:
        """Generate basic queries without platform"""
        queries = []

        if industry and location:
            # Industry + Location + Action
            builder = QueryBuilder()
            if action:
                builder.add_term(action)
            builder.add_term(industry)
            builder.add_term(location)
            queries.append(builder.build())

            # Persian format
            builder = QueryBuilder()
            builder.add_term(industry)
            builder.add_term(location)
            if action:
                builder.add_term(action)
            queries.append(builder.build())

        elif industry:
            # Just industry
            builder = QueryBuilder()
            builder.add_term(industry)
            if action:
                builder.add_term(action)
            queries.append(builder.build())

        return queries

    def _generate_platform_queries(
        self,
        industry: str,
        location: str,
        action: str,
        platform: str,
    ) -> list[Query]:
        """Generate platform-specific queries"""
        queries = []

        templates = self.PLATFORM_TEMPLATES.get(platform, [])

        for template in templates:
            try:
                query_str = template.format(
                    industry=industry,
                    location=location,
                    action=action,
                    platform=platform,
                )
                queries.append(QueryBuilder.from_string(query_str))
            except (KeyError, IndexError):
                continue

        return queries


class SearchPlanner:
    """
    Orchestrates the search planning process

    Intent → Analysis → Queries
    """

    def __init__(self):
        self.intent_analyzer = IntentAnalyzer()
        self.query_generator = QueryGenerator()

    def plan_search(
        self,
        intent: SearchIntent,
        max_queries: int = 10,
    ) -> tuple[IntentAnalysis, list[Query]]:
        """
        Plan a search from intent

        Returns:
            Tuple of (intent_analysis, queries)
        """
        # Step 1: Analyze intent
        analysis = self.intent_analyzer.analyze(intent)

        # Step 2: Generate queries
        queries = self.query_generator.generate_queries(analysis, max_queries)

        return analysis, queries

    def explain_plan(
        self,
        analysis: IntentAnalysis,
        queries: list[Query],
    ) -> dict:
        """
        Generate explanation of search plan

        Returns a structured explanation for debugging.
        """
        return {
            "intent": analysis.original_intent.objective,
            "concepts": {
                "industry": analysis.industry,
                "location": analysis.location,
                "actions": analysis.actions,
                "targets": analysis.targets,
                "platforms": analysis.platforms,
            },
            "queries": [
                {
                    "query": q.to_string(),
                    "terms": [t.value for t in q.terms],
                    "operators": [str(op) for op in q.operators],
                }
                for q in queries
            ],
            "total_queries": len(queries),
        }
