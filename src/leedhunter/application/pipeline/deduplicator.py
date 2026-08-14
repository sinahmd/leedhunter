"""
Candidate Deduplicator

This module removes duplicate candidates within a search result set.

Deduplication at multiple levels:
- Search Result
- Candidate
- Identity

If 10 queries discover the same Instagram profile:
10 discoveries → 1 identity → 1 entity

But preserve all discovery provenance.
"""

from dataclasses import dataclass, field
from typing import Optional

from leedhunter.application.pipeline.extractor import ExtractedCandidate, ExtractedIdentity
from leedhunter.domain.models import EntityIdentityType
from leedhunter.domain.normalization import normalize_domain, normalize_phone


@dataclass
class DeduplicationResult:
    """Result of deduplication"""

    unique_candidates: list[ExtractedCandidate] = field(default_factory=list)
    duplicates_removed: int = 0
    duplicate_groups: list[list[ExtractedCandidate]] = field(default_factory=list)


class CandidateDeduplicator:
    """
    Deduplicates candidates based on identities

    Uses a priority-based approach:
    1. Exact domain match
    2. Exact email match
    3. Exact phone match
    4. Exact username match (same platform)
    """

    def deduplicate(
        self,
        candidates: list[ExtractedCandidate],
    ) -> DeduplicationResult:
        """
        Deduplicate candidates

        Args:
            candidates: List of extracted candidates

        Returns:
            DeduplicationResult with unique candidates and statistics
        """
        result = DeduplicationResult()

        # Track seen identities
        seen_domains: dict[str, ExtractedCandidate] = {}
        seen_emails: dict[str, ExtractedCandidate] = {}
        seen_phones: dict[str, ExtractedCandidate] = {}
        seen_usernames: dict[str, tuple[str, ExtractedCandidate]] = {}  # (platform, candidate)

        unique = []
        duplicate_groups: dict[str, list[ExtractedCandidate]] = {}

        for candidate in candidates:
            is_duplicate = False
            duplicate_key = None

            # Check for domain match
            domain = self._get_domain(candidate)
            if domain:
                normalized_domain = normalize_domain(domain)
                if normalized_domain in seen_domains:
                    is_duplicate = True
                    duplicate_key = f"domain:{normalized_domain}"
                else:
                    seen_domains[normalized_domain] = candidate

            # Check for email match
            if not is_duplicate:
                email = self._get_email(candidate)
                if email:
                    normalized_email = email.lower()
                    if normalized_email in seen_emails:
                        is_duplicate = True
                        duplicate_key = f"email:{normalized_email}"
                    else:
                        seen_emails[normalized_email] = candidate

            # Check for phone match
            if not is_duplicate:
                phone = self._get_phone(candidate)
                if phone:
                    normalized_phone = normalize_phone(phone)
                    if normalized_phone and normalized_phone in seen_phones:
                        is_duplicate = True
                        duplicate_key = f"phone:{normalized_phone}"
                    elif normalized_phone:
                        seen_phones[normalized_phone] = candidate

            # Check for username match (same platform)
            if not is_duplicate:
                username_info = self._get_username(candidate)
                if username_info:
                    platform, username = username_info
                    key = f"{platform}:{username.lower()}"
                    if key in seen_usernames:
                        is_duplicate = True
                        duplicate_key = f"username:{key}"
                    else:
                        seen_usernames[key] = (platform, candidate)

            if is_duplicate:
                result.duplicates_removed += 1
                if duplicate_key:
                    if duplicate_key not in duplicate_groups:
                        duplicate_groups[duplicate_key] = []
                    duplicate_groups[duplicate_key].append(candidate)
            else:
                unique.append(candidate)

        result.unique_candidates = unique
        result.duplicate_groups = list(duplicate_groups.values())

        return result

    def _get_domain(self, candidate: ExtractedCandidate) -> Optional[str]:
        """Get domain from candidate"""
        # Check identities
        for identity in candidate.identities:
            if identity.type == EntityIdentityType.WEBSITE:
                return identity.value
        # Check candidate
        return candidate.candidate.observed_domain

    def _get_email(self, candidate: ExtractedCandidate) -> Optional[str]:
        """Get email from candidate"""
        for identity in candidate.identities:
            if identity.type == EntityIdentityType.EMAIL:
                return identity.value
        return candidate.candidate.observed_email

    def _get_phone(self, candidate: ExtractedCandidate) -> Optional[str]:
        """Get phone from candidate"""
        for identity in candidate.identities:
            if identity.type == EntityIdentityType.PHONE:
                return identity.value
        return candidate.candidate.observed_phone

    def _get_username(self, candidate: ExtractedCandidate) -> Optional[tuple[str, str]]:
        """Get username and platform from candidate"""
        for identity in candidate.identities:
            if identity.type in [EntityIdentityType.INSTAGRAM, EntityIdentityType.LINKEDIN]:
                return (identity.type.value, identity.value)
        return None
