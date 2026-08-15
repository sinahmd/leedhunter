"""
SQLAlchemy ORM models

These models represent the database schema and map to domain models.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from leedhunter.infrastructure.database.base import Base


def _utcnow() -> datetime:
    """Get current UTC time with timezone info"""
    return datetime.now(timezone.utc)


class EntityModel(Base):
    """Entity database model"""

    __tablename__ = "entities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    canonical_name: Mapped[str] = mapped_column(String(500), nullable=False)
    canonical_name_normalized: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    canonical_domain: Mapped[str | None] = mapped_column(String(200), nullable=True, unique=True)
    canonical_domain_normalized: Mapped[str | None] = mapped_column(
        String(200), nullable=True, index=True
    )
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    # Relationships
    identities: Mapped[list["EntityIdentityModel"]] = relationship(
        "EntityIdentityModel",
        back_populates="entity",
        cascade="all, delete-orphan",
    )
    evidence: Mapped[list["EvidenceModel"]] = relationship(
        "EvidenceModel",
        back_populates="entity",
        cascade="all, delete-orphan",
    )
    signals: Mapped[list["SignalModel"]] = relationship(
        "SignalModel",
        back_populates="entity",
        cascade="all, delete-orphan",
    )
    opportunities: Mapped[list["OpportunityModel"]] = relationship(
        "OpportunityModel",
        back_populates="entity",
        cascade="all, delete-orphan",
    )
    leads: Mapped[list["LeadModel"]] = relationship(
        "LeadModel",
        back_populates="entity",
        cascade="all, delete-orphan",
    )

    # Indexes
    __table_args__ = (
        Index("idx_entity_canonical_name", "canonical_name"),
        Index("idx_entity_canonical_domain", "canonical_domain"),
        Index("idx_entity_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Entity(id={self.id}, name='{self.canonical_name}')>"


class EntityIdentityModel(Base):
    """Entity Identity database model"""

    __tablename__ = "entity_identities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_id: Mapped[int] = mapped_column(Integer, ForeignKey("entities.id"), nullable=False)
    identity_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # website, instagram, linkedin, phone, email, google_profile
    value: Mapped[str] = mapped_column(String(500), nullable=False)
    value_normalized: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    normalized_value: Mapped[str] = mapped_column(String(500), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    source_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    discovered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    # Relationships
    entity: Mapped["EntityModel"] = relationship("EntityModel", back_populates="identities")

    # Uniqueness constraints
    __table_args__ = (
        UniqueConstraint(
            "entity_id", "identity_type", "normalized_value", name="uq_entity_identity"
        ),
        Index("idx_identity_type_normalized", "identity_type", "normalized_value"),
        Index("idx_identity_entity_id", "entity_id"),
    )

    def __repr__(self) -> str:
        return f"<EntityIdentity(id={self.id}, type='{self.identity_type}', value='{self.value}')>"


class EvidenceModel(Base):
    """Evidence database model"""

    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_id: Mapped[int] = mapped_column(Integer, ForeignKey("entities.id"), nullable=False)
    claim: Mapped[str] = mapped_column(String(1000), nullable=False)
    claim_normalized: Mapped[str] = mapped_column(String(1000), nullable=False, index=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    value_normalized: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    source_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)

    # Relationships
    entity: Mapped["EntityModel"] = relationship("EntityModel", back_populates="evidence")

    # Indexes
    __table_args__ = (
        Index("idx_evidence_entity_id", "entity_id"),
        Index("idx_evidence_source", "source"),
        Index("idx_evidence_observed_at", "observed_at"),
    )

    def __repr__(self) -> str:
        return f"<Evidence(id={self.id}, claim='{self.claim[:50]}...')>"


class SignalModel(Base):
    """Signal database model"""

    __tablename__ = "signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_id: Mapped[int] = mapped_column(Integer, ForeignKey("entities.id"), nullable=False)
    signal_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # expansion, digital_presence, engagement, activity, contactability
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    description_normalized: Mapped[str] = mapped_column(String(1000), nullable=False, index=True)
    evidence_ids_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)

    # Relationships
    entity: Mapped["EntityModel"] = relationship("EntityModel", back_populates="signals")

    # Indexes
    __table_args__ = (
        Index("idx_signal_entity_id", "entity_id"),
        Index("idx_signal_type", "signal_type"),
    )

    def __repr__(self) -> str:
        return f"<Signal(id={self.id}, type='{self.signal_type}')>"


class OpportunityModel(Base):
    """Opportunity database model"""

    __tablename__ = "opportunities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_id: Mapped[int] = mapped_column(Integer, ForeignKey("entities.id"), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    description_normalized: Mapped[str] = mapped_column(String(1000), nullable=False, index=True)
    signal_ids_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    relevance_score: Mapped[float] = mapped_column(Float, nullable=False)

    # Relationships
    entity: Mapped["EntityModel"] = relationship("EntityModel", back_populates="opportunities")

    # Indexes
    __table_args__ = (
        Index("idx_opportunity_entity_id", "entity_id"),
        Index("idx_opportunity_relevance", "relevance_score"),
    )

    def __repr__(self) -> str:
        return f"<Opportunity(id={self.id}, relevance={self.relevance_score})>"


class LeadModel(Base):
    """Lead database model"""

    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("entities.id"), nullable=False, unique=True
    )
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="new"
    )  # new, qualified, disqualified, contacted
    qualification_reasons_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    # Relationships
    entity: Mapped["EntityModel"] = relationship("EntityModel", back_populates="leads")

    # Indexes
    __table_args__ = (
        Index("idx_lead_entity_id", "entity_id"),
        Index("idx_lead_score", "score"),
        Index("idx_lead_status", "status"),
        Index("idx_lead_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Lead(id={self.id}, score={self.score}, status='{self.status}')>"
