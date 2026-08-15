"""
Search domain module

This module implements the search query representation and manipulation.
It provides structured query construction with support for Persian/Arabic text.
"""

from leedhunter.domain.search.planner import (
    Concept,
    ConceptType,
    IntentAnalysis,
    IntentAnalyzer,
    QueryGenerator,
    SearchPlanner,
)
from leedhunter.domain.search.query import (
    ExactPhrase,
    Exclusion,
    IntitleOperator,
    InurlOperator,
    Operator,
    OperatorType,
    Query,
    QueryBuilder,
    QueryTerm,
    SiteOperator,
)

__all__ = [
    # Query
    "Query",
    "QueryTerm",
    "ExactPhrase",
    "Operator",
    "OperatorType",
    "SiteOperator",
    "IntitleOperator",
    "InurlOperator",
    "Exclusion",
    "QueryBuilder",
    # Planner
    "Concept",
    "ConceptType",
    "IntentAnalysis",
    "IntentAnalyzer",
    "QueryGenerator",
    "SearchPlanner",
]
