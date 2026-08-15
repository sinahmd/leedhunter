"""
Tests for evidence engine
"""

from leedhunter.application.evidence.collector import CollectedEvidence, EvidenceCollector
from leedhunter.application.evidence.deduplicator import EvidenceDeduplicator
from leedhunter.application.evidence.validator import EvidenceValidator, ValidationStatus


class TestEvidenceCollector:
    """Tests for EvidenceCollector"""

    def setup_method(self):
        """Set up test fixtures"""
        self.collector = EvidenceCollector()

    def test_collect_basic(self):
        """Test collecting basic evidence"""
        evidence = self.collector.collect(
            entity_id="entity_1",
            claim="business_name",
            value="Test Business",
            source="google",
            source_url="https://google.com",
            confidence=0.9,
        )

        assert evidence.entity_id == "entity_1"
        assert evidence.claim == "business_name"
        assert evidence.value == "Test Business"
        assert evidence.confidence == 0.9

    def test_collect_with_metadata(self):
        """Test collecting evidence with metadata"""
        evidence = self.collector.collect(
            entity_id="entity_1",
            claim="phone_number",
            value="+98 912 123 4567",
            source="instagram",
            source_url="https://instagram.com/test",
            confidence=0.85,
            metadata={"verified": True},
        )

        assert evidence.metadata == {"verified": True}

    def test_collect_clamps_confidence(self):
        """Test that confidence is clamped to 0-1"""
        evidence = self.collector.collect(
            entity_id="entity_1",
            claim="test",
            value="test",
            source="test",
            source_url="https://test.com",
            confidence=1.5,
        )

        assert evidence.confidence == 1.0

    def test_collect_from_candidate(self):
        """Test collecting evidence from candidate"""
        from leedhunter.domain.models import Candidate

        candidate = Candidate(
            source="google",
            source_url="https://example.com",
            observed_name="Test Business",
            observed_domain="example.com",
            observed_phone="+98 912 123 4567",
            observed_email="test@example.com",
        )

        evidence_list = self.collector.collect_from_candidate("entity_1", candidate)

        assert len(evidence_list) == 4
        claims = [e.claim for e in evidence_list]
        assert "business_name" in claims
        assert "website_domain" in claims
        assert "phone_number" in claims
        assert "email_address" in claims

    def test_collect_batch(self):
        """Test collecting batch of evidence"""
        claims = [
            {
                "claim": "business_name",
                "value": "Test",
                "source": "google",
                "source_url": "https://google.com",
                "confidence": 0.9,
            },
            {
                "claim": "phone",
                "value": "1234567890",
                "source": "instagram",
                "source_url": "https://instagram.com",
                "confidence": 0.8,
            },
        ]

        evidence_list = self.collector.collect_batch("entity_1", claims)

        assert len(evidence_list) == 2


