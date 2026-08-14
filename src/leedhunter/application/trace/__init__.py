"""
Research Trace module

This module provides observability for research jobs.
Every research job should produce traceable events.
"""

from leedhunter.application.trace.tracer import (
    ResearchTracer,
    TraceEvent,
    TraceEventType,
    ResearchTrace,
)

__all__ = [
    "ResearchTracer",
    "TraceEvent",
    "TraceEventType",
    "ResearchTrace",
]
