"""
LLM Arbiter

Minimal LLM assistance for AMBIGUOUS entity matches only.

Flow:
Deterministic matching → ambiguous candidate → optional LLM recommendation
→ existing Entity Resolution orchestrator makes the final decision.

LLM saying SAME must NOT directly merge entities.
Final merge/dedup decision belongs to the deterministic Entity Resolution layer.
"""

from dataclasses import dataclass

from leedhunter.application.llm.parser import LLMResponseParser
from leedhunter.application.llm.provider import LLMProvider
from leedhunter.application.llm.schemas import EntityComparisonResult
from leedhunter.domain.models import Candidate, Entity


@dataclass
class ArbitrationResult:
    """Result of LLM arbitration for ambiguous match"""

    recommendation: str  # SAME, DIFFERENT, AMBIGUOUS
    confidence: float
    reasons: list[str]
    matched_on: list[str]
    conflicts: list[str]
    is_llm_available: bool

    def should_merge(self, min_confidence: float = 0.8) -> bool:
        """
        Check if LLM recommends merge with sufficient confidence.

        NOTE: This is only a recommendation. The orchestrator makes the final decision.
        """
        return (
            self.recommendation == "SAME"
            and self.confidence >= min_confidence
            and self.is_llm_available
        )


class LLMArbiter:
    """
    Minimal LLM arbiter for ambiguous entity matches.

    This is OPTIONAL. The system works fully without it.
    It provides recommendations, not decisions.
    """

    def __init__(
        self,
        llm_provider: LLMProvider | None = None,
    ):
        self._llm = llm_provider
        self._parser = LLMResponseParser()

    def is_available(self) -> bool:
        """Check if LLM arbiter is available"""
        return self._llm is not None

    async def arbitrate(
        self,
        candidate: Candidate,
        entity: Entity,
    ) -> ArbitrationResult:
        """
        Get LLM recommendation for ambiguous entity match.

        Args:
            candidate: Candidate being matched
            entity: Existing entity to compare against

        Returns:
            ArbitrationResult with recommendation (NOT a decision)
        """
        if not self._llm:
            return ArbitrationResult(
                recommendation="AMBIGUOUS",
                confidence=0.0,
                reasons=["LLM not available"],
                matched_on=[],
                conflicts=[],
                is_llm_available=False,
            )

        # Build evidence-scoped comparison input
        candidate_info = self._extract_candidate_info(candidate)
        entity_info = self._extract_entity_info(entity)

        # Get LLM comparison
        response = await self._llm.compare_entities(candidate_info, entity_info)

        # Parse and validate
        parse_result = self._parser.parse(response, EntityComparisonResult)

        if not parse_result.is_success():
            return ArbitrationResult(
                recommendation="AMBIGUOUS",
                confidence=0.0,
                reasons=[f"LLM response invalid: {parse_result.error_message}"],
                matched_on=[],
                conflicts=[],
                is_llm_available=True,
            )

        result = parse_result.get_data()

        return ArbitrationResult(
            recommendation=result.decision,
            confidence=result.confidence,
            reasons=result.reasons,
            matched_on=result.matched_on,
            conflicts=result.conflicts,
            is_llm_available=True,
        )

    def _extract_candidate_info(self, candidate: Candidate) -> dict:
        """Extract candidate info for comparison (only observed facts)"""
        info = {}
        if candidate.observed_name:
            info["name"] = candidate.observed_name
        if candidate.observed_domain:
            info["domain"] = candidate.observed_domain
        if candidate.observed_phone:
            info["phone"] = candidate.observed_phone
        if candidate.observed_email:
            info["email"] = candidate.observed_email
        if candidate.observed_username:
            info["username"] = candidate.observed_username
        info["source"] = candidate.source
        info["source_url"] = candidate.source_url
        return info

    def _extract_entity_info(self, entity: Entity) -> dict:
        """Extract entity info for comparison"""
        info = {
            "name": entity.canonical_name,
        }
        if entity.canonical_domain:
            info["domain"] = entity.canonical_domain
        if entity.identities:
            info["identities"] = [
                {"type": i.type.value, "value": i.value} for i in entity.identities
            ]
        return info
