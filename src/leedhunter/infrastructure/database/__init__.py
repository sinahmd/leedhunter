"""
Database infrastructure layer

This module provides database connectivity, session management, and ORM models.
"""

from leedhunter.infrastructure.database.base import (
    Base,
    close_db,
    get_engine_instance,
    get_session,
    get_session_factory_instance,
    init_db,
)
from leedhunter.infrastructure.database.models import (
    EntityIdentityModel,
    EntityModel,
    EvidenceModel,
    LeadModel,
    OpportunityModel,
    SignalModel,
)
from leedhunter.infrastructure.database.repositories import (
    EntityRepository,
    EvidenceRepository,
    LeadRepository,
    SignalRepository,
)

__all__ = [
    # Base
    "Base",
    "get_engine_instance",
    "get_session_factory_instance",
    "get_session",
    "init_db",
    "close_db",
    # Models
    "EntityModel",
    "EntityIdentityModel",
    "EvidenceModel",
    "SignalModel",
    "OpportunityModel",
    "LeadModel",
    # Repositories
    "EntityRepository",
    "EvidenceRepository",
    "SignalRepository",
    "LeadRepository",
]
