"""
Tests for search planner module
"""

import pytest

from leedhunter.domain.models import SearchIntent
from leedhunter.domain.search.planner import (
    Concept,
    ConceptType,
    IntentAnalysis,
    IntentAnalyzer,
    QueryGenerator,
    SearchPlanner,
)


class TestIntentAnalyzer:
    """Tests for IntentAnalyzer"""

    def setup_method(self):
        """Set up test fixtures"""
        self.analyzer = IntentAnalyzer()

    def test_analyze_persian_intent(self):
        """Test analyzing Persian intent"""
        intent = SearchIntent(
            objective="Find auto importers in Mazandaran",
            location="Mazandaran",
            industry="Automotive",
        )
        analysis = self.analyzer.analyze(intent)

        assert analysis.industry == "automotive"
        assert analysis.location == "mazandaran"
        assert len(analysis.concepts) >= 2

    def test_analyze_english_intent(self):
        """Test analyzing English intent"""
        intent = SearchIntent(
            objective="Find automotive companies in Tehran",
        )
        analysis = self.analyzer.analyze(intent)

        assert analysis.industry == "automotive"
        assert analysis.location == "tehran"

    def test_analyze_persian_text(self):
        """Test analyzing Persian text"""
        intent = SearchIntent(
            objective="واردکنندگان خودرو در مازندران",
        )
        analysis = self.analyzer.analyze(intent)

        assert analysis.industry == "automotive"
        assert analysis.location == "mazandaran"
        assert "import" in analysis.actions

    def test_analyze_with_action(self):
        """Test extracting actions"""
        intent = SearchIntent(
            objective="Find importers of cars",
        )
        analysis = self.analyzer.analyze(intent)

        assert "import" in analysis.actions

    def test_analyze_with_platform(self):
        """Test extracting platforms"""
        intent = SearchIntent(
            objective="Find businesses on Instagram",
        )
        analysis = self.analyzer.analyze(intent)

        assert "instagram" in analysis.platforms

    def test_analyze_with_target(self):
        """Test extracting targets"""
        intent = SearchIntent(
            objective="Find companies and shops",
        )
        analysis = self.analyzer.analyze(intent)

        assert "business" in analysis.targets or "shop" in analysis.targets

    def test_analyze_explicit_location(self):
        """Test using explicit location from intent"""
        intent = SearchIntent(
            objective="Find businesses",
            location="Tehran",
        )
        analysis = self.analyzer.analyze(intent)

        assert analysis.location == "tehran"

    def test_analyze_explicit_industry(self):
        """Test using explicit industry from intent"""
        intent = SearchIntent(
            objective="Find companies",
            industry="Automotive",
        )
        analysis = self.analyzer.analyze(intent)

        assert analysis.industry == "automotive"

    def test_get_concepts_by_type(self):
        """Test getting concepts by type"""
        intent = SearchIntent(
            objective="Find auto importers in Mazandaran",
        )
        analysis = self.analyzer.analyze(intent)

        industry_concepts = analysis.get_concepts_by_type(ConceptType.INDUSTRY)
        assert len(industry_concepts) > 0
        assert industry_concepts[0].type == ConceptType.INDUSTRY


class TestQueryGenerator:
    """Tests for QueryGenerator"""

    def setup_method(self):
        """Set up test fixtures"""
        self.generator = QueryGenerator()

    def test_generate_basic_queries(self):
        """Test generating basic queries"""
        analysis = IntentAnalysis(
            original_intent=SearchIntent(objective="test"),
            industry="automotive",
            location="mazandaran",
            actions=["import"],
        )
        queries = self.generator.generate_queries(analysis)

        assert len(queries) > 0
        # Check that queries contain industry and location
        for query in queries:
            query_str = query.to_string()
            assert "automotive" in query_str or "mazandaran" in query_str

    def test_generate_platform_queries(self):
        """Test generating platform-specific queries"""
        analysis = IntentAnalysis(
            original_intent=SearchIntent(objective="test"),
            industry="automotive",
            location="mazandaran",
            actions=["import"],
            platforms=["instagram"],
        )
        queries = self.generator.generate_queries(analysis)

        # Check for site: operator
        site_queries = [q for q in queries if q.has_site_operator()]
        assert len(site_queries) > 0

    def test_generate_queries_with_constraints(self):
        """Test generating queries with constraints"""
        intent = SearchIntent(
            objective="Find auto importers",
            constraints=["used", "parts"],
        )
        analysis = IntentAnalysis(
            original_intent=intent,
            industry="automotive",
            location="mazandaran",
            actions=["import"],
        )
        queries = self.generator.generate_queries(analysis)

        # Check for exclusions
        exclusion_queries = [q for q in queries if len(q.exclusions) > 0]
        assert len(exclusion_queries) > 0

    def test_limit_queries(self):
        """Test limiting number of queries"""
        analysis = IntentAnalysis(
            original_intent=SearchIntent(objective="test"),
            industry="automotive",
            location="mazandaran",
            actions=["import", "export"],
            platforms=["instagram", "linkedin", "website"],
        )
        queries = self.generator.generate_queries(analysis, max_queries=5)

        assert len(queries) <= 5


