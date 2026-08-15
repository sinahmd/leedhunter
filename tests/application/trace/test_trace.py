"""
Tests for research trace
"""

from leedhunter.application.trace.tracer import (
    ResearchTrace,
    ResearchTracer,
    TraceEvent,
    TraceEventType,
)


class TestTraceEventType:
    """Tests for TraceEventType"""

    def test_event_types(self):
        """Test event type values"""
        assert TraceEventType.INTENT_CREATED == "INTENT_CREATED"
        assert TraceEventType.QUERY_GENERATED == "QUERY_GENERATED"
        assert TraceEventType.RESEARCH_STARTED == "RESEARCH_STARTED"
        assert TraceEventType.RESEARCH_COMPLETED == "RESEARCH_COMPLETED"


class TestTraceEvent:
    """Tests for TraceEvent"""

    def test_create_event(self):
        """Test creating a TraceEvent"""
        event = TraceEvent(
            event_type=TraceEventType.INTENT_CREATED,
            research_id="research_1",
        )

        assert event.event_type == TraceEventType.INTENT_CREATED
        assert event.research_id == "research_1"

    def test_to_dict(self):
        """Test converting to dictionary"""
        event = TraceEvent(
            event_type=TraceEventType.QUERY_GENERATED,
            research_id="research_1",
            metadata={"query": "test"},
        )

        data = event.to_dict()

        assert data["event_type"] == "QUERY_GENERATED"
        assert data["research_id"] == "research_1"
        assert "timestamp" in data


class TestResearchTrace:
    """Tests for ResearchTrace"""

    def test_create_trace(self):
        """Test creating a ResearchTrace"""
        trace = ResearchTrace(research_id="research_1")

        assert trace.research_id == "research_1"
        assert trace.success is True
        assert trace.event_count == 0

    def test_duration_seconds(self):
        """Test duration calculation"""
        trace = ResearchTrace(research_id="research_1")
        trace.completed_at = trace.started_at

        assert trace.duration_seconds == 0.0

    def test_get_events_by_type(self):
        """Test getting events by type"""
        trace = ResearchTrace(research_id="research_1")
        trace.events = [
            TraceEvent(event_type=TraceEventType.INTENT_CREATED),
            TraceEvent(event_type=TraceEventType.QUERY_GENERATED),
            TraceEvent(event_type=TraceEventType.INTENT_CREATED),
        ]

        intent_events = trace.get_events_by_type(TraceEventType.INTENT_CREATED)
        assert len(intent_events) == 2

    def test_to_dict(self):
        """Test converting to dictionary"""
        trace = ResearchTrace(research_id="research_1")
        trace.events = [
            TraceEvent(event_type=TraceEventType.INTENT_CREATED),
        ]

        data = trace.to_dict()

        assert data["research_id"] == "research_1"
        assert data["event_count"] == 1
        assert "events" in data


class TestResearchTracer:
    """Tests for ResearchTracer"""

    def setup_method(self):
        """Set up test fixtures"""
        self.tracer = ResearchTracer()

    def test_start_trace(self):
        """Test starting a trace"""
        trace = self.tracer.start_trace("research_1")

        assert trace.research_id == "research_1"
        assert self.tracer.get_trace("research_1") is not None

    def test_end_trace_success(self):
        """Test ending a trace successfully"""
        self.tracer.start_trace("research_1")
        self.tracer.end_trace("research_1", success=True)

        trace = self.tracer.get_trace("research_1")
        assert trace.success is True
        assert trace.completed_at is not None

    def test_end_trace_failure(self):
        """Test ending a trace with failure"""
        self.tracer.start_trace("research_1")
        self.tracer.end_trace("research_1", success=False, error_message="Test error")

        trace = self.tracer.get_trace("research_1")
        assert trace.success is False
        assert trace.error_message == "Test error"

    def test_record_event(self):
        """Test recording an event"""
        self.tracer.start_trace("research_1")
        self.tracer.record_event(
            TraceEventType.QUERY_GENERATED,
            metadata={"query": "test"},
        )

        trace = self.tracer.get_trace("research_1")
        assert trace.event_count >= 2  # Started + query generated

    def test_get_all_traces(self):
        """Test getting all traces"""
        self.tracer.start_trace("research_1")
        self.tracer.start_trace("research_2")

        traces = self.tracer.get_all_traces()
        assert len(traces) == 2

    def test_generate_report(self):
        """Test generating a report"""
        self.tracer.start_trace("research_1")
        self.tracer.record_event(TraceEventType.QUERY_GENERATED)
        self.tracer.record_event(TraceEventType.RESULT_RECEIVED)
        self.tracer.end_trace("research_1")

        report = self.tracer.generate_report("research_1")

        assert report is not None
        assert report["research_id"] == "research_1"
        assert report["success"] is True
        assert "event_counts" in report

    def test_generate_report_not_found(self):
        """Test generating report for non-existent trace"""
        report = self.tracer.generate_report("nonexistent")
        assert report is None

    def test_reset(self):
        """Test resetting traces"""
        self.tracer.start_trace("research_1")
        self.tracer.reset()

        assert self.tracer.get_all_traces() == []
