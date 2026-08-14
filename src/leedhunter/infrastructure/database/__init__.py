"""
Database infrastructure layer

This module provides database connectivity, session management, and ORM models.
"""

from leedhunter.infrastructure.database.base import (
    Base,
    get_engine_instance,
    get_session_factory_instance,
    get_session,
    init_db,
    close_db,
)
from leedhunter.infrastructure.database.models import (
    EntityModel,
    EntityIdentityModel,
    EvidenceModel,
    SignalModel,
    OpportunityModel,
    LeadModel,
)
from leedhunter.infrastructure.database.repositories import (
    EntityRepository,
    EvidenceRepository,
    SignalRepository,
    LeadRepository,
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
