"""
Tests for scoring engine
"""

import pytest

from leedhunter.application.scoring.engine import (
    ScoringEngine,
    ScoreBreakdown,
)
from leedhunter.domain.models import (
    Entity,
    EntityIdentity,
    EntityIdentityType,
    Opportunity,
    Signal,
    SignalType,
)


class TestScoreBreakdown:
    """Tests for ScoreBreakdown"""

    def test_create_breakdown(self):
        """Test creating a ScoreBreakdown"""
        breakdown = ScoreBreakdown(
            total_score=75.0,
            icp_fit=20.0,
            opportunity=20.0,
            signals=20.0,
            contactability=15.0,
        )

        assert breakdown.total_score == 75.0
        assert breakdown.icp_fit == 20.0


class TestScoringEngine:
    """Tests for ScoringEngine"""

    def setup_method(self):
        """Set up test fixtures"""
        self.engine = ScoringEngine()

    def test_calculate_score_with_all_factors(self):
        """Test calculating score with all factors"""
        entity = Entity(
            id="entity_1",
            canonical_name="Test Business",
            canonical_domain="example.com",
            identities=[
                EntityIdentity(
                    type=EntityIdentityType.WEBSITE,
                    value="example.com",
                    normalized_value="example.com",
                    source="test",
                    source_url="https://example.com",
                ),
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
            metadata={"industry": "automotive", "location": "mazandaran"},
        )
        signals = [
            Signal(
                entity_id="entity_1",
                signal_type=SignalType.EXPANSION,
                description="Expanding",
                confidence=0.8,
            ),
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
                relevance_score=0.8,
            ),
        ]

        breakdown = self.engine.calculate_score(entity, signals, opportunities)

        assert 0.0 <= breakdown.total_score <= 100.0
        assert breakdown.total_score > 0.0
        assert breakdown.icp_fit > 0.0
        assert breakdown.opportunity > 0.0
        assert breakdown.signals > 0.0
        assert breakdown.contactability > 0.0

    def test_calculate_score_minimal_entity(self):
        """Test calculating score with minimal entity"""
        entity = Entity(
            id="entity_1",
            canonical_name="Test Business",
        )
        signals = []
        opportunities = []

        breakdown = self.engine.calculate_score(entity, signals, opportunities)

        assert 0.0 <= breakdown.total_score <= 100.0
        assert breakdown.total_score < 50.0  # Should be low

    def test_icp_fit_score(self):
        """Test ICP fit calculation"""
        entity = Entity(
            id="entity_1",
            canonical_name="Test Business",
            identities=[
                EntityIdentity(
                    type=EntityIdentityType.WEBSITE,
                    value="example.com",
                    normalized_value="example.com",
                    source="test",
                    source_url="https://example.com",
                ),
            ],
            metadata={"industry": "automotive", "location": "mazandaran"},
        )

        breakdown = self.engine.calculate_score(entity, [], [])

        assert breakdown.icp_fit > 0.0
        assert breakdown.icp_fit <= 25.0

    def test_opportunity_score(self):
        """Test opportunity calculation"""
        entity = Entity(id="entity_1", canonical_name="Test")
        opportunities = [
            Opportunity(
                entity_id="entity_1",
                description="Test opportunity",
                relevance_score=0.8,
            ),
        ]

        breakdown = self.engine.calculate_score(entity, [], opportunities)

        assert breakdown.opportunity > 0.0
        assert breakdown.opportunity <= 25.0

    def test_signal_score(self):
        """Test signal calculation"""
        entity = Entity(id="entity_1", canonical_name="Test")
        signals = [
            Signal(
                entity_id="entity_1",
                signal_type=SignalType.EXPANSION,
                description="Expanding",
                confidence=0.8,
            ),
        ]

        breakdown = self.engine.calculate_score(entity, signals, [])

        assert breakdown.signals > 0.0
        assert breakdown.signals <= 25.0

    def test_contactability_score(self):
        """Test contactability calculation"""
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

        breakdown = self.engine.calculate_score(entity, [], [])

        assert breakdown.contactability > 0.0
        assert breakdown.contactability <= 25.0

    def test_explain_score(self):
        """Test score explanation"""
        entity = Entity(id="entity_1", canonical_name="Test")
        breakdown = self.engine.calculate_score(entity, [], [])

        explanation = self.engine.explain_score(breakdown)

        assert "total_score" in explanation
        assert "factors" in explanation
        assert "recommendations" in explanation
        assert "icp_fit" in explanation["factors"]
        assert "opportunity" in explanation["factors"]
        assert "signals" in explanation["factors"]
        assert "contactability" in explanation["factors"]

    def test_deterministic_scoring(self):
        """Test that scoring is deterministic"""
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
                description="Test",
                relevance_score=0.7,
            ),
        ]

        breakdown1 = self.engine.calculate_score(entity, signals, opportunities)
        breakdown2 = self.engine.calculate_score(entity, signals, opportunities)

        assert breakdown1.total_score == breakdown2.total_score

    def test_persian_entity(self):
        """Test scoring Persian entity"""
        entity = Entity(
            id="entity_1",
            canonical_name="شرکت تست",
            identities=[
                EntityIdentity(
                    type=EntityIdentityType.PHONE,
                    value="+98 912 123 4567",
                    normalized_value="09121234567",
                    source="test",
                    source_url="https://test.com",
                ),
            ],
            metadata={"industry": "automotive", "location": "mazandaran"},
        )
        signals = [
            Signal(
                entity_id="entity_1",
                signal_type=SignalType.EXPANSION,
                description="Expanding",
                confidence=0.8,
            ),
        ]

        breakdown = self.engine.calculate_score(entity, signals, [])

        assert breakdown.total_score > 0.0
