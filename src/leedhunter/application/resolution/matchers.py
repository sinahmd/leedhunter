"""
Entity Resolution Matchers

This module implements different matching strategies for entity resolution:
- Exact matching (identifiers)
- Deterministic matching (normalized identifiers)
- Fuzzy matching (name similarity)

NEVER use an LLM as the first mechanism for entity matching.
Prefer: exact identifiers → deterministic matching → fuzzy matching → semantic matching → LLM arbitration
"""

from dataclasses import dataclass, field
from enum import Enum

from leedhunter.domain.models import (
    Candidate,
    Entity,
    EntityIdentityType,
)
from leedhunter.domain.normalization import (
    normalize_domain,
    normalize_phone,
    normalize_text,
)


class MatchDecision(str, Enum):
    """Decision from matching"""

    MATCH = "MATCH"
    POSSIBLE_MATCH = "POSSIBLE_MATCH"
    NO_MATCH = "NO_MATCH"


@dataclass
class MatchExplanation:
    """Structured explanation for a match decision"""

    decision: MatchDecision
    score: float
    matched_on: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    details: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "decision": self.decision.value,
            "score": self.score,
            "matched": self.matched_on,
            "conflicts": self.conflicts,
            "details": self.details,
        }


@dataclass
class MatchResult:
    """Result of a matching operation"""

    decision: MatchDecision
    entity: Entity | None
    explanation: MatchExplanation
    confidence: float


class ExactMatcher:
    """
    Exact matcher using identifiers

    Matches:
    - Exact domain
    - Exact email
    - Exact phone (normalized)
    - Exact username on same platform
    """

    def match(
        self,
        candidate: Candidate,
        entities: list[Entity],
    ) -> MatchResult | None:
        """
        Try to match candidate against entities using exact identifiers

        Args:
            candidate: Candidate to match
            entities: List of existing entities

        Returns:
            MatchResult if exact match found, None otherwise
        """
        for entity in entities:
            explanation = self._check_match(candidate, entity)
            if explanation.decision == MatchDecision.MATCH:
                return MatchResult(
                    decision=MatchDecision.MATCH,
                    entity=entity,
                    explanation=explanation,
                    confidence=1.0,
                )
        return None

    def _check_match(
        self,
        candidate: Candidate,
        entity: Entity,
    ) -> MatchExplanation:
        """Check if candidate matches entity exactly"""
        matched_on = []
        conflicts = []

        # Check domain match
        if candidate.observed_domain and entity.canonical_domain:
            if candidate.observed_domain.lower() == entity.canonical_domain.lower():
                matched_on.append("exact_domain")
            elif normalize_domain(candidate.observed_domain) == normalize_domain(
                entity.canonical_domain
            ):
                matched_on.append("normalized_domain")

        # Check email match
        if candidate.observed_email:
            for identity in entity.identities:
                if identity.type == EntityIdentityType.EMAIL:
                    if identity.normalized_value.lower() == candidate.observed_email.lower():
                        matched_on.append("exact_email")

        # Check phone match
        if candidate.observed_phone:
            normalized_candidate_phone = normalize_phone(candidate.observed_phone)
            for identity in entity.identities:
                if identity.type == EntityIdentityType.PHONE:
                    normalized_entity_phone = normalize_phone(identity.normalized_value)
                    if normalized_candidate_phone == normalized_entity_phone:
                        matched_on.append("exact_phone")

        # Check username match
        if candidate.observed_username:
            platform = candidate.metadata.get("platform", "").lower()
            for identity in entity.identities:
                if identity.type == self._platform_to_identity_type(platform):
                    if identity.normalized_value.lower() == candidate.observed_username.lower():
                        matched_on.append(f"exact_{platform}_username")

        # Decision
        if matched_on:
            decision = MatchDecision.MATCH
            score = min(1.0, len(matched_on) * 0.3)
        else:
            decision = MatchDecision.NO_MATCH
            score = 0.0

        return MatchExplanation(
            decision=decision,
            score=score,
            matched_on=matched_on,
            conflicts=conflicts,
        )

    def _platform_to_identity_type(self, platform: str) -> EntityIdentityType:
        """Convert platform string to identity type"""
        platform_map = {
            "instagram": EntityIdentityType.INSTAGRAM,
            "linkedin": EntityIdentityType.LINKEDIN,
            "website": EntityIdentityType.WEBSITE,
        }
        return platform_map.get(platform, EntityIdentityType.WEBSITE)


