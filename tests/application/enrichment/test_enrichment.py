"""
Tests for enrichment service
"""

import pytest

from leedhunter.application.enrichment.enricher import (
    EnrichmentService,
    EnrichmentResult,
    EnrichedData,
)


class TestEnrichedData:
    """Tests for EnrichedData"""

    def test_create_empty(self):
        """Test creating empty EnrichedData"""
        data = EnrichedData()

        assert data.phones == []
        assert data.emails == []
        assert data.addresses == []

    def test_create_with_data(self):
        """Test creating EnrichedData with data"""
        data = EnrichedData(
            phones=["+98 912 123 4567"],
            emails=["test@example.com"],
            addresses=["Tehran, Iran"],
        )

        assert len(data.phones) == 1
        assert len(data.emails) == 1


class TestEnrichmentResult:
    """Tests for EnrichmentResult"""

    def test_create_result(self):
        """Test creating EnrichmentResult"""
        result = EnrichmentResult(
            entity_id="entity_1",
            source="web",
            source_url="https://example.com",
            enriched_data=EnrichedData(),
        )

        assert result.entity_id == "entity_1"
        assert result.success is True


class TestEnrichmentService:
    """Tests for EnrichmentService"""

    def setup_method(self):
        """Set up test fixtures"""
        self.service = EnrichmentService()

    def test_enrich_from_url(self):
        """Test enriching from URL"""
        result = self.service.enrich_from_url(
            entity_id="entity_1",
            url="https://example.com",
        )

        assert result.entity_id == "entity_1"
        assert result.source_url == "https://example.com"
        assert result.success is True

    def test_extract_contact_info_emails(self):
        """Test extracting emails"""
        text = "Contact us at info@example.com or support@example.com"
        result = self.service.extract_contact_info(text)

        assert "info@example.com" in result["emails"]
        assert "support@example.com" in result["emails"]

    def test_extract_contact_info_phones(self):
        """Test extracting phones"""
        text = "Call us at +98 912 123 4567 or 021-1234-5678"
        result = self.service.extract_contact_info(text)

        assert len(result["phones"]) > 0

    def test_extract_contact_info_persian(self):
        """Test extracting contact info from Persian text"""
        text = "تماس: info@example.com تلفن: ۰۹۱۲۱۲۳۴۵۶۷"
        result = self.service.extract_contact_info(text)

        assert "info@example.com" in result["emails"]

    def test_extract_social_links_instagram(self):
        """Test extracting Instagram links"""
        text = "Follow us on https://instagram.com/test_business"
        result = self.service.extract_social_links(text)

        assert "instagram" in result
        assert "test_business" in result["instagram"]

    def test_extract_social_links_linkedin(self):
        """Test extracting LinkedIn links"""
        text = "Connect on https://linkedin.com/in/test-user"
        result = self.service.extract_social_links(text)

        assert "linkedin" in result

    def test_extract_social_links_multiple(self):
        """Test extracting multiple social links"""
        text = """
        Instagram: https://instagram.com/test
        LinkedIn: https://linkedin.com/in/test
        """
        result = self.service.extract_social_links(text)

        assert "instagram" in result
        assert "linkedin" in result

    def test_merge_enriched_data(self):
        """Test merging enriched data"""
        existing = EnrichedData(
            phones=["+98 912 123 4567"],
            emails=["test@example.com"],
        )
        new = EnrichedData(
            phones=["+98 912 123 4567", "+98 912 987 6543"],
            emails=["info@example.com"],
        )

        merged = self.service.merge_enriched_data(existing, new)

        assert len(merged.phones) == 2  # Deduplicated
        assert len(merged.emails) == 2

    def test_merge_enriched_data_social_links(self):
        """Test merging social links"""
        existing = EnrichedData(
            social_links={"instagram": "https://instagram.com/test"},
        )
        new = EnrichedData(
            social_links={"linkedin": "https://linkedin.com/in/test"},
        )

        merged = self.service.merge_enriched_data(existing, new)

        assert "instagram" in merged.social_links
        assert "linkedin" in merged.social_links
