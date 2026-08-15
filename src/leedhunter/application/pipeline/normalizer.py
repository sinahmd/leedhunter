"""
Result Normalizer

This module normalizes search results from different providers into
a consistent format for further processing.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from leedhunter.domain.models import Candidate
from leedhunter.domain.normalization import (
    normalize_domain,
    normalize_email,
    normalize_phone,
    normalize_text,
    normalize_username,
)


@dataclass
class NormalizedResult:
    """A normalized search result"""

    # Source information
    source: str
    source_url: str
    query_id: str | None = None

    # Business information
    name: str | None = None
    name_normalized: str | None = None
    domain: str | None = None
    domain_normalized: str | None = None

    # Contact information
    phone: str | None = None
    phone_normalized: str | None = None
    email: str | None = None
    email_normalized: str | None = None

    # Social media
    username: str | None = None
    username_normalized: str | None = None
    platform: str | None = None

    # Additional metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    # Timestamps
    discovered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_candidate(self) -> Candidate:
        """Convert to domain Candidate model"""
        return Candidate(
            source=self.source,
            source_url=self.source_url,
            observed_name=self.name,
            observed_domain=self.domain,
            observed_username=self.username,
            observed_phone=self.phone,
            observed_email=self.email,
            metadata=self.metadata,
            discovered_at=self.discovered_at,
            query_id=self.query_id,
        )


class ResultNormalizer:
    """
    Normalizes search results from different providers

    Handles:
    - Different field names across providers
    - Persian/Arabic text normalization
    - Domain normalization
    - Phone number normalization
    - Email normalization
    """

    def normalize(
        self,
        raw_result: dict[str, Any],
        source: str,
        query_id: str | None = None,
    ) -> NormalizedResult:
        """
        Normalize a raw search result

        Args:
            raw_result: Raw result dictionary from provider
            source: Source provider name
            query_id: Optional query ID for provenance

        Returns:
            NormalizedResult with normalized fields
        """
        result = NormalizedResult(
            source=source,
            source_url=raw_result.get("source_url", ""),
            query_id=query_id,
        )

        # Extract and normalize name
        result.name = self._extract_name(raw_result)
        if result.name:
            result.name_normalized = normalize_text(result.name)

        # Extract and normalize domain
        result.domain = self._extract_domain(raw_result)
        if result.domain:
            result.domain_normalized = normalize_domain(result.domain)

        # Extract and normalize phone
        result.phone = self._extract_phone(raw_result)
        if result.phone:
            result.phone_normalized = normalize_phone(result.phone)

        # Extract and normalize email
        result.email = self._extract_email(raw_result)
        if result.email:
            result.email_normalized = normalize_email(result.email)

        # Extract and normalize username
        result.username = self._extract_username(raw_result)
        if result.username:
            result.username_normalized = normalize_username(result.username)

        # Extract platform
        result.platform = self._extract_platform(raw_result)

        # Copy metadata
        result.metadata = raw_result.get("metadata", {})

        return result

    def normalize_batch(
        self,
        raw_results: list[dict[str, Any]],
        source: str,
        query_id: str | None = None,
    ) -> list[NormalizedResult]:
        """
        Normalize a batch of raw results

        Args:
            raw_results: List of raw result dictionaries
            source: Source provider name
            query_id: Optional query ID

        Returns:
            List of NormalizedResult objects
        """
        return [self.normalize(result, source, query_id) for result in raw_results]

    def _extract_name(self, raw_result: dict[str, Any]) -> str | None:
        """Extract business name from raw result"""
        # Try different field names
        for field_name in ["observed_name", "name", "title", "business_name"]:
            if field_name in raw_result and raw_result[field_name]:
                return raw_result[field_name]
        return None

    def _extract_domain(self, raw_result: dict[str, Any]) -> str | None:
        """Extract domain from raw result"""
        # Try direct domain field
        if "observed_domain" in raw_result and raw_result["observed_domain"]:
            return raw_result["observed_domain"]

        # Try to extract from URL
        url = raw_result.get("source_url", "")
        if url:
            try:
                from urllib.parse import urlparse

                parsed = urlparse(url)
                if parsed.netloc:
                    return parsed.netloc
            except Exception:
                pass

        return None

    def _extract_phone(self, raw_result: dict[str, Any]) -> str | None:
        """Extract phone number from raw result"""
        for field_name in ["observed_phone", "phone", "telephone", "mobile"]:
            if field_name in raw_result and raw_result[field_name]:
                return raw_result[field_name]
        return None

    def _extract_email(self, raw_result: dict[str, Any]) -> str | None:
        """Extract email from raw result"""
        for field_name in ["observed_email", "email", "contact_email"]:
            if field_name in raw_result and raw_result[field_name]:
                return raw_result[field_name]
        return None

    def _extract_username(self, raw_result: dict[str, Any]) -> str | None:
        """Extract username from raw result"""
        for field_name in ["observed_username", "username", "handle"]:
            if field_name in raw_result and raw_result[field_name]:
                return raw_result[field_name]
        return None

    def _extract_platform(self, raw_result: dict[str, Any]) -> str | None:
        """Extract platform from raw result"""
        # Try direct platform field
        if "platform" in raw_result:
            return raw_result["platform"]

        # Try from metadata
        metadata = raw_result.get("metadata", {})
        if "platform" in metadata:
            return metadata["platform"]

        # Try to infer from URL
        url = raw_result.get("source_url", "").lower()
        if "instagram.com" in url:
            return "instagram"
        elif "linkedin.com" in url:
            return "linkedin"
        elif "twitter.com" in url or "x.com" in url:
            return "twitter"
        elif "facebook.com" in url:
            return "facebook"

        return None