class TestSearchPlanner:
    """Tests for SearchPlanner"""

    def setup_method(self):
        """Set up test fixtures"""
        self.planner = SearchPlanner()

    def test_plan_search(self):
        """Test planning a search"""
        intent = SearchIntent(
            objective="Find auto importers in Mazandaran",
            location="Mazandaran",
            industry="Automotive",
        )
        analysis, queries = self.planner.plan_search(intent)

        assert analysis is not None
        assert len(queries) > 0
        assert analysis.industry == "automotive"

    def test_plan_search_persian(self):
        """Test planning a Persian search"""
        intent = SearchIntent(
            objective="واردکنندگان خودرو در مازندران",
        )
        analysis, queries = self.planner.plan_search(intent)

        assert analysis is not None
        assert len(queries) > 0

    def test_explain_plan(self):
        """Test explaining a search plan"""
        intent = SearchIntent(
            objective="Find auto importers in Mazandaran",
        )
        analysis, queries = self.planner.plan_search(intent)
        explanation = self.planner.explain_plan(analysis, queries)

        assert "intent" in explanation
        assert "concepts" in explanation
        assert "queries" in explanation
        assert "total_queries" in explanation

    def test_plan_search_with_all_fields(self):
        """Test planning with all intent fields"""
        intent = SearchIntent(
            objective="Find automotive importers on Instagram",
            location="Mazandaran",
            industry="Automotive",
            constraints=["used"],
        )
        analysis, queries = self.planner.plan_search(intent, max_queries=5)

        assert analysis.industry == "automotive"
        assert analysis.location == "mazandaran"
        assert "import" in analysis.actions
        assert "instagram" in analysis.platforms
        assert len(queries) <= 5


class TestConcept:
    """Tests for Concept"""

    def test_create_concept(self):
        """Test creating a Concept"""
        concept = Concept(
            type=ConceptType.INDUSTRY,
            value="automotive",
            normalized="automotive",
        )
        assert concept.type == ConceptType.INDUSTRY
        assert concept.value == "automotive"

    def test_concept_str(self):
        """Test Concept string representation"""
        concept = Concept(
            type=ConceptType.LOCATION,
            value="Tehran",
            normalized="tehran",
        )
        assert "location" in str(concept)
        assert "Tehran" in str(concept)


class TestIntentAnalysis:
    """Tests for IntentAnalysis"""

    def test_create_analysis(self):
        """Test creating an IntentAnalysis"""
        intent = SearchIntent(objective="test")
        analysis = IntentAnalysis(original_intent=intent)

        assert analysis.original_intent == intent
        assert analysis.concepts == []
        assert analysis.industry is None

    def test_get_concepts_by_type(self):
        """Test getting concepts by type"""
        intent = SearchIntent(objective="test")
        analysis = IntentAnalysis(
            original_intent=intent,
            concepts=[
                Concept(type=ConceptType.INDUSTRY, value="auto", normalized="auto"),
                Concept(type=ConceptType.LOCATION, value="tehran", normalized="tehran"),
            ],
        )

        industry_concepts = analysis.get_concepts_by_type(ConceptType.INDUSTRY)
        assert len(industry_concepts) == 1
        assert industry_concepts[0].value == "auto"

        location_concepts = analysis.get_concepts_by_type(ConceptType.LOCATION)
        assert len(location_concepts) == 1
        assert location_concepts[0].value == "tehran"
