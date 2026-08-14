"""
Opportunity Engine module

This module identifies business opportunities from signals.

Opportunities represent potential business value:
- Expansion → May need digital infrastructure
- Digital Presence → May need marketing services
- High Engagement → Good partnership candidate
- Recent Activity → Timely outreach opportunity
"""

from leedhunter.application.opportunities.engine import (
    OpportunityEngine,
    OpportunityRule,
)

__all__ = [
    "OpportunityEngine",
    "OpportunityRule",
]
