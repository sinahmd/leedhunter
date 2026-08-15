"""
Evidence Deduplicator

This module removes duplicate evidence items.

Evidence is considered duplicate if:
- Same entity_id
- Same claim
- Same value (normalized)
- Same source
"""

from dataclasses import dataclass, field

from leedhunter.application.evidence.collector import CollectedEvidence
from leedhunter.domain.normalization import normalize_text


@dataclass
class DeduplicationResult:
    """Result of evidence deduplication"""

    unique_evidence: list[CollectedEvidence] = field(default_factory=list)
    duplicates_removed: int = 0
    duplicate_groups: list[list[CollectedEvidence]] = field(default_factory=list)


class EvidenceDeduplicator:
    """
    Deduplicates evidence items

    Keeps the highest confidence evidence when duplicates are found.
    Preserves all sources for provenance.
    """

    def deduplicate(
        self,
        evidence_list: list[CollectedEvidence],
    ) -> DeduplicationResult:
        """
        Deduplicate evidence

        Args:
            evidence_list: List of evidence to deduplicate

        Returns:
            DeduplicationResult with unique evidence and statistics
        """
        result = DeduplicationResult()

        # Group by (entity_id, claim, normalized_value)
        groups: dict[str, list[CollectedEvidence]] = {}

        for evidence in evidence_list:
            key = self._make_key(evidence)
            if key not in groups:
                groups[key] = []
            groups[key].append(evidence)

        # Process groups
        for _key, group in groups.items():
            if len(group) == 1:
                result.unique_evidence.append(group[0])
            else:
                # Keep highest confidence
                best = max(group, key=lambda e: e.confidence)
                result.unique_evidence.append(best)
                result.duplicates_removed += len(group) - 1
                result.duplicate_groups.append(group)

        return result

    def _make_key(self, evidence: CollectedEvidence) -> str:
        """Create a key for deduplication"""
        normalized_value = normalize_text(evidence.value).lower()
        return f"{evidence.entity_id}:{evidence.claim}:{normalized_value}"
