"""
Entity Resolution module

This module implements the entity resolution pipeline:
Candidate → Identity extraction → Exact matching → Deterministic matching
→ Fuzzy matching → Semantic matching → Decision

Decision: MATCH, POSSIBLE_MATCH, or NEW_ENTITY
"""

from leedhunter.application.resolution.matchers import (
    DeterministicMatcher,
    ExactMatcher,
    FuzzyMatcher,
    MatchExplanation,
    MatchResult,
)
from leedhunter.application.resolution.orchestrator import (
    EntityResolutionOrchestrator,
    ResolutionDecision,
    ResolutionResult,
)

__all__ = [
    # Orchestrator
    "EntityResolutionOrchestrator",
    "ResolutionResult",
    "ResolutionDecision",
    # Matchers
    "ExactMatcher",
    "DeterministicMatcher",
    "FuzzyMatcher",
    "MatchResult",
    "MatchExplanation",
]