class TestEvidenceValidator:
    """Tests for EvidenceValidator"""

    def setup_method(self):
        """Set up test fixtures"""
        self.validator = EvidenceValidator()

    def test_validate_valid_evidence(self):
        """Test validating valid evidence"""
        evidence = CollectedEvidence(
            entity_id="entity_1",
            claim="business_name",
            value="Test Business",
            source="google",
            source_url="https://google.com",
            confidence=0.9,
        )

        result = self.validator.validate(evidence)

        assert result.is_valid()
        assert result.status == ValidationStatus.VALID
        assert len(result.errors) == 0

    def test_validate_missing_entity_id(self):
        """Test validation with missing entity_id"""
        evidence = CollectedEvidence(
            entity_id="",
            claim="test",
            value="test",
            source="test",
            source_url="https://test.com",
            confidence=0.9,
        )

        result = self.validator.validate(evidence)

        assert not result.is_valid()
        assert result.status == ValidationStatus.INVALID
        assert "Missing entity_id" in result.errors

    def test_validate_missing_source(self):
        """Test validation with missing source (warning)"""
        evidence = CollectedEvidence(
            entity_id="entity_1",
            claim="test",
            value="test",
            source="",
            source_url="",
            confidence=0.9,
        )

        result = self.validator.validate(evidence)

        assert result.status == ValidationStatus.WARNING
        assert len(result.warnings) > 0

    def test_validate_invalid_phone(self):
        """Test validation with invalid phone"""
        evidence = CollectedEvidence(
            entity_id="entity_1",
            claim="phone_number",
            value="invalid",
            source="test",
            source_url="https://test.com",
            confidence=0.9,
        )

        result = self.validator.validate(evidence)

        assert not result.is_valid()
        assert any("phone" in e.lower() for e in result.errors)

    def test_validate_invalid_email(self):
        """Test validation with invalid email"""
        evidence = CollectedEvidence(
            entity_id="entity_1",
            claim="email_address",
            value="invalid",
            source="test",
            source_url="https://test.com",
            confidence=0.9,
        )

        result = self.validator.validate(evidence)

        assert not result.is_valid()
        assert any("email" in e.lower() for e in result.errors)

    def test_validate_valid_phone(self):
        """Test validation with valid phone"""
        evidence = CollectedEvidence(
            entity_id="entity_1",
            claim="phone_number",
            value="+98 912 123 4567",
            source="test",
            source_url="https://test.com",
            confidence=0.9,
        )

        result = self.validator.validate(evidence)

        assert result.is_valid()

    def test_validate_valid_email(self):
        """Test validation with valid email"""
        evidence = CollectedEvidence(
            entity_id="entity_1",
            claim="email_address",
            value="test@example.com",
            source="test",
            source_url="https://test.com",
            confidence=0.9,
        )

        result = self.validator.validate(evidence)

        assert result.is_valid()

    def test_validate_batch(self):
        """Test validating batch of evidence"""
        evidence_list = [
            CollectedEvidence(
                entity_id="entity_1",
                claim="test",
                value="test",
                source="test",
                source_url="https://test.com",
                confidence=0.9,
            ),
            CollectedEvidence(
                entity_id="entity_2",
                claim="test",
                value="test",
                source="test",
                source_url="https://test.com",
                confidence=0.9,
            ),
        ]

        results = self.validator.validate_batch(evidence_list)

        assert len(results) == 2


class TestEvidenceDeduplicator:
    """Tests for EvidenceDeduplicator"""

    def setup_method(self):
        """Set up test fixtures"""
        self.deduplicator = EvidenceDeduplicator()

    def test_deduplicate_no_duplicates(self):
        """Test deduplication with no duplicates"""
        evidence_list = [
            CollectedEvidence(
                entity_id="entity_1",
                claim="business_name",
                value="Test 1",
                source="google",
                source_url="https://google.com",
                confidence=0.9,
            ),
            CollectedEvidence(
                entity_id="entity_1",
                claim="phone",
                value="1234567890",
                source="google",
                source_url="https://google.com",
                confidence=0.8,
            ),
        ]

        result = self.deduplicator.deduplicate(evidence_list)

        assert len(result.unique_evidence) == 2
        assert result.duplicates_removed == 0

    def test_deduplicate_with_duplicates(self):
        """Test deduplication with duplicates"""
        evidence_list = [
            CollectedEvidence(
                entity_id="entity_1",
                claim="business_name",
                value="Test Business",
                source="google",
                source_url="https://google.com",
                confidence=0.9,
            ),
            CollectedEvidence(
                entity_id="entity_1",
                claim="business_name",
                value="Test Business",
                source="instagram",
                source_url="https://instagram.com",
                confidence=0.8,
            ),
        ]

        result = self.deduplicator.deduplicate(evidence_list)

        assert len(result.unique_evidence) == 1
        assert result.duplicates_removed == 1
        # Should keep higher confidence
        assert result.unique_evidence[0].confidence == 0.9

    def test_deduplicate_different_claims(self):
        """Test deduplication with different claims"""
        evidence_list = [
            CollectedEvidence(
                entity_id="entity_1",
                claim="business_name",
                value="Test",
                source="google",
                source_url="https://google.com",
                confidence=0.9,
            ),
            CollectedEvidence(
                entity_id="entity_1",
                claim="phone",
                value="Test",
                source="google",
                source_url="https://google.com",
                confidence=0.8,
            ),
        ]

        result = self.deduplicator.deduplicate(evidence_list)

        assert len(result.unique_evidence) == 2
