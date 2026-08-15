"""
Domain layer - Core business logic and models

This layer contains the core domain models and business rules.
It must NOT depend on infrastructure, CLI, or external libraries.
"""

from leedhunter.domain.events import (
    CandidateCreatedEvent,
    CandidateDeduplicatedEvent,
    DomainEvent,
    EntityCreatedEvent,
    EntityMatchedEvent,
    ErrorOccurredEvent,
    EventType,
    EvidenceCreatedEvent,
    IdentityAttachedEvent,
    IntentCreatedEvent,
    LeadCreatedEvent,
    ProviderCalledEvent,
    ProviderFailedEvent,
    QueryExecutedEvent,
    QueryGeneratedEvent,
    ResearchCompletedEvent,
    ResearchFailedEvent,
    ResearchStartedEvent,
    ResultReceivedEvent,
    ScoreCalculatedEvent,
    SignalCreatedEvent,
)
from leedhunter.domain.models import (
    Candidate,
    Entity,
    EntityIdentity,
    EntityIdentityType,
    Evidence,
    Lead,
    LeadStatus,
    Opportunity,
    SearchIntent,
    Signal,
    SignalType,
)
from leedhunter.domain.normalization import (
    PersianNormalizer,
    get_normalizer,
    normalize_domain,
    normalize_email,
    normalize_phone,
    normalize_text,
    normalize_username,
)
from leedhunter.domain.services import (
    EntityResolutionService,
    QualificationService,
    ScoringService,
)

__all__ = [
    # Models
    "SearchIntent",
    "Candidate",
    "Entity",
    "EntityIdentity",
    "EntityIdentityType",
    "Evidence",
    "Signal",
    "SignalType",
    "Opportunity",
    "Lead",
    "LeadStatus",
    # Services
    "EntityResolutionService",
    "ScoringService",
    "QualificationService",
    # Events
    "EventType",
    "DomainEvent",
    "IntentCreatedEvent",
    "QueryGeneratedEvent",
    "QueryExecutedEvent",
    "ResultReceivedEvent",
    "CandidateCreatedEvent",
    "CandidateDeduplicatedEvent",
    "EntityMatchedEvent",
    "EntityCreatedEvent",
    "IdentityAttachedEvent",
    "EvidenceCreatedEvent",
    "SignalCreatedEvent",
    "LeadCreatedEvent",
    "ScoreCalculatedEvent",
    "ResearchStartedEvent",
    "ResearchCompletedEvent",
    "ResearchFailedEvent",
    "ProviderCalledEvent",
    "ProviderFailedEvent",
    "ErrorOccurredEvent",
    # Normalization
    "PersianNormalizer",
    "get_normalizer",
    "normalize_text",
    "normalize_domain",
    "normalize_phone",
    "normalize_email",
    "normalize_username",
]
