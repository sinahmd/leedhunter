"""
Scoring Engine

This module implements deterministic lead scoring.

Scoring must be deterministic and explainable.
Do NOT ask an LLM to give a score - calculate from explicit factors.

Factors (0-25 each, total 0-100):
- ICP Fit: Industry, location, business type match
- Opportunity: Number and relevance of opportunities
- Signals: Number and confidence of signals
- Contactability: Availability of contact information
"""

from dataclasses import dataclass, field

from leedhunter.domain.models import (
    Entity,
    EntityIdentityType,
    Opportunity,
    Signal,
    SignalType,
)


@dataclass
class ScoreBreakdown:
    """Breakdown of lead score"""

    total_score: float
    icp_fit: float
    opportunity: float
    signals: float
    contactability: float
    factors: dict[str, float] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)


class ScoringEngine:
    """
    Calculates deterministic lead scores.

    Each factor contributes 0-25 points (total 0-100).
    """

    def calculate_score(
        self,
        entity: Entity,
        signals: list[Signal],
        opportunities: list[Opportunity],
    ) -> ScoreBreakdown:
        """
        Calculate lead score

        Args:
            entity: Entity to score
            signals: Entity's signals
            opportunities: Entity's opportunities

        Returns:
            ScoreBreakdown with total and factor scores
        """
        # Calculate each factor (0-25)
        icp_score = self._calculate_icp_fit(entity)
        opportunity_score = self._calculate_opportunity(opportunities)
        signal_score = self._calculate_signals(signals)
        contactability_score = self._calculate_contactability(entity)

        total_score = min(
            100.0, icp_score + opportunity_score + signal_score + contactability_score
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            icp_score, opportunity_score, signal_score, contactability_score
        )

        return ScoreBreakdown(
            total_score=total_score,
            icp_fit=icp_score,
            opportunity=opportunity_score,
            signals=signal_score,
            contactability=contactability_score,
            factors={
                "icp_fit": icp_score,
                "opportunity": opportunity_score,
                "signals": signal_score,
                "contactability": contactability_score,
            },
            recommendations=recommendations,
        )

    def _calculate_icp_fit(self, entity: Entity) -> float:
        """
        Calculate ICP (Ideal Customer Profile) fit score

        Based on:
        - Industry match (from metadata)
        - Location match (from metadata)
        - Business type (website presence)
        """
        score = 0.0
        metadata = entity.metadata

        # Industry match
        if metadata.get("industry"):
            score += 8.0

        # Location match
        if metadata.get("location"):
            score += 8.0

        # Has website
        has_website = any(i.type == EntityIdentityType.WEBSITE for i in entity.identities)
        if has_website:
            score += 5.0

        # Has business name
        if entity.canonical_name:
            score += 4.0

        return min(25.0, score)

    def _calculate_opportunity(self, opportunities: list[Opportunity]) -> float:
        """
        Calculate opportunity score

        Based on:
        - Number of opportunities
        - Average relevance
        """
        if not opportunities:
            return 0.0

        # Average relevance
        avg_relevance = sum(o.relevance_score for o in opportunities) / len(opportunities)

        # Count factor (up to 5 opportunities)
        count_factor = min(1.0, len(opportunities) / 5.0)

        score = avg_relevance * 15.0 + count_factor * 10.0

        return min(25.0, score)

    def _calculate_signals(self, signals: list[Signal]) -> float:
        """
        Calculate signal score

        Based on:
        - Number of signals
        - Average confidence
        - Signal type diversity
        """
        if not signals:
            return 0.0

        # Average confidence
        avg_confidence = sum(s.confidence for s in signals) / len(signals)

        # Unique signal types
        unique_types = len(set(s.signal_type for s in signals))

        # Expansion bonus
        has_expansion = any(s.signal_type == SignalType.EXPANSION for s in signals)

        score = avg_confidence * 10.0
        score += min(10.0, unique_types * 3.0)
        if has_expansion:
            score += 5.0

        return min(25.0, score)

    def _calculate_contactability(self, entity: Entity) -> float:
        """
        Calculate contactability score

        Based on:
        - Has phone
        - Has email
        - Has social media
        """
        score = 0.0

        has_phone = any(i.type == EntityIdentityType.PHONE for i in entity.identities)
        has_email = any(i.type == EntityIdentityType.EMAIL for i in entity.identities)
        has_instagram = any(i.type == EntityIdentityType.INSTAGRAM for i in entity.identities)
        has_linkedin = any(i.type == EntityIdentityType.LINKEDIN for i in entity.identities)

        if has_phone:
            score += 10.0
        if has_email:
            score += 10.0
        if has_instagram:
            score += 3.0
        if has_linkedin:
            score += 2.0

        return min(25.0, score)

    def _generate_recommendations(
        self,
        icp_score: float,
        opportunity_score: float,
        signal_score: float,
        contactability_score: float,
    ) -> list[str]:
        """Generate recommendations based on scores"""
        recommendations = []

        if icp_score < 10:
            recommendations.append("Low ICP fit - verify target market alignment")
        if opportunity_score < 10:
            recommendations.append("Few opportunities identified - investigate further")
        if signal_score < 10:
            recommendations.append("Weak signals - gather more evidence")
        if contactability_score < 10:
            recommendations.append("Poor contactability - find contact information")

        if not recommendations:
            recommendations.append("Strong lead - prioritize outreach")

        return recommendations

    def explain_score(self, breakdown: ScoreBreakdown) -> dict:
        """
        Generate detailed explanation of score

        Args:
            breakdown: Score breakdown

        Returns:
            Explanation dictionary
        """
        return {
            "total_score": round(breakdown.total_score, 1),
            "factors": {
                "icp_fit": {
                    "score": round(breakdown.icp_fit, 1),
                    "max": 25.0,
                    "percentage": round(breakdown.icp_fit / 25.0 * 100, 1),
                },
                "opportunity": {
                    "score": round(breakdown.opportunity, 1),
                    "max": 25.0,
                    "percentage": round(breakdown.opportunity / 25.0 * 100, 1),
                },
                "signals": {
                    "score": round(breakdown.signals, 1),
                    "max": 25.0,
                    "percentage": round(breakdown.signals / 25.0 * 100, 1),
                },
                "contactability": {
                    "score": round(breakdown.contactability, 1),
                    "max": 25.0,
                    "percentage": round(breakdown.contactability / 25.0 * 100, 1),
                },
            },
            "recommendations": breakdown.recommendations,
        }
