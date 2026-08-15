"""
Enrichment Service

This module enriches entities with additional data from web pages and profiles.

Enrichment extracts:
- Contact information (phone, email)
- Business details (address, description)
- Social media links
- Operating hours
- Services/products
"""

from dataclasses import dataclass, field

from leedhunter.domain.models import EntityIdentity


@dataclass
class EnrichedData:
    """Data enriched from external sources"""

    phones: list[str] = field(default_factory=list)
    emails: list[str] = field(default_factory=list)
    addresses: list[str] = field(default_factory=list)
    descriptions: list[str] = field(default_factory=list)
    social_links: dict[str, str] = field(default_factory=dict)
    services: list[str] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass
class EnrichmentResult:
    """Result of entity enrichment"""

    entity_id: str
    source: str
    source_url: str
    enriched_data: EnrichedData
    success: bool = True
    error_message: str | None = None
    new_identities: list[EntityIdentity] = field(default_factory=list)


class EnrichmentService:
    """
    Enriches entities with additional data.

    This is a base implementation that can be extended with real web scraping.
    """

    def enrich_from_url(
        self,
        entity_id: str,
        url: str,
        source: str = "web",
    ) -> EnrichmentResult:
        """
        Enrich entity from a URL

        Args:
            entity_id: Entity ID to enrich
            url: URL to scrape
            source: Source name

        Returns:
            EnrichmentResult with enriched data
        """
        # This would be a real web scraper in production
        # For now, return empty enrichment
        return EnrichmentResult(
            entity_id=entity_id,
            source=source,
            source_url=url,
            enriched_data=EnrichedData(),
        )

    def extract_contact_info(
        self,
        text: str,
    ) -> dict[str, list[str]]:
        """
        Extract contact information from text

        Args:
            text: Text to extract from

        Returns:
            Dictionary with phones, emails, etc.
        """
        import re

        result = {
            "phones": [],
            "emails": [],
        }

        # Extract emails
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        emails = re.findall(email_pattern, text)
        result["emails"] = list(set(emails))

        # Extract phone numbers (basic pattern)
        phone_pattern = r"[\+]?[(]?[0-9]{1,4}[)]?[-\s\./0-9]{7,}"
        phones = re.findall(phone_pattern, text)
        result["phones"] = list(set(phones))

        return result

    def extract_social_links(
        self,
        text: str,
    ) -> dict[str, str]:
        """
        Extract social media links from text

        Args:
            text: Text to extract from

        Returns:
            Dictionary mapping platform to URL
        """
        import re

        social_links = {}

        # Instagram
        instagram_pattern = r"(?:https?://)?(?:www\.)?instagram\.com/([a-zA-Z0-9_\.]+)/?"
        instagram_match = re.search(instagram_pattern, text)
        if instagram_match:
            social_links["instagram"] = f"https://instagram.com/{instagram_match.group(1)}"

        # LinkedIn
        linkedin_pattern = r"(?:https?://)?(?:www\.)?linkedin\.com/(?:in|company)/([a-zA-Z0-9-]+)/?"
        linkedin_match = re.search(linkedin_pattern, text)
        if linkedin_match:
            social_links["linkedin"] = f"https://linkedin.com/in/{linkedin_match.group(1)}"

        return social_links

    def merge_enriched_data(
        self,
        existing: EnrichedData,
        new: EnrichedData,
    ) -> EnrichedData:
        """
        Merge enriched data, avoiding duplicates

        Args:
            existing: Existing enriched data
            new: New enriched data to merge

        Returns:
            Merged EnrichedData
        """
        merged = EnrichedData()

        # Merge phones
        all_phones = set(existing.phones + new.phones)
        merged.phones = list(all_phones)

        # Merge emails
        all_emails = set(existing.emails + new.emails)
        merged.emails = list(all_emails)

        # Merge addresses
        all_addresses = set(existing.addresses + new.addresses)
        merged.addresses = list(all_addresses)

        # Merge descriptions
        merged.descriptions = existing.descriptions + new.descriptions

        # Merge social links
        merged.social_links = {**existing.social_links, **new.social_links}

        # Merge services
        all_services = set(existing.services + new.services)
        merged.services = list(all_services)

        # Merge metadata
        merged.metadata = {**existing.metadata, **new.metadata}

        return merged
