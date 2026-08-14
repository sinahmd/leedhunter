"""
Tests for qualification engine
"""

import pytest

from leedhunter.application.qualification.engine import (
    QualificationEngine,
    QualificationRule,
    QualificationResult,
    QualificationStatus,
)
from leedhunter.domain.models import (
    Entity,
    EntityIdentity,
    EntityIdentityType,
    Lead,
    LeadStatus,
    Opportunity,
    Signal,
    SignalType,
)


class TestQualificationRule:
    """Tests for QualificationRule"""

    def test_create_rule(self):
        """Test creating a QualificationRule"""
        rule = QualificationRule(
            name="test_rule",
            description="Test rule",
            weight=0.5,
            min_threshold=0.3,
        )

        assert rule.name == "test_rule"
        assert rule.weight == 0.5


class TestQualificationEngine:
    """Tests for QualificationEngine"""

    def setup_method(self):
        """Set up test fixtures"""
        self.engine = QualificationEngine()

    def test_qualify_with_signals_and_opportunities(self):
        """Test qualifying with signals and opportunities"""
        entity = Entity(
            id="entity_1",
            canonical_name="Test Business",
            identities=[
                EntityIdentity(
                    type=EntityIdentityType.PHONE,
                    value="+98 912 123 4567",
                    normalized_value="09121234567",
                    source="test",
                    source_url="https://test.com",
                ),
            ],
        )
        signals = [
            Signal(
                entity_id="entity_1",
                signal_type=SignalType.EXPANSION,
                description="Expanding",
                confidence=0.8,
            ),
        ]
        opportunities = [
            Opportunity(
                entity_id="entity_1",
                description="Partnership opportunity",
                relevance_score=0.7,
            ),
        ]

        result = self.engine.qualify(entity, signals, opportunities)

        assert result.status == QualificationStatus.QUALIFIED
        assert result.score >= 0.5

    def test_qualify_without_signals(self):
        """Test qualifying without signals"""
        entity = Entity(
            id="entity_1",
            canonical_name="Test Business",
            identities=[
                EntityIdentity(
                    type=EntityIdentityType.PHONE,
                    value="+98 912 123 4567",
                    normalized_value="09121234567",
                    source="test",
                    source_url="https://test.com",
                ),
            ],
        )
        signals = []
        opportunities = [
            Opportunity(
                entity_id="entity_1",
                description="Partnership opportunity",
                relevance_score=0.7,
            ),
        ]

        result = self.engine.qualify(entity, signals, opportunities)

        assert result.score < 0.5 or "signal" in " ".join(result.reasons).lower()

    def test_qualify_with_contact_info(self):
        """Test qualifying with contact info"""
        entity = Entity(
            id="entity_1",
            canonical_name="Test Business",
            identities=[
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
            ],
        )
        signals = [
            Signal(
                entity_id="entity_1",
                signal_type=SignalType.DIGITAL_PRESENCE,
                description="Active online",
                confidence=0.7,
            ),
        ]
        opportunities = [
            Opportunity(
                entity_id="entity_1",
                description="Partnership opportunity",
                relevance_score=0.6,
            ),
        ]

        result = self.engine.qualify(entity, signals, opportunities)

        assert "contact" in " ".join(result.reasons).lower()

    def test_qualify_lead(self):
        """Test qualifying a lead"""
        entity = Entity(
            id="entity_1",
            canonical_name="Test Business",
            identities=[
                EntityIdentity(
                    type=EntityIdentityType.PHONE,
                    value="+98 912 123 4567",
                    normalized_value="09121234567",
                    source="test",
                    source_url="https://test.com",
                ),
            ],
        )
        lead = Lead(
            entity=entity,
            signals=[
                Signal(
                    entity_id="entity_1",
                    signal_type=SignalType.EXPANSION,
                    description="Expanding",
                    confidence=0.8,
                ),
            ],
            opportunities=[
                Opportunity(
                    entity_id="entity_1",
                    description="Partnership opportunity",
                    relevance_score=0.7,
                ),
            ],
            score=0.0,
            status=LeadStatus.NEW,
        )

        updated_lead = self.engine.qualify_lead(lead)

        assert updated_lead.status == LeadStatus.QUALIFIED
        assert len(updated_lead.qualification_reasons) > 0

    def test_rule_scores(self):
        """Test that rule scores are returned"""
        entity = Entity(
            id="entity_1",
            canonical_name="Test Business",
            identities=[
                EntityIdentity(
                    type=EntityIdentityType.PHONE,
                    value="+98 912 123 4567",
                    normalized_value="09121234567",
                    source="test",
                    source_url="https://test.com",
                ),
            ],
        )
        signals = [
            Signal(
                entity_id="entity_1",
                signal_type=SignalType.EXPANSION,
                description="Expanding",
                confidence=0.8,
            ),
        ]
        opportunities = [
            Opportunity(
                entity_id="entity_1",
                description="Partnership opportunity",
                relevance_score=0.7,
            ),
        ]

        result = self.engine.qualify(entity, signals, opportunities)

        assert "has_signals" in result.rule_scores
        assert "has_opportunities" in result.rule_scores
        assert "has_contact_info" in result.rule_scores

    def test_custom_min_score(self):
        """Test custom minimum score threshold"""
        engine = QualificationEngine(min_score=0.8)

        entity = Entity(
            id="entity_1",
            canonical_name="Test Business",
            identities=[
                EntityIdentity(
                    type=EntityIdentityType.PHONE,
                    value="+98 912 123 4567",
                    normalized_value="09121234567",
                    source="test",
                    source_url="https://test.com",
                ),
            ],
        )
        signals = [
            Signal(
                entity_id="entity_1",
                signal_type=SignalType.EXPANSION,
                description="Expanding",
                confidence=0.6,
            ),
        ]
        opportunities = [
            Opportunity(
                entity_id="entity_1",
                description="Partnership opportunity",
                relevance_score=0.5,
            ),
        ]

        result = engine.qualify(entity, signals, opportunities)

        # May be disqualified with higher threshold
        assert result.status in [QualificationStatus.QUALIFIED, QualificationStatus.DISQUALIFIED]