class DeterministicMatcher:
    """
    Deterministic matcher using normalized identifiers

    Matches:
    - Normalized domain (removing www., http://, etc.)
    - Normalized phone (removing spaces, dashes, country codes)
    """

    def match(
        self,
        candidate: Candidate,
        entities: list[Entity],
    ) -> MatchResult | None:
        """
        Try to match candidate against entities using normalized identifiers

        Args:
            candidate: Candidate to match
            entities: List of existing entities

        Returns:
            MatchResult if deterministic match found, None otherwise
        """
        for entity in entities:
            explanation = self._check_match(candidate, entity)
            if explanation.decision == MatchDecision.MATCH:
                return MatchResult(
                    decision=MatchDecision.MATCH,
                    entity=entity,
                    explanation=explanation,
                    confidence=0.9,
                )
        return None

    def _check_match(
        self,
        candidate: Candidate,
        entity: Entity,
    ) -> MatchExplanation:
        """Check if candidate matches entity deterministically"""
        matched_on = []
        conflicts = []

        # Check normalized domain
        if candidate.observed_domain and entity.canonical_domain:
            norm_candidate = normalize_domain(candidate.observed_domain)
            norm_entity = normalize_domain(entity.canonical_domain)
            if norm_candidate == norm_entity:
                matched_on.append("normalized_domain")

        # Check normalized phone
        if candidate.observed_phone:
            norm_candidate_phone = normalize_phone(candidate.observed_phone)
            for identity in entity.identities:
                if identity.type == EntityIdentityType.PHONE:
                    norm_entity_phone = normalize_phone(identity.normalized_value)
                    if norm_candidate_phone == norm_entity_phone:
                        matched_on.append("normalized_phone")

        # Decision
        if matched_on:
            decision = MatchDecision.MATCH
            score = min(1.0, len(matched_on) * 0.4)
        else:
            decision = MatchDecision.NO_MATCH
            score = 0.0

        return MatchExplanation(
            decision=decision,
            score=score,
            matched_on=matched_on,
            conflicts=conflicts,
        )


class FuzzyMatcher:
    """
    Fuzzy matcher using name similarity

    This is conservative - only returns matches with very high similarity
    to avoid false merges.

    NEVER merge two businesses merely because their names are similar.
    """

    def __init__(self, threshold: float = 0.85):
        """
        Initialize fuzzy matcher

        Args:
            threshold: Minimum similarity score for a match (0-1)
        """
        self.threshold = threshold

    def match(
        self,
        candidate: Candidate,
        entities: list[Entity],
    ) -> MatchResult | None:
        """
        Try to match candidate against entities using fuzzy name matching

        Args:
            candidate: Candidate to match
            entities: List of existing entities

        Returns:
            MatchResult if fuzzy match found, None otherwise
        """
        if not candidate.observed_name:
            return None

        best_match = None
        best_score = 0.0

        for entity in entities:
            score = self._calculate_similarity(candidate.observed_name, entity.canonical_name)

            if score >= self.threshold and score > best_score:
                best_score = score
                best_match = entity

        if best_match:
            # Check if it's an exact match (should be MATCH, not POSSIBLE_MATCH)
            decision = MatchDecision.MATCH if best_score >= 1.0 else MatchDecision.POSSIBLE_MATCH

            explanation = MatchExplanation(
                decision=decision,
                score=best_score,
                matched_on=["fuzzy_name_match"],
                conflicts=[],
                details={
                    "candidate_name": candidate.observed_name,
                    "entity_name": best_match.canonical_name,
                    "similarity": best_score,
                },
            )

            return MatchResult(
                decision=decision,
                entity=best_match,
                explanation=explanation,
                confidence=best_score,
            )

        return None

    def _calculate_similarity(self, name1: str, name2: str) -> float:
        """
        Calculate similarity between two names

        Uses normalized text comparison with multiple strategies:
        1. Exact match after normalization
        2. Jaccard similarity on character bigrams
        3. Levenshtein-like ratio
        """
        # Normalize both names
        norm1 = normalize_text(name1).lower().strip()
        norm2 = normalize_text(name2).lower().strip()

        # Exact match
        if norm1 == norm2:
            return 1.0

        # Empty strings
        if not norm1 or not norm2:
            return 0.0

        # Jaccard similarity on bigrams
        bigrams1 = set(norm1[i : i + 2] for i in range(len(norm1) - 1))
        bigrams2 = set(norm2[i : i + 2] for i in range(len(norm2) - 1))

        if not bigrams1 or not bigrams2:
            return 0.0

        intersection = bigrams1 & bigrams2
        union = bigrams1 | bigrams2

        jaccard = len(intersection) / len(union)

        # Length ratio penalty
        len_ratio = min(len(norm1), len(norm2)) / max(len(norm1), len(norm2))

        # Combined score
        return jaccard * 0.7 + len_ratio * 0.3
