"""
Scoring module

This module implements deterministic lead scoring.

Scoring must be deterministic and explainable.
Do NOT ask an LLM to give a score - calculate from explicit factors.

Factors:
- ICP Fit (0-25)
- Opportunity (0-25)
- Signals (0-25)
- Contactability (0-25)
"""

from leedhunter.application.scoring.engine import (
    ScoringEngine,
    ScoreBreakdown,
)

__all__ = [
    "ScoringEngine",
    "ScoreBreakdown",
]
