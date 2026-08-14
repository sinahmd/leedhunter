"""
Opportunity Engine

This module identifies business opportunities from signals.

Opportunities are derived from signals:
- Signal: EXPANSION → Opportunity: "May need digital infrastructure"
- Signal: DIGITAL_PRESENCE → Opportunity: "Active online - partnership potential"
- Signal: ENGAGEMENT → Opportunity: "Good marketing partnership candidate"

Opportunities reference signal IDs for provenance.
"""

import hashlib
from dataclasses import dataclass, field
from typing import Optional

from leedhunter.domain.models import (
    Opportunity,
    Signal,
    SignalType,
)


def _generate_signal_id(signal: Signal) -> str:
    """Generate a stable ID for a signal"""
    content = f"{signal.entity_id}:{signal.signal_type.value}:{signal.description}"
    return f"sig_{hashlib.md5(content.encode()).hexdigest()[:12]}"


@dataclass
class OpportunityRule:
    """A rule for generating opportunities from signals"""

    signal_type: SignalType
    description_template: str
    relevance_base: float = 0.5
    relevance_boost: float = 0.1


class OpportunityEngine:
    """
    Identifies business opportunities from signals.

    Each opportunity references the signal IDs that support it.
    """

    # Default opportunity rules
    DEFAULT_RULES = [
        OpportunityRule(
            signal_type=SignalType.EXPANSION,
            description_template="Business expanding - may need additional services",
            relevance_base=0.7,
            relevance_boost=0.1,
        ),
        OpportunityRule(
            signal_type=SignalType.DIGITAL_PRESENCE,
            description_template="Active digital presence - partnership potential",
            relevance_base=0.6,
            relevance_boost=0.1,
        ),
        OpportunityRule(
            signal_type=SignalType.ENGAGEMENT,
            description_template="High engagement - good outreach candidate",
            relevance_base=0.6,
            relevance_boost=0.1,
        ),
        OpportunityRule(
            signal_type=SignalType.ACTIVITY,
            description_template="Recent activity - timely outreach opportunity",
            relevance_base=0.5,
            relevance_boost=0.1,
        ),
        OpportunityRule(
            signal_type=SignalType.CONTACTABILITY,
            description_template="Easy to contact - quick outreach possible",
            relevance_base=0.5,
            relevance_boost=0.05,
        ),
    ]

    def __init__(self, rules: Optional[list[OpportunityRule]] = None):
        self._rules = rules or self.DEFAULT_RULES

    def identify(
        self,
        entity_id: str,
        signals: list[Signal],
    ) -> list[Opportunity]:
        """
        Identify opportunities from signals

        Args:
            entity_id: Entity ID
            signals: List of signals

        Returns:
            List of opportunities
        """
        opportunities = []

        for signal in signals:
            rule = self._find_rule(signal.signal_type)
            if rule:
                # Calculate relevance
                relevance = min(1.0, rule.relevance_base + signal.confidence * rule.relevance_boost)

                opportunity = Opportunity(
                    entity_id=entity_id,
                    description=rule.description_template,
                    signal_ids=[_generate_signal_id(signal)],
                    relevance_score=relevance,
                )
                opportunities.append(opportunity)

        # Sort by relevance (highest first)
        opportunities.sort(key=lambda o: o.relevance_score, reverse=True)

        return opportunities

    def identify_batch(
        self,
        entity_id: str,
        signals: list[Signal],
        max_opportunities: int = 5,
    ) -> list[Opportunity]:
        """
        Identify opportunities with limit

        Args:
            entity_id: Entity ID
            signals: List of signals
            max_opportunities: Maximum opportunities to return

        Returns:
            List of top opportunities
        """
        opportunities = self.identify(entity_id, signals)
        return opportunities[:max_opportunities]

    def _find_rule(self, signal_type: SignalType) -> Optional[OpportunityRule]:
        """Find the rule for a signal type"""
        for rule in self._rules:
            if rule.signal_type == signal_type:
                return rule
        return None

    def rank_opportunities(
        self,
        opportunities: list[Opportunity],
    ) -> list[Opportunity]:
        """
        Rank opportunities by relevance

        Args:
            opportunities: List of opportunities

        Returns:
            Sorted list (highest relevance first)
        """
        return sorted(opportunities, key=lambda o: o.relevance_score, reverse=True)

    def explain_opportunity(
        self,
        opportunity: Opportunity,
        signals: list[Signal],
    ) -> dict:
        """
        Generate explanation for an opportunity

        Args:
            opportunity: The opportunity to explain
            signals: List of signals (to find supporting signals)

        Returns:
            Explanation dictionary
        """
        # Find supporting signals
        supporting_signals = [
            s for s in signals
            if _generate_signal_id(s) in opportunity.signal_ids
        ]

        return {
            "description": opportunity.description,
            "relevance_score": opportunity.relevance_score,
            "supporting_signals": [
                {
                    "type": s.signal_type.value,
                    "description": s.description,
                    "confidence": s.confidence,
                }
                for s in supporting_signals
            ],
            "recommendation": self._get_recommendation(opportunity),
        }

    def _get_recommendation(self, opportunity: Opportunity) -> str:
        """Get recommendation based on relevance"""
        if opportunity.relevance_score >= 0.8:
            return "High priority - immediate outreach recommended"
        elif opportunity.relevance_score >= 0.6:
            return "Medium priority - include in outreach campaign"
        else:
            return "Low priority - monitor for changes"
