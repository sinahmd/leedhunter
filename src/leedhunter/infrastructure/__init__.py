"""
Infrastructure layer - External integrations and implementations

This layer implements the interfaces defined in the application layer.
It contains database, cache, external API, and other infrastructure concerns.
"""

from leedhunter.infrastructure.database import (
    Base,
    EntityIdentityModel,
    EntityModel,
    EntityRepository,
    EvidenceModel,
    EvidenceRepository,
    LeadModel,
    LeadRepository,
    OpportunityModel,
    SignalModel,
    SignalRepository,
    close_db,
    get_engine_instance,
    get_session,
    get_session_factory_instance,
    init_db,
)
from leedhunter.infrastructure.errors import (
    AuthenticationError,
    InfrastructureError,
    NetworkError,
    ProviderError,
    RateLimitError,
    StorageError,
)

__all__ = [
    # Errors
    "InfrastructureError",
    "ProviderError",
    "AuthenticationError",
    "RateLimitError",
    "NetworkError",
    "StorageError",
    # Database
    "Base",
    "EntityModel",
    "EntityIdentityModel",
    "EvidenceModel",
    "SignalModel",
    "OpportunityModel",
    "LeadModel",
    "EntityRepository",
    "EvidenceRepository",
    "SignalRepository",
    "LeadRepository",
    "get_session",
    "init_db",
    "close_db",
    "get_engine_instance",
    "get_session_factory_instance",
]
