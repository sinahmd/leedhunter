"""
Search Query AST (Abstract Syntax Tree)

This module provides structured query representation for search engines.
It supports Persian/Arabic text and various search operators.

Do NOT construct search queries through uncontrolled string concatenation.
Use this structured representation instead.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union

from leedhunter.domain.normalization import normalize_text


class OperatorType(str, Enum):
    """Types of search operators"""

    SITE = "site"
    INTITLE = "intitle"
    INURL = "inurl"


@dataclass(frozen=True)
class QueryTerm:
    """
    A single search term

    Represents a word or phrase to search for.
    """

    value: str
    normalized: str = field(init=False)

    def __post_init__(self):
        """Normalize the term on creation"""
        object.__setattr__(self, "normalized", normalize_text(self.value))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ExactPhrase:
    """
    An exact phrase to search for

    Will be quoted in the search query.
    """

    value: str
    normalized: str = field(init=False)

    def __post_init__(self):
        """Normalize the phrase on creation"""
        object.__setattr__(self, "normalized", normalize_text(self.value))

    def __str__(self) -> str:
        return f'"{self.value}"'


@dataclass(frozen=True)
class Operator:
    """
    A search operator

    Examples:
    - site:instagram.com
    - intitle:import
    - inurl:contact
    """

    type: OperatorType
    value: str

    def __str__(self) -> str:
        return f"{self.type.value}:{self.value}"


@dataclass(frozen=True)
class SiteOperator(Operator):
    """Site operator (site:example.com)"""

    type: OperatorType = field(default=OperatorType.SITE, init=False)

    def __init__(self, domain: str):
        object.__setattr__(self, "value", domain)

    def __str__(self) -> str:
        return f"site:{self.value}"


@dataclass(frozen=True)
class IntitleOperator(Operator):
    """Intitle operator (intitle:keyword)"""

    type: OperatorType = field(default=OperatorType.INTITLE, init=False)

    def __init__(self, keyword: str):
        object.__setattr__(self, "value", keyword)

    def __str__(self) -> str:
        return f"intitle:{self.value}"


@dataclass(frozen=True)
class InurlOperator(Operator):
    """Inurl operator (inurl:path)"""

    type: OperatorType = field(default=OperatorType.INURL, init=False)

    def __init__(self, path: str):
        object.__setattr__(self, "value", path)

    def __str__(self) -> str:
        return f"inurl:{self.value}"


@dataclass(frozen=True)
class Exclusion:
    """
    A term to exclude from search

    Will be prefixed with - in the search query.
    """

    value: str
    normalized: str = field(init=False)

    def __post_init__(self):
        """Normalize the exclusion on creation"""
        object.__setattr__(self, "normalized", normalize_text(self.value))

    def __str__(self) -> str:
        return f"-{self.value}"


@dataclass
class Query:
    """
    Structured search query

    Represents a complete search query with terms, phrases, operators, and exclusions.
    This is the core AST node for search queries.
    """

    terms: list[QueryTerm] = field(default_factory=list)
    exact_phrases: list[ExactPhrase] = field(default_factory=list)
    operators: list[Operator] = field(default_factory=list)
    exclusions: list[Exclusion] = field(default_factory=list)
    provider: Optional[str] = None

    def to_string(self) -> str:
        """
        Convert query to string representation

        This produces a valid search engine query string.
        """
        parts = []

        # Add operators
        for op in self.operators:
            parts.append(str(op))

        # Add exact phrases
        for phrase in self.exact_phrases:
            parts.append(str(phrase))

        # Add terms
        for term in self.terms:
            parts.append(str(term))

        # Add exclusions
        for exclusion in self.exclusions:
            parts.append(str(exclusion))

        return " ".join(parts)

    def is_empty(self) -> bool:
        """Check if query is empty"""
        return (
            len(self.terms) == 0
            and len(self.exact_phrases) == 0
            and len(self.operators) == 0
            and len(self.exclusions) == 0
        )

    def get_normalized_terms(self) -> list[str]:
        """Get all normalized terms"""
        terms = []
        for term in self.terms:
            terms.append(term.normalized)
        for phrase in self.exact_phrases:
            terms.append(phrase.normalized)
        return terms

    def get_operators_by_type(self, op_type: OperatorType) -> list[Operator]:
        """Get all operators of a specific type"""
        return [op for op in self.operators if op.type == op_type]

    def has_site_operator(self) -> bool:
        """Check if query has a site operator"""
        return any(op.type == OperatorType.SITE for op in self.operators)

    def get_site_domain(self) -> Optional[str]:
        """Get the domain from site operator"""
        for op in self.operators:
            if op.type == OperatorType.SITE:
                return op.value
        return None

    def validate(self) -> list[str]:
        """
        Validate the query

        Returns a list of validation errors (empty if valid).
        """
        errors = []

        if self.is_empty():
            errors.append("Query is empty")
            return errors

        # Validate terms
        for term in self.terms:
            if not term.value.strip():
                errors.append("Empty term found")

        # Validate exact phrases
        for phrase in self.exact_phrases:
            if not phrase.value.strip():
                errors.append("Empty exact phrase found")

        # Validate operators
        for op in self.operators:
            if not op.value.strip():
                errors.append(f"Empty operator value for {op.type}")

        # Validate exclusions
        for exclusion in self.exclusions:
            if not exclusion.value.strip():
                errors.append("Empty exclusion found")

        return errors

    def is_valid(self) -> bool:
        """Check if query is valid"""
        return len(self.validate()) == 0

    def __str__(self) -> str:
        return self.to_string()


class QueryBuilder:
    """
    Fluent query builder

    Provides a convenient way to construct queries with method chaining.

    Example:
        query = (
            QueryBuilder()
            .add_term("import")
            .add_exact_phrase("واردات خودرو")
            .add_site("instagram.com")
            .add_exclusion("used")
            .build()
        )
    """

    def __init__(self):
        self._terms: list[QueryTerm] = []
        self._exact_phrases: list[ExactPhrase] = []
        self._operators: list[Operator] = []
        self._exclusions: list[Exclusion] = []
        self._provider: Optional[str] = None

    def add_term(self, value: str) -> "QueryBuilder":
        """Add a search term"""
        if value and value.strip():
            self._terms.append(QueryTerm(value=value.strip()))
        return self

    def add_exact_phrase(self, value: str) -> "QueryBuilder":
        """Add an exact phrase"""
        if value and value.strip():
            self._exact_phrases.append(ExactPhrase(value=value.strip()))
        return self

    def add_operator(self, op_type: OperatorType, value: str) -> "QueryBuilder":
        """Add a search operator"""
        if value and value.strip():
            self._operators.append(Operator(type=op_type, value=value.strip()))
        return self

    def add_site(self, domain: str) -> "QueryBuilder":
        """Add a site operator"""
        if domain and domain.strip():
            self._operators.append(SiteOperator(domain=domain.strip()))
        return self

    def add_intitle(self, keyword: str) -> "QueryBuilder":
        """Add an intitle operator"""
        if keyword and keyword.strip():
            self._operators.append(IntitleOperator(keyword=keyword.strip()))
        return self

    def add_inurl(self, path: str) -> "QueryBuilder":
        """Add an inurl operator"""
        if path and path.strip():
            self._operators.append(InurlOperator(path=path.strip()))
        return self

    def add_exclusion(self, value: str) -> "QueryBuilder":
        """Add an exclusion"""
        if value and value.strip():
            self._exclusions.append(Exclusion(value=value.strip()))
        return self

    def set_provider(self, provider: str) -> "QueryBuilder":
        """Set the search provider"""
        self._provider = provider
        return self

    def build(self) -> Query:
        """Build the query"""
        return Query(
            terms=self._terms,
            exact_phrases=self._exact_phrases,
            operators=self._operators,
            exclusions=self._exclusions,
            provider=self._provider,
        )

    @staticmethod
    def from_string(query_string: str) -> Query:
        """
        Parse a query string into a Query object

        This is a simple parser that handles basic query syntax.
        For complex queries, use the builder instead.
        """
        builder = QueryBuilder()

        # Simple tokenization
        tokens = query_string.split()
        i = 0
        while i < len(tokens):
            token = tokens[i]

            # Handle site: operator
            if token.startswith("site:"):
                domain = token[5:]
                builder.add_site(domain)

            # Handle intitle: operator
            elif token.startswith("intitle:"):
                keyword = token[8:]
                builder.add_intitle(keyword)

            # Handle inurl: operator
            elif token.startswith("inurl:"):
                path = token[6:]
                builder.add_inurl(path)

            # Handle exact phrase
            elif token.startswith('"'):
                # Find closing quote
                phrase_parts = [token[1:]]
                while i + 1 < len(tokens) and not tokens[i].endswith('"'):
                    i += 1
                    phrase_parts.append(tokens[i])
                # Remove trailing quote
                phrase = " ".join(phrase_parts)
                if phrase.endswith('"'):
                    phrase = phrase[:-1]
                builder.add_exact_phrase(phrase)

            # Handle exclusion
            elif token.startswith("-"):
                value = token[1:]
                if value:
                    builder.add_exclusion(value)

            # Regular term
            else:
                builder.add_term(token)

            i += 1

        return builder.build()
