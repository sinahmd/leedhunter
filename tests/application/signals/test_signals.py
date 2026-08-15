"""
Tests for signal detection
"""

from leedhunter.application.signals.detector import (
    SignalDetector,
    SignalRule,
)
from leedhunter.domain.models import (
    EntityIdentity,
    EntityIdentityType,
    Evidence,
    Signal,
    SignalType,
)


class TestSignalRule:
    """Tests for SignalRule"""

    def test_create_rule(self):
        """Test creating a SignalRule"""
        rule = SignalRule(
            signal_type=SignalType.EXPANSION,
            description="Expanding",
            keywords=["branch", "new"],
            min_confidence=0.5,
        )

        assert rule.signal_type == SignalType.EXPANSION
        assert "branch" in rule.keywords


class TestSignalDetector:
    """Tests for SignalDetector"""

    def setup_method(self):
        """Set up test fixtures"""
        self.detector = SignalDetector()

    def test_detect_expansion_signal(self):
        """Test detecting expansion signal"""
        evidence = Evidence(
            entity_id="entity_1",
            claim="Opening new branch",
            value="Opening new branch in Sari",
            source="instagram",
            source_url="https://instagram.com/test",
            confidence=0.9,
        )

        signals = self.detector.detect_from_evidence("entity_1", evidence)

        assert len(signals) > 0
        expansion_signals = [s for s in signals if s.signal_type == SignalType.EXPANSION]
        assert len(expansion_signals) > 0

    def test_detect_digital_presence_signal(self):
        """Test detecting digital presence signal"""
        evidence = Evidence(
            entity_id="entity_1",
            claim="Website",
            value="New website launched",
            source="google",
            source_url="https://example.com",
            confidence=0.8,
        )

        signals = self.detector.detect_from_evidence("entity_1", evidence)

        digital_signals = [s for s in signals if s.signal_type == SignalType.DIGITAL_PRESENCE]
        assert len(digital_signals) > 0

    def test_detect_activity_signal(self):
        """Test detecting activity signal"""
        evidence = Evidence(
            entity_id="entity_1",
            claim="New products",
            value="Latest new products added",
            source="website",
            source_url="https://example.com",
            confidence=0.7,
        )

        signals = self.detector.detect_from_evidence("entity_1", evidence)

        activity_signals = [s for s in signals if s.signal_type == SignalType.ACTIVITY]
        assert len(activity_signals) > 0

    def test_detect_contactability_signal(self):
        """Test detecting contactability signal"""
        evidence = Evidence(
            entity_id="entity_1",
            claim="Contact info",
            value="Phone and email available for contact",
            source="website",
            source_url="https://example.com",
            confidence=0.8,
        )

        signals = self.detector.detect_from_evidence("entity_1", evidence)

        contact_signals = [s for s in signals if s.signal_type == SignalType.CONTACTABILITY]
        assert len(contact_signals) > 0

    def test_detect_from_identities_digital_presence(self):
        """Test detecting digital presence from identities"""
        identities = [
            EntityIdentity(
                type=EntityIdentityType.WEBSITE,
                value="example.com",
                normalized_value="example.com",
                source="test",
                source_url="https://example.com",
            ),
            EntityIdentity(
                type=EntityIdentityType.INSTAGRAM,
                value="test",
                normalized_value="test",
                source="test",
                source_url="https://instagram.com/test",
            ),
        ]

        signals = self.detector.detect_from_identities("entity_1", identities)

        digital_signals = [s for s in signals if s.signal_type == SignalType.DIGITAL_PRESENCE]
        assert len(digital_signals) > 0
        assert "Instagram" in digital_signals[0].description

    def test_detect_from_identities_contactability(self):
        """Test detecting contactability from identities"""
        identities = [
            EntityIdentity(
                type=EntityIdentityType.PHONE,
                value="+98 912 123 4567",
                normalized_value="09121234567",
                source="test",
                source_url="https://test.com",
            ),
            EntityIdentity(
                type=EntityIdentityType.EMAIL,
                value="test@example.com",
                normalized_value="test@example.com",
                source="test",
                source_url="https://test.com",
            ),
        ]

        signals = self.detector.detect_from_identities("entity_1", identities)

        contact_signals = [s for s in signals if s.signal_type == SignalType.CONTACTABILITY]
        assert len(contact_signals) > 0
        assert "phone" in contact_signals[0].description.lower()
        assert "email" in contact_signals[0].description.lower()

    def test_detect_batch(self):
        """Test detecting signals from batch"""
        evidence_list = [
            Evidence(
                entity_id="entity_1",
                claim="Expansion",
                value="Opening new branch",
                source="instagram",
                source_url="https://instagram.com/test",
                confidence=0.9,
            ),
            Evidence(
                entity_id="entity_1",
                claim="Website",
                value="New website",
                source="google",
                source_url="https://example.com",
                confidence=0.8,
            ),
        ]

        signals = self.detector.detect_batch("entity_1", evidence_list)

        assert len(signals) > 0

    def test_detect_persian_keywords(self):
        """Test detecting signals with Persian keywords"""
        evidence = Evidence(
            entity_id="entity_1",
            claim="شعبه جدید",
            value="Opening new branch in Sari",
            source="instagram",
            source_url="https://instagram.com/test",
            confidence=0.9,
        )

        signals = self.detector.detect_from_evidence("entity_1", evidence)

        expansion_signals = [s for s in signals if s.signal_type == SignalType.EXPANSION]
        assert len(expansion_signals) > 0

    def test_deduplicate_signals(self):
        """Test signal deduplication"""
        signals = [
            Signal(
                entity_id="entity_1",
                signal_type=SignalType.EXPANSION,
                description="Expanding",
                confidence=0.7,
            ),
            Signal(
                entity_id="entity_1",
                signal_type=SignalType.EXPANSION,
                description="Expanding more",
                confidence=0.9,
            ),
        ]

        deduplicated = self.detector._deduplicate_signals(signals)

        assert len(deduplicated) == 1
        assert deduplicated[0].confidence == 0.9
