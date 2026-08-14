"""
Domain events for LeedHunter

These events provide observability and traceability for the research pipeline.
Every important action should produce a domain event.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


def _utcnow() -> datetime:
    """Get current UTC time with timezone info"""
    return datetime.now(timezone.utc)


class EventType(str, Enum):
    """Types of domain events"""

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


class DomainEvent(BaseModel):
    """Base domain event"""

    event_type: EventType
    timestamp: datetime = Field(default_factory=_utcnow)
    event_id: Optional[str] = None
    correlation_id: Optional[str] = None  # Research job ID
    metadata: dict[str, Any] = Field(default_factory=dict)


class IntentCreatedEvent(DomainEvent):
    """Event fired when a search intent is created"""

    event_type: EventType = EventType.INTENT_CREATED
    objective: str = ""
    location: Optional[str] = None
    industry: Optional[str] = None


class QueryGeneratedEvent(DomainEvent):
    """Event fired when a search query is generated"""

    event_type: EventType = EventType.QUERY_GENERATED
    query_string: str = ""
    query_type: str = ""
    provider: Optional[str] = None


class QueryExecutedEvent(DomainEvent):
    """Event fired when a search query is executed"""

    event_type: EventType = EventType.QUERY_EXECUTED
    query_string: str = ""
    provider: str = ""
    result_count: int = 0
    duration_ms: float = 0.0


class ResultReceivedEvent(DomainEvent):
    """Event fired when search results are received"""

    event_type: EventType = EventType.RESULT_RECEIVED
    source: str = ""
    result_count: int = 0
    query_id: Optional[str] = None


class CandidateCreatedEvent(DomainEvent):
    """Event fired when a candidate is created"""

    event_type: EventType = EventType.CANDIDATE_CREATED
    candidate_id: Optional[str] = None
    source: str = ""
    source_url: str = ""
    observed_name: Optional[str] = None


class CandidateDeduplicatedEvent(DomainEvent):
    """Event fired when a candidate is deduplicated"""

    event_type: EventType = EventType.CANDIDATE_DEDUPLICATED
    candidate_id: str = ""
    duplicate_of: str = ""
    reason: str = ""


class EntityMatchedEvent(DomainEvent):
    """Event fired when a candidate matches an existing entity"""

    event_type: EventType = EventType.ENTITY_MATCHED
    candidate_id: str = ""
    entity_id: str = ""
    decision: str = ""  # MATCH, POSSIBLE_MATCH
    score: float = 0.0
    matched_on: list[str] = Field(default_factory=list)


class EntityCreatedEvent(DomainEvent):
    """Event fired when a new entity is created"""

    event_type: EventType = EventType.ENTITY_CREATED
    entity_id: str = ""
    canonical_name: str = ""
    canonical_domain: Optional[str] = None
    source: str = ""


class IdentityAttachedEvent(DomainEvent):
    """Event fired when an identity is attached to an entity"""

    event_type: EventType = EventType.IDENTITY_ATTACHED
    entity_id: str = ""
    identity_type: str = ""
    identity_value: str = ""
    source: str = ""


class EvidenceCreatedEvent(DomainEvent):
    """Event fired when evidence is created"""

    event_type: EventType = EventType.EVIDENCE_CREATED
    evidence_id: Optional[str] = None
    entity_id: str = ""
    claim: str = ""
    confidence: float = 0.0
    source: str = ""


class SignalCreatedEvent(DomainEvent):
    """Event fired when a signal is created"""

    event_type: EventType = EventType.SIGNAL_CREATED
    signal_id: Optional[str] = None
    entity_id: str = ""
    signal_type: str = ""
    confidence: float = 0.0


class LeadCreatedEvent(DomainEvent):
    """Event fired when a lead is created"""

    event_type: EventType = EventType.LEAD_CREATED
    lead_id: Optional[str] = None
    entity_id: str = ""
    score: float = 0.0
    status: str = ""


class ScoreCalculatedEvent(DomainEvent):
    """Event fired when a score is calculated"""

    event_type: EventType = EventType.SCORE_CALCULATED
    entity_id: str = ""
    score: float = 0.0
    factors: dict[str, float] = Field(default_factory=dict)


class ResearchStartedEvent(DomainEvent):
    """Event fired when a research job starts"""

    event_type: EventType = EventType.RESEARCH_STARTED
    research_id: str = ""
    objective: str = ""
    location: Optional[str] = None
    industry: Optional[str] = None


class ResearchCompletedEvent(DomainEvent):
    """Event fired when a research job completes"""

    event_type: EventType = EventType.RESEARCH_COMPLETED
    research_id: str = ""
    duration_seconds: float = 0.0
    candidates_found: int = 0
    entities_created: int = 0
    leads_qualified: int = 0


class ResearchFailedEvent(DomainEvent):
    """Event fired when a research job fails"""

    event_type: EventType = EventType.RESEARCH_FAILED
    research_id: str = ""
    error_type: str = ""
    error_message: str = ""
    partial_results: bool = False


class ProviderCalledEvent(DomainEvent):
    """Event fired when a provider is called"""

    event_type: EventType = EventType.PROVIDER_CALLED
    provider: str = ""
    operation: str = ""
    duration_ms: float = 0.0
    success: bool = True


class ProviderFailedEvent(DomainEvent):
    """Event fired when a provider fails"""

    event_type: EventType = EventType.PROVIDER_FAILED
    provider: str = ""
    operation: str = ""
    error_type: str = ""
    error_message: str = ""
    retryable: bool = True


class ErrorOccurredEvent(DomainEvent):
    """Event fired when an error occurs"""

    event_type: EventType = EventType.ERROR_OCCURRED
    error_type: str = ""
    error_message: str = ""
    context: dict[str, Any] = Field(default_factory=dict)
