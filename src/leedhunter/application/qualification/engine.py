"""
Qualification Engine

This module qualifies leads based on signals, opportunities, and other factors.

A lead is qualified if:
1. It has sufficient signals
2. It has at least one opportunity
3. It has contact information
4. It meets minimum score threshold
"""

from dataclasses import dataclass, field
from enum import Enum

from leedhunter.domain.models import (
    Entity,
    EntityIdentityType,
    Lead,
    LeadStatus,
    Opportunity,
    Signal,
)


class QualificationStatus(str, Enum):
    """Status of qualification"""

    QUALIFIED = "qualified"
    DISQUALIFIED = "disqualified"
    PENDING = "pending"


@dataclass
class QualificationRule:
    """A rule for qualifying leads"""

    name: str
    description: str
    weight: float = 1.0
    min_threshold: float = 0.5


@dataclass
class QualificationResult:
    """Result of lead qualification"""

    status: QualificationStatus
    score: float
    reasons: list[str] = field(default_factory=list)
    rule_scores: dict[str, float] = field(default_factory=dict)


class QualificationEngine:
    """
    Qualifies leads based on multiple factors.

    Factors:
    - Signal count and confidence
    - Opportunity count and relevance
    - Contact information availability
    - Entity completeness
    """

    # Default qualification rules
    DEFAULT_RULES = [
        QualificationRule(
            name="has_signals",
            description="Has at least one signal",
            weight=0.3,
            min_threshold=0.0,
        ),
        QualificationRule(
            name="has_opportunities",
            description="Has at least one opportunity",
            weight=0.3,
            min_threshold=0.0,
        ),
        QualificationRule(
            name="has_contact_info",
            description="Has contact information (phone or email)",
            weight=0.2,
            min_threshold=0.0,
        ),
        QualificationRule(
            name="signal_confidence",
            description="Average signal confidence",
            weight=0.1,
            min_threshold=0.3,
        ),
        QualificationRule(
            name="opportunity_relevance",
            description="Average opportunity relevance",
            weight=0.1,
            min_threshold=0.3,
        ),
    ]

    def __init__(
        self,
        rules: list[QualificationRule] | None = None,
        min_score: float = 0.5,
    ):
        self._rules = rules or self.DEFAULT_RULES
        self._min_score = min_score

    def qualify(
        self,
        entity: Entity,
        signals: list[Signal],
        opportunities: list[Opportunity],
    ) -> QualificationResult:
        """
        Qualify a lead

        Args:
            entity: Entity to qualify
            signals: Entity's signals
            opportunities: Entity's opportunities

        Returns:
            QualificationResult with status and score
        """
        rule_scores = {}
        reasons = []

        # Evaluate each rule
        for rule in self._rules:
            score = self._evaluate_rule(rule, entity, signals, opportunities)
            rule_scores[rule.name] = score

            if score >= rule.min_threshold:
                reasons.append(f"✓ {rule.description}")
            else:
                reasons.append(f"✗ {rule.description}")

        # Calculate weighted total score
        total_score = 0.0
        total_weight = 0.0
        for rule in self._rules:
            total_score += rule_scores[rule.name] * rule.weight
            total_weight += rule.weight

        final_score = total_score / total_weight if total_weight > 0 else 0.0

        # Determine status
        if final_score >= self._min_score:
            status = QualificationStatus.QUALIFIED
        else:
            status = QualificationStatus.DISQUALIFIED

        return QualificationResult(
            status=status,
            score=final_score,
            reasons=reasons,
            rule_scores=rule_scores,
        )

    def qualify_lead(
        self,
        lead: Lead,
    ) -> Lead:
        """
        Qualify a lead and update its status

        Args:
            lead: Lead to qualify

        Returns:
            Updated lead with qualification status
        """
        result = self.qualify(
            entity=lead.entity,
            signals=lead.signals,
            opportunities=lead.opportunities,
        )

        lead.status = (
            LeadStatus.QUALIFIED
            if result.status == QualificationStatus.QUALIFIED
            else LeadStatus.DISQUALIFIED
        )
        lead.qualification_reasons = result.reasons

        return lead

    def _evaluate_rule(
        self,
        rule: QualificationRule,
        entity: Entity,
        signals: list[Signal],
        opportunities: list[Opportunity],
    ) -> float:
        """Evaluate a single rule"""
        if rule.name == "has_signals":
            return 1.0 if len(signals) > 0 else 0.0
        elif rule.name == "has_opportunities":
            return 1.0 if len(opportunities) > 0 else 0.0
        elif rule.name == "has_contact_info":
            has_phone = any(i.type == EntityIdentityType.PHONE for i in entity.identities)
            has_email = any(i.type == EntityIdentityType.EMAIL for i in entity.identities)
            if has_phone and has_email:
                return 1.0
            elif has_phone or has_email:
                return 0.5
            return 0.0
        elif rule.name == "signal_confidence":
            if not signals:
                return 0.0
            avg_confidence = sum(s.confidence for s in signals) / len(signals)
            return avg_confidence
        elif rule.name == "opportunity_relevance":
            if not opportunities:
                return 0.0
            avg_relevance = sum(o.relevance_score for o in opportunities) / len(opportunities)
            return avg_relevance
        return 0.0
