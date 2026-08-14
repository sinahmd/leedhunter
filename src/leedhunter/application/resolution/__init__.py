"""
Entity Resolution module

This module implements the entity resolution pipeline:
Candidate → Identity extraction → Exact matching → Deterministic matching
→ Fuzzy matching → Semantic matching → Decision

Decision: MATCH, POSSIBLE_MATCH, or NEW_ENTITY
"""

from leedhunter.application.resolution.orchestrator import (
    EntityResolutionOrchestrator,
    ResolutionResult,
    ResolutionDecision,
)

from leedhunter.application.resolution.matchers import (
    ExactMatcher,
    DeterministicMatcher,
    FuzzyMatcher,
    MatchResult,
    MatchExplanation,
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
