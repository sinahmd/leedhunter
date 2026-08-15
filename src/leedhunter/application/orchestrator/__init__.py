"""
Research Orchestrator module

This module connects all components into a complete research pipeline:
Search → Pipeline → Resolution → Evidence → Signals → Opportunities → Qualification → Scoring → Leads
"""

from leedhunter.application.orchestrator.research import (
    ResearchConfig,
    ResearchOrchestrator,
    ResearchResult,
)

__all__ = [
    "ResearchOrchestrator",
    "ResearchResult",
    "ResearchConfig",
]
