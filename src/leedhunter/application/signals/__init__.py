"""
Signals module

This module identifies business signals from evidence.

Signal types:
- EXPANSION: Business expanding (new locations, branches)
- DIGITAL_PRESENCE: Active digital presence
- ENGAGEMENT: High customer engagement
- ACTIVITY: Recent business activity
- CONTACTABILITY: Easy to contact
"""

from leedhunter.application.signals.detector import (
    SignalDetector,
    SignalRule,
)

__all__ = [
    "SignalDetector",
    "SignalRule",
]
