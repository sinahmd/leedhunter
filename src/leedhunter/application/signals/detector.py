"""
Signal Detector

This module identifies business signals from evidence.

Signal types:
- EXPANSION: Business expanding (new locations, branches)
- DIGITAL_PRESENCE: Active digital presence
- ENGAGEMENT: High customer engagement
- ACTIVITY: Recent business activity
- CONTACTABILITY: Easy to contact

Signals must reference evidence IDs.
"""

import hashlib
from dataclasses import dataclass, field
from typing import Optional

from leedhunter.domain.models import (
    Evidence,
    EntityIdentity,
    EntityIdentityType,
    Signal,
    SignalType,
)


def _generate_evidence_id(evidence: Evidence) -> str:
    """Generate a stable ID for evidence based on its content"""
    content = f"{evidence.entity_id}:{evidence.claim}:{evidence.value}:{evidence.source}"
    return f"ev_{hashlib.md5(content.encode()).hexdigest()[:12]}"


@dataclass
class SignalRule:
    """A rule for detecting signals"""

    signal_type: SignalType
    description: str
    keywords: list[str] = field(default_factory=list)
    min_confidence: float = 0.5


class SignalDetector:
    """
    Detects business signals from evidence and identities.

    Signals are inferred from evidence, not stored as facts.
    """

    # Default signal rules
    DEFAULT_RULES = [
        SignalRule(
            signal_type=SignalType.EXPANSION,
            description="Business expanding to new locations",
            keywords=["branch", "new location", "expanding", "opening", "شعبه", "گسترش"],
            min_confidence=0.7,
        ),
        SignalRule(
            signal_type=SignalType.DIGITAL_PRESENCE,
            description="Active digital presence",
            keywords=["website", "instagram", "linkedin", "online"],
            min_confidence=0.6,
        ),
        SignalRule(
            signal_type=SignalType.ENGAGEMENT,
            description="High customer engagement",
            keywords=["followers", "reviews", "customers", "engagement"],
            min_confidence=0.5,
        ),
        SignalRule(
            signal_type=SignalType.ACTIVITY,
            description="Recent business activity",
            keywords=["new", "recent", "latest", "جدید"],
            min_confidence=0.5,
        ),
        SignalRule(
            signal_type=SignalType.CONTACTABILITY,
            description="Easy to contact",
            keywords=["phone", "email", "contact", "تماس"],
            min_confidence=0.6,
        ),
    ]

    def __init__(self, rules: Optional[list[SignalRule]] = None):
        self._rules = rules or self.DEFAULT_RULES

    def detect_from_evidence(
        self,
        entity_id: str,
        evidence: Evidence,
    ) -> list[Signal]:
        """
        Detect signals from a single evidence item

        Args:
            entity_id: Entity ID
            evidence: Evidence to analyze

        Returns:
            List of detected signals
        """
        signals = []
        text = f"{evidence.claim} {evidence.value}".lower()

        for rule in self._rules:
            # Check if any keywords match
            matched_keywords = [
                kw for kw in rule.keywords
                if kw.lower() in text
            ]

            if matched_keywords:
                # Calculate confidence: base evidence confidence + keyword boost
                keyword_boost = min(0.3, len(matched_keywords) * 0.1)
                signal_confidence = min(1.0, evidence.confidence + keyword_boost)

                if signal_confidence >= rule.min_confidence:
                    signal = Signal(
                        entity_id=entity_id,
                        signal_type=rule.signal_type,
                        description=rule.description,
                        evidence_ids=[_generate_evidence_id(evidence)],
                        confidence=signal_confidence,
                    )
                    signals.append(signal)

        return signals

    def detect_from_identities(
        self,
        entity_id: str,
        identities: list[EntityIdentity],
    ) -> list[Signal]:
        """
        Detect signals from entity identities

        Args:
            entity_id: Entity ID
            identities: List of identities

        Returns:
            List of detected signals
        """
        signals = []

        # Check for digital presence signals
        has_website = any(i.type == EntityIdentityType.WEBSITE for i in identities)
        has_instagram = any(i.type == EntityIdentityType.INSTAGRAM for i in identities)
        has_linkedin = any(i.type == EntityIdentityType.LINKEDIN for i in identities)

        if has_website or has_instagram or has_linkedin:
            platforms = []
            if has_website:
                platforms.append("website")
            if has_instagram:
                platforms.append("Instagram")
            if has_linkedin:
                platforms.append("LinkedIn")

            signal = Signal(
                entity_id=entity_id,
                signal_type=SignalType.DIGITAL_PRESENCE,
                description=f"Active on {', '.join(platforms)}",
                evidence_ids=[],
                confidence=0.7 if len(platforms) >= 2 else 0.5,
            )
            signals.append(signal)

        # Check for contactability signals
        has_phone = any(i.type == EntityIdentityType.PHONE for i in identities)
        has_email = any(i.type == EntityIdentityType.EMAIL for i in identities)

        if has_phone and has_email:
            signal = Signal(
                entity_id=entity_id,
                signal_type=SignalType.CONTACTABILITY,
                description="Has phone and email - easy to contact",
                evidence_ids=[],
                confidence=0.8,
            )
            signals.append(signal)
        elif has_phone or has_email:
            contact_type = "phone" if has_phone else "email"
            signal = Signal(
                entity_id=entity_id,
                signal_type=SignalType.CONTACTABILITY,
                description=f"Has {contact_type}",
                evidence_ids=[],
                confidence=0.6,
            )
            signals.append(signal)

        return signals

    def detect_batch(
        self,
        entity_id: str,
        evidence_list: list[Evidence],
        identities: Optional[list[EntityIdentity]] = None,
    ) -> list[Signal]:
        """
        Detect signals from multiple evidence items and identities

        Args:
            entity_id: Entity ID
            evidence_list: List of evidence
            identities: Optional list of identities

        Returns:
            List of detected signals (deduplicated)
        """
        all_signals = []

        # Detect from evidence
        for evidence in evidence_list:
            signals = self.detect_from_evidence(entity_id, evidence)
            all_signals.extend(signals)

        # Detect from identities
        if identities:
            signals = self.detect_from_identities(entity_id, identities)
            all_signals.extend(signals)

        # Deduplicate by signal type, keeping highest confidence
        return self._deduplicate_signals(all_signals)

    def _deduplicate_signals(self, signals: list[Signal]) -> list[Signal]:
        """Deduplicate signals by type, keeping highest confidence"""
        by_type: dict[SignalType, Signal] = {}

        for signal in signals:
            if signal.signal_type not in by_type:
                by_type[signal.signal_type] = signal
            elif signal.confidence > by_type[signal.signal_type].confidence:
                by_type[signal.signal_type] = signal

        return list(by_type.values())
