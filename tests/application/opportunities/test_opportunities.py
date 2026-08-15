"""
Tests for opportunity engine
"""

from leedhunter.application.opportunities.engine import (
    OpportunityEngine,
    OpportunityRule,
)
from leedhunter.domain.models import (
    Opportunity,
    Signal,
    SignalType,
)


class TestOpportunityRule:
    """Tests for OpportunityRule"""

    def test_create_rule(self):
        """Test creating an OpportunityRule"""
        rule = OpportunityRule(
            signal_type=SignalType.EXPANSION,
            description_template="Expanding business",
            relevance_base=0.7,
        )

        assert rule.signal_type == SignalType.EXPANSION
        assert rule.relevance_base == 0.7


class TestOpportunityEngine:
    """Tests for OpportunityEngine"""

    def setup_method(self):
        """Set up test fixtures"""
        self.engine = OpportunityEngine()

    def test_identify_from_expansion_signal(self):
        """Test identifying opportunity from expansion signal"""
        signal = Signal(
            entity_id="entity_1",
            signal_type=SignalType.EXPANSION,
            description="Expanding to new locations",
            confidence=0.8,
        )

        opportunities = self.engine.identify("entity_1", [signal])

        assert len(opportunities) == 1
        assert "expanding" in opportunities[0].description.lower()
        assert opportunities[0].relevance_score > 0.5

    def test_identify_from_digital_presence_signal(self):
        """Test identifying opportunity from digital presence signal"""
        signal = Signal(
            entity_id="entity_1",
            signal_type=SignalType.DIGITAL_PRESENCE,
            description="Active on Instagram and LinkedIn",
            confidence=0.7,
        )

        opportunities = self.engine.identify("entity_1", [signal])

        assert len(opportunities) == 1
        assert (
            "digital" in opportunities[0].description.lower()
            or "partnership" in opportunities[0].description.lower()
        )

    def test_identify_from_multiple_signals(self):
        """Test identifying opportunities from multiple signals"""
        signals = [
            Signal(
                entity_id="entity_1",
                signal_type=SignalType.EXPANSION,
                description="Expanding",
                confidence=0.8,
            ),
            Signal(
                entity_id="entity_1",
                signal_type=SignalType.CONTACTABILITY,
                description="Easy to contact",
                confidence=0.7,
            ),
        ]

        opportunities = self.engine.identify("entity_1", signals)

        assert len(opportunities) == 2

    def test_identify_batch_limit(self):
        """Test identifying with batch limit"""
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
                description="Online",
                confidence=0.7,
            ),
            Signal(
                entity_id="entity_1",
                signal_type=SignalType.ENGAGEMENT,
                description="Engaged",
                confidence=0.6,
            ),
        ]

        opportunities = self.engine.identify_batch("entity_1", signals, max_opportunities=2)

        assert len(opportunities) <= 2

    def test_rank_opportunities(self):
        """Test ranking opportunities"""
        opportunities = [
            Opportunity(
                entity_id="entity_1",
                description="Low relevance",
                relevance_score=0.3,
            ),
            Opportunity(
                entity_id="entity_1",
                description="High relevance",
                relevance_score=0.9,
            ),
        ]

        ranked = self.engine.rank_opportunities(opportunities)

        assert ranked[0].relevance_score >= ranked[1].relevance_score

    def test_explain_opportunity(self):
        """Test explaining an opportunity"""
        signal = Signal(
            entity_id="entity_1",
            signal_type=SignalType.EXPANSION,
            description="Expanding to new locations",
            confidence=0.8,
        )
        opportunity = Opportunity(
            entity_id="entity_1",
            description="Expanding business",
            signal_ids=[f"sig_{hash(signal.entity_id + signal.signal_type.value + signal.description)}"],
            relevance_score=0.8,
        )

        explanation = self.engine.explain_opportunity(opportunity, [signal])

        assert "description" in explanation
        assert "relevance_score" in explanation
        assert "supporting_signals" in explanation
        assert "recommendation" in explanation

    def test_relevance_scoring(self):
        """Test relevance scoring calculation"""
        signal = Signal(
            entity_id="entity_1",
            signal_type=SignalType.EXPANSION,
            description="Expanding",
            confidence=0.9,
        )

        opportunities = self.engine.identify("entity_1", [signal])

        assert len(opportunities) == 1
        assert 0.0 <= opportunities[0].relevance_score <= 1.0

    def test_no_signals_no_opportunities(self):
        """Test that no signals means no opportunities"""
        opportunities = self.engine.identify("entity_1", [])

        assert len(opportunities) == 0
