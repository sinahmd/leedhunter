"""
Entity Resolution Orchestrator

This module orchestrates the entity resolution pipeline:
Candidate → Exact match → Deterministic match → Fuzzy match → Decision

FALSE MERGE IS MORE DANGEROUS THAN FALSE SPLIT
When uncertain, prefer POSSIBLE_MATCH or NEW_ENTITY over unsafe merge.
"""

from dataclasses import dataclass
from enum import Enum

from leedhunter.application.resolution.matchers import (
    DeterministicMatcher,
    ExactMatcher,
    FuzzyMatcher,
    MatchDecision,
    MatchExplanation,
)
from leedhunter.domain.models import Candidate, Entity


class ResolutionDecision(str, Enum):
    """Final resolution decision"""

    MATCH = "MATCH"
    POSSIBLE_MATCH = "POSSIBLE_MATCH"
    NEW_ENTITY = "NEW_ENTITY"


@dataclass
class ResolutionResult:
    """Result of entity resolution"""

    decision: ResolutionDecision
    matched_entity: Entity | None
    explanation: MatchExplanation
    confidence: float
    match_stage: str  # Which stage produced the match

    def to_dict(self) -> dict:
        """Convert to dictionary for logging/serialization"""
        return {
            "decision": self.decision.value,
            "matched_entity_id": self.matched_entity.id if self.matched_entity else None,
            "match_stage": self.match_stage,
            "confidence": self.confidence,
            "explanation": self.explanation.to_dict(),
        }


class EntityResolutionOrchestrator:
    """
    Orchestrates entity resolution using multiple matching strategies

    Resolution pipeline:
    1. Exact matching (identifiers)
    2. Deterministic matching (normalized identifiers)
    3. Fuzzy matching (name similarity)

    LLM-based matching is NOT used as first mechanism.
    It can be added later as a final arbiter for ambiguous cases.
    """

    def __init__(
        self,
        fuzzy_threshold: float = 0.85,
    ):
        """
        Initialize the orchestrator

        Args:
            fuzzy_threshold: Threshold for fuzzy matching (0-1)
        """
        self.exact_matcher = ExactMatcher()
        self.deterministic_matcher = DeterministicMatcher()
        self.fuzzy_matcher = FuzzyMatcher(threshold=fuzzy_threshold)

    def resolve(
        self,
        candidate: Candidate,
        existing_entities: list[Entity],
    ) -> ResolutionResult:
        """
        Resolve a candidate against existing entities

        Args:
            candidate: Candidate to resolve
            existing_entities: List of existing entities

        Returns:
            ResolutionResult with decision and explanation
        """
        # Step 1: Exact matching
        exact_result = self.exact_matcher.match(candidate, existing_entities)
        if exact_result:
            return ResolutionResult(
                decision=ResolutionDecision.MATCH,
                matched_entity=exact_result.entity,
                explanation=exact_result.explanation,
                confidence=exact_result.confidence,
                match_stage="exact",
            )

        # Step 2: Deterministic matching
        deterministic_result = self.deterministic_matcher.match(candidate, existing_entities)
        if deterministic_result:
            return ResolutionResult(
                decision=ResolutionDecision.MATCH,
                matched_entity=deterministic_result.entity,
                explanation=deterministic_result.explanation,
                confidence=deterministic_result.confidence,
                match_stage="deterministic",
            )

        # Step 3: Fuzzy matching
        fuzzy_result = self.fuzzy_matcher.match(candidate, existing_entities)
        if fuzzy_result:
            # Convert match decision to resolution decision
            if fuzzy_result.decision == MatchDecision.MATCH:
                decision = ResolutionDecision.MATCH
            else:
                decision = ResolutionDecision.POSSIBLE_MATCH

            return ResolutionResult(
                decision=decision,
                matched_entity=fuzzy_result.entity,
                explanation=fuzzy_result.explanation,
                confidence=fuzzy_result.confidence,
                match_stage="fuzzy",
            )

        # No match found - create new entity
        return ResolutionResult(
            decision=ResolutionDecision.NEW_ENTITY,
            matched_entity=None,
            explanation=MatchExplanation(
                decision=MatchDecision.NO_MATCH,
                score=0.0,
                matched_on=[],
                conflicts=[],
            ),
            confidence=0.0,
            match_stage="none",
        )

    def resolve_batch(
        self,
        candidates: list[Candidate],
        existing_entities: list[Entity],
    ) -> list[ResolutionResult]:
        """
        Resolve a batch of candidates

        Args:
            candidates: List of candidates to resolve
            existing_entities: List of existing entities

        Returns:
            List of ResolutionResult objects
        """
        return [self.resolve(candidate, existing_entities) for candidate in candidates]

    def explain_resolution(
        self,
        result: ResolutionResult,
    ) -> dict:
        """
        Generate detailed explanation of resolution

        Args:
            result: Resolution result

        Returns:
            Detailed explanation dictionary
        """
        return {
            "decision": result.decision.value,
            "match_stage": result.match_stage,
            "confidence": result.confidence,
            "matched_entity": {
                "id": result.matched_entity.id,
                "name": result.matched_entity.canonical_name,
                "domain": result.matched_entity.canonical_domain,
            }
            if result.matched_entity
            else None,
            "explanation": result.explanation.to_dict(),
            "recommendation": self._get_recommendation(result),
        }

    def _get_recommendation(self, result: ResolutionResult) -> str:
        """Get recommendation based on resolution result"""
        if result.decision == ResolutionDecision.MATCH:
            if result.confidence >= 0.9:
                return "High confidence match - safe to merge"
            else:
                return "Medium confidence match - verify before merging"
        elif result.decision == ResolutionDecision.POSSIBLE_MATCH:
            return "Possible match - requires human review before merging"
        else:
            return "No match - create new entity"
