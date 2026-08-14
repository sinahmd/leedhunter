"""
Evidence Collector

This module collects evidence from various sources and creates Evidence objects.

Every important fact must be traceable with:
- source
- source_url
- claim
- value
- confidence
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from leedhunter.domain.models import Evidence


@dataclass
class CollectedEvidence:
    """Evidence collected from a source"""

    entity_id: str
    claim: str
    value: str
    source: str
    source_url: str
    confidence: float
    metadata: dict[str, Any] = field(default_factory=dict)
    observed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_evidence(self) -> Evidence:
        """Convert to domain Evidence model"""
        return Evidence(
            entity_id=self.entity_id,
            claim=self.claim,
            value=self.value,
            source=self.source,
            source_url=self.source_url,
            observed_at=self.observed_at,
            confidence=self.confidence,
        )


class EvidenceCollector:
    """
    Collects evidence from various sources

    This is the main entry point for creating evidence.
    It ensures all evidence has proper provenance.
    """

    def collect(
        self,
        entity_id: str,
        claim: str,
        value: str,
        source: str,
        source_url: str,
        confidence: float = 1.0,
        metadata: Optional[dict[str, Any]] = None,
    ) -> CollectedEvidence:
        """
        Collect evidence

        Args:
            entity_id: ID of the entity this evidence is about
            claim: The claim being made
            value: The value of the claim
            source: Source of the evidence
            source_url: URL of the source
            confidence: Confidence score (0-1)
            metadata: Optional additional metadata

        Returns:
            CollectedEvidence object
        """
        return CollectedEvidence(
            entity_id=entity_id,
            claim=claim,
            value=value,
            source=source,
            source_url=source_url,
            confidence=max(0.0, min(1.0, confidence)),
            metadata=metadata or {},
        )

    def collect_from_candidate(
        self,
        entity_id: str,
        candidate: Any,
    ) -> list[CollectedEvidence]:
        """
        Collect evidence from a candidate

        Args:
            entity_id: ID of the entity
            candidate: Candidate object

        Returns:
            List of collected evidence
        """
        evidence_list = []

        # Collect name evidence
        if candidate.observed_name:
            evidence_list.append(self.collect(
                entity_id=entity_id,
                claim="business_name",
                value=candidate.observed_name,
                source=candidate.source,
                source_url=candidate.source_url,
                confidence=0.9,
            ))

        # Collect domain evidence
        if candidate.observed_domain:
            evidence_list.append(self.collect(
                entity_id=entity_id,
                claim="website_domain",
                value=candidate.observed_domain,
                source=candidate.source,
                source_url=candidate.source_url,
                confidence=0.95,
            ))

        # Collect phone evidence
        if candidate.observed_phone:
            evidence_list.append(self.collect(
                entity_id=entity_id,
                claim="phone_number",
                value=candidate.observed_phone,
                source=candidate.source,
                source_url=candidate.source_url,
                confidence=0.85,
            ))

        # Collect email evidence
        if candidate.observed_email:
            evidence_list.append(self.collect(
                entity_id=entity_id,
                claim="email_address",
                value=candidate.observed_email,
                source=candidate.source,
                source_url=candidate.source_url,
                confidence=0.85,
            ))

        return evidence_list

    def collect_batch(
        self,
        entity_id: str,
        claims: list[dict[str, Any]],
    ) -> list[CollectedEvidence]:
        """
        Collect multiple evidence items

        Args:
            entity_id: ID of the entity
            claims: List of claim dictionaries

        Returns:
            List of collected evidence
        """
        evidence_list = []

        for claim_data in claims:
            evidence = self.collect(
                entity_id=entity_id,
                claim=claim_data.get("claim", ""),
                value=claim_data.get("value", ""),
                source=claim_data.get("source", "unknown"),
                source_url=claim_data.get("source_url", ""),
                confidence=claim_data.get("confidence", 0.5),
                metadata=claim_data.get("metadata"),
            )
            evidence_list.append(evidence)

        return evidence_list
