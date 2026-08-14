"""
Research Tracer

This module provides observability for research jobs.

Every research job should produce traceable events:
- INTENT_CREATED
- QUERY_GENERATED
- QUERY_EXECUTED
- RESULT_RECEIVED
- CANDIDATE_CREATED
- CANDIDATE_DEDUPLICATED
- ENTITY_MATCHED
- ENTITY_CREATED
- IDENTITY_ATTACHED
- EVIDENCE_CREATED
- SIGNAL_CREATED
- LEAD_CREATED
- SCORE_CALCULATED
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class TraceEventType(str, Enum):
    """Types of trace events"""

    # Intent events
    INTENT_CREATED = "INTENT_CREATED"

    # Query events
    QUERY_GENERATED = "QUERY_GENERATED"
    QUERY_EXECUTED = "QUERY_EXECUTED"

    # Search events
    RESULT_RECEIVED = "RESULT_RECEIVED"

    # Candidate events
    CANDIDATE_CREATED = "CANDIDATE_CREATED"
    CANDIDATE_DEDUPLICATED = "CANDIDATE_DEDUPLICATED"

    # Entity events
    ENTITY_MATCHED = "ENTITY_MATCHED"
    ENTITY_CREATED = "ENTITY_CREATED"
    IDENTITY_ATTACHED = "IDENTITY_ATTACHED"

    # Evidence events
    EVIDENCE_CREATED = "EVIDENCE_CREATED"

    # Signal events
    SIGNAL_CREATED = "SIGNAL_CREATED"

    # Lead events
    LEAD_CREATED = "LEAD_CREATED"
    SCORE_CALCULATED = "SCORE_CALCULATED"

    # Research job events
    RESEARCH_STARTED = "RESEARCH_STARTED"
    RESEARCH_COMPLETED = "RESEARCH_COMPLETED"
    RESEARCH_FAILED = "RESEARCH_FAILED"

    # Provider events
    PROVIDER_CALLED = "PROVIDER_CALLED"
    PROVIDER_FAILED = "PROVIDER_FAILED"

    # Error events
    ERROR_OCCURRED = "ERROR_OCCURRED"


@dataclass
class TraceEvent:
    """A single trace event"""

    event_type: TraceEventType
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: Optional[str] = None
    research_id: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    duration_ms: Optional[float] = None

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "event_id": self.event_id,
            "research_id": self.research_id,
            "metadata": self.metadata,
            "duration_ms": self.duration_ms,
        }


@dataclass
class ResearchTrace:
    """Complete trace for a research job"""

    research_id: str
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    events: list[TraceEvent] = field(default_factory=list)
    success: bool = True
    error_message: Optional[str] = None

    @property
    def duration_seconds(self) -> Optional[float]:
        """Get duration in seconds"""
        if self.completed_at and self.started_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @property
    def event_count(self) -> int:
        """Get number of events"""
        return len(self.events)

    def get_events_by_type(self, event_type: TraceEventType) -> list[TraceEvent]:
        """Get events by type"""
        return [e for e in self.events if e.event_type == event_type]

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "research_id": self.research_id,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "success": self.success,
            "error_message": self.error_message,
            "event_count": self.event_count,
            "events": [e.to_dict() for e in self.events],
        }


class ResearchTracer:
    """
    Traces research job execution.

    Provides observability and debugging capabilities.
    """

    def __init__(self):
        self._traces: dict[str, ResearchTrace] = {}
        self._current_research_id: Optional[str] = None

    def start_trace(self, research_id: str) -> ResearchTrace:
        """
        Start a new research trace

        Args:
            research_id: Unique research job ID

        Returns:
            New ResearchTrace
        """
        trace = ResearchTrace(research_id=research_id)
        self._traces[research_id] = trace
        self._current_research_id = research_id

        self.record_event(
            TraceEventType.RESEARCH_STARTED,
            research_id=research_id,
        )

        return trace

    def end_trace(
        self,
        research_id: str,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> None:
        """
        End a research trace

        Args:
            research_id: Research job ID
            success: Whether the research succeeded
            error_message: Error message if failed
        """
        trace = self._traces.get(research_id)
        if trace:
            trace.completed_at = datetime.now(timezone.utc)
            trace.success = success
            trace.error_message = error_message

            event_type = TraceEventType.RESEARCH_COMPLETED if success else TraceEventType.RESEARCH_FAILED
            self.record_event(
                event_type,
                research_id=research_id,
                metadata={"error_message": error_message} if error_message else {},
            )

        if self._current_research_id == research_id:
            self._current_research_id = None

    def record_event(
        self,
        event_type: TraceEventType,
        research_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        duration_ms: Optional[float] = None,
    ) -> TraceEvent:
        """
        Record a trace event

        Args:
            event_type: Type of event
            research_id: Research job ID (uses current if not specified)
            metadata: Event metadata
            duration_ms: Duration in milliseconds

        Returns:
            Created TraceEvent
        """
        rid = research_id or self._current_research_id

        event = TraceEvent(
            event_type=event_type,
            research_id=rid,
            metadata=metadata or {},
            duration_ms=duration_ms,
        )

        if rid and rid in self._traces:
            self._traces[rid].events.append(event)

        return event

    def get_trace(self, research_id: str) -> Optional[ResearchTrace]:
        """Get trace for a research job"""
        return self._traces.get(research_id)

    def get_all_traces(self) -> list[ResearchTrace]:
        """Get all traces"""
        return list(self._traces.values())

    def generate_report(self, research_id: str) -> Optional[dict]:
        """
        Generate a report for a research job

        Args:
            research_id: Research job ID

        Returns:
            Report dictionary
        """
        trace = self._traces.get(research_id)
        if not trace:
            return None

        # Count events by type
        event_counts: dict[str, int] = {}
        for event in trace.events:
            event_type = event.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

        return {
            "research_id": trace.research_id,
            "duration_seconds": trace.duration_seconds,
            "success": trace.success,
            "error_message": trace.error_message,
            "total_events": trace.event_count,
            "event_counts": event_counts,
            "events": [e.to_dict() for e in trace.events],
        }

    def reset(self) -> None:
        """Reset all traces"""
        self._traces.clear()
        self._current_research_id = None
