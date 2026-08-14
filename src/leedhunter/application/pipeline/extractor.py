"""
Candidate Extractor

This module extracts candidates and identities from normalized results.
"""

from dataclasses import dataclass, field
from typing import Optional

from leedhunter.application.pipeline.normalizer import NormalizedResult
from leedhunter.domain.models import (
    Candidate,
    EntityIdentity,
    EntityIdentityType,
)
from leedhunter.domain.normalization import normalize_domain


@dataclass
class ExtractedIdentity:
    """An extracted identity from a result"""

    type: EntityIdentityType
    value: str
    normalized_value: str
    source: str
    source_url: str
    is_primary: bool = False

    def to_entity_identity(self) -> EntityIdentity:
        """Convert to domain EntityIdentity model"""
        return EntityIdentity(
            type=self.type,
            value=self.value,
            normalized_value=self.normalized_value,
            is_primary=self.is_primary,
            is_verified=False,
            source=self.source,
            source_url=self.source_url,
        )


@dataclass
class ExtractedCandidate:
    """An extracted candidate with identities"""

    candidate: Candidate
    identities: list[ExtractedIdentity] = field(default_factory=list)
    confidence: float = 1.0


class IdentityExtractor:
    """
    Extracts identities from normalized results

    Identifies and extracts:
    - Website identities (domain)
    - Instagram identities (username)
    - LinkedIn identities (username)
    - Phone identities
    - Email identities
    """

    def extract(self, result: NormalizedResult) -> list[ExtractedIdentity]:
        """
        Extract identities from a normalized result

        Args:
            result: Normalized result

        Returns:
            List of extracted identities
        """
        identities = []

        # Extract domain identity
        if result.domain:
            identities.append(ExtractedIdentity(
                type=EntityIdentityType.WEBSITE,
                value=result.domain,
                normalized_value=result.domain_normalized or normalize_domain(result.domain),
                source=result.source,
                source_url=result.source_url,
                is_primary=True,  # Website is usually primary
            ))

        # Extract Instagram identity
        if result.platform == "instagram" and result.username:
            identities.append(ExtractedIdentity(
                type=EntityIdentityType.INSTAGRAM,
                value=result.username,
                normalized_value=result.username_normalized or result.username.lower(),
                source=result.source,
                source_url=result.source_url,
            ))

        # Extract LinkedIn identity
        elif result.platform == "linkedin" and result.username:
            identities.append(ExtractedIdentity(
                type=EntityIdentityType.LINKEDIN,
                value=result.username,
                normalized_value=result.username_normalized or result.username.lower(),
                source=result.source,
                source_url=result.source_url,
            ))

        # Extract phone identity
        if result.phone:
            identities.append(ExtractedIdentity(
                type=EntityIdentityType.PHONE,
                value=result.phone,
                normalized_value=result.phone_normalized or result.phone,
                source=result.source,
                source_url=result.source_url,
            ))

        # Extract email identity
        if result.email:
            identities.append(ExtractedIdentity(
                type=EntityIdentityType.EMAIL,
                value=result.email,
                normalized_value=result.email_normalized or result.email.lower(),
                source=result.source,
                source_url=result.source_url,
            ))

        return identities

    def extract_batch(
        self,
        results: list[NormalizedResult],
    ) -> list[tuple[NormalizedResult, list[ExtractedIdentity]]]:
        """
        Extract identities from a batch of results

        Args:
            results: List of normalized results

        Returns:
            List of (result, identities) tuples
        """
        return [
            (result, self.extract(result))
            for result in results
        ]


class CandidateExtractor:
    """
    Extracts candidates from normalized results

    Combines result normalization with identity extraction
    to produce complete candidate objects.
    """

    def __init__(self):
        self.identity_extractor = IdentityExtractor()

    def extract(self, result: NormalizedResult) -> ExtractedCandidate:
        """
        Extract a candidate from a normalized result

        Args:
            result: Normalized result

        Returns:
            ExtractedCandidate with candidate and identities
        """
        # Extract identities
        identities = self.identity_extractor.extract(result)

        # Create candidate
        candidate = result.to_candidate()

        # Calculate confidence based on available information
        confidence = self._calculate_confidence(result, identities)

        return ExtractedCandidate(
            candidate=candidate,
            identities=identities,
            confidence=confidence,
        )

    def extract_batch(
        self,
        results: list[NormalizedResult],
    ) -> list[ExtractedCandidate]:
        """
        Extract candidates from a batch of results

        Args:
            results: List of normalized results

        Returns:
            List of ExtractedCandidate objects
        """
        return [self.extract(result) for result in results]

    def _calculate_confidence(
        self,
        result: NormalizedResult,
        identities: list[ExtractedIdentity],
    ) -> float:
        """
        Calculate confidence score for a candidate

        Higher confidence when:
        - Has a name
        - Has multiple identities
        - Has verified information

        Args:
            result: Normalized result
            identities: Extracted identities

        Returns:
            Confidence score between 0 and 1
        """
        score = 0.0

        # Base score for having a result
        score += 0.2

        # Score for having a name
        if result.name:
            score += 0.2

        # Score for having identities
        if identities:
            score += 0.2
            # Bonus for multiple identities
            score += min(0.2, len(identities) * 0.05)

        # Score for having contact information
        if result.phone or result.email:
            score += 0.1

        # Score for having a domain
        if result.domain:
            score += 0.1

        return min(1.0, score)
