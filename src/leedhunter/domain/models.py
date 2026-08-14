"""
Core domain models for LeedHunter

These models represent the core business entities and are independent of
infrastructure concerns.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator


def _utcnow() -> datetime:
    """Get current UTC time with timezone info"""
    return datetime.now(timezone.utc)


class SearchIntent(BaseModel):
    """Represents the user's prospecting objective"""

    objective: str = Field(..., min_length=1, max_length=1000)
    location: Optional[str] = Field(None, max_length=200)
    industry: Optional[str] = Field(None, max_length=200)
    constraints: list[str] = Field(default_factory=list)

    @field_validator("objective")
    @classmethod
    def validate_objective(cls, v: str) -> str:
        """Validate objective is not just whitespace"""
        if not v.strip():
            raise ValueError("Objective cannot be empty or just whitespace")
        return v.strip()

    @field_validator("constraints")
    @classmethod
    def validate_constraints(cls, v: list[str]) -> list[str]:
        """Validate and clean constraints"""
        return [c.strip() for c in v if c.strip()]


class Candidate(BaseModel):
    """Represents a potential business entity discovered through search"""

    source: str = Field(..., min_length=1)
    source_url: str = Field(..., min_length=1)
    observed_name: Optional[str] = Field(None, max_length=500)
    observed_domain: Optional[str] = Field(None, max_length=200)
    observed_username: Optional[str] = Field(None, max_length=200)
    observed_phone: Optional[str] = Field(None, max_length=50)
    observed_email: Optional[str] = Field(None, max_length=200)
    metadata: dict[str, str] = Field(default_factory=dict)
    discovered_at: datetime = Field(default_factory=_utcnow)
    query_id: Optional[str] = None

    @field_validator("source_url")
    @classmethod
    def validate_source_url(cls, v: str) -> str:
        """Validate source URL format"""
        if not v.startswith(("http://", "https://")):
            raise ValueError("Source URL must start with http:// or https://")
        return v

    @field_validator("observed_email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """Basic email validation"""
        if v is not None and "@" not in v:
            raise ValueError("Invalid email format")
        return v

    def has_identity(self) -> bool:
        """Check if candidate has any identity information"""
        return any([
            self.observed_domain,
            self.observed_username,
            self.observed_phone,
            self.observed_email,
        ])


class EntityIdentityType(str, Enum):
    """Types of entity identities"""

    WEBSITE = "website"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    PHONE = "phone"
    EMAIL = "email"
    GOOGLE_PROFILE = "google_profile"


class EntityIdentity(BaseModel):
    """Represents a single identity/channel for an entity"""

    type: EntityIdentityType
    value: str = Field(..., min_length=1)
    normalized_value: str = Field(..., min_length=1)
    is_primary: bool = False
    is_verified: bool = False
    source: str = Field(..., min_length=1)
    source_url: str = Field(..., min_length=1)
    discovered_at: datetime = Field(default_factory=_utcnow)

    @model_validator(mode="after")
    def validate_identity(self) -> "EntityIdentity":
        """Validate identity consistency"""
        if self.type == EntityIdentityType.EMAIL and "@" not in self.value:
            raise ValueError("Email identity must contain @")
        if self.type == EntityIdentityType.PHONE and not any(c.isdigit() for c in self.value):
            raise ValueError("Phone identity must contain digits")
        return self


class Entity(BaseModel):
    """Represents a canonical real-world business entity"""

    id: Optional[str] = None
    canonical_name: str = Field(..., min_length=1, max_length=500)
    canonical_domain: Optional[str] = Field(None, max_length=200)
    identities: list[EntityIdentity] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)

    @model_validator(mode="after")
    def validate_update_time(self) -> "Entity":
        """Ensure updated_at is not before created_at"""
        if self.updated_at < self.created_at:
            self.updated_at = self.created_at
        return self

    def get_identity(self, identity_type: EntityIdentityType) -> Optional[EntityIdentity]:
        """Get the first identity of the specified type"""
        for identity in self.identities:
            if identity.type == identity_type:
                return identity
        return None

    def get_primary_identity(self) -> Optional[EntityIdentity]:
        """Get the primary identity"""
        for identity in self.identities:
            if identity.is_primary:
                return identity
        return None

    def add_identity(self, identity: EntityIdentity) -> None:
        """Add an identity to the entity"""
        # If this is the first identity of its type, make it primary
        if not any(i.type == identity.type for i in self.identities):
            identity.is_primary = True
        self.identities.append(identity)
        self.updated_at = _utcnow()


class Evidence(BaseModel):
    """Represents a factual observation about an entity"""

    entity_id: str = Field(..., min_length=1)
    claim: str = Field(..., min_length=1, max_length=1000)
    value: str = Field(..., min_length=1, max_length=5000)
    source: str = Field(..., min_length=1)
    source_url: str = Field(..., min_length=1)
    observed_at: datetime = Field(default_factory=_utcnow)
    confidence: float = Field(ge=0.0, le=1.0)

    @field_validator("source_url")
    @classmethod
    def validate_source_url(cls, v: str) -> str:
        """Validate source URL format"""
        if not v.startswith(("http://", "https://")):
            raise ValueError("Source URL must start with http:// or https://")
        return v

    def is_high_confidence(self, threshold: float = 0.8) -> bool:
        """Check if evidence has high confidence"""
        return self.confidence >= threshold

    def is_recent(self, days: int = 30) -> bool:
        """Check if evidence is recent (within specified days)"""
        from datetime import timedelta
        return (_utcnow() - self.observed_at) <= timedelta(days=days)


class SignalType(str, Enum):
    """Types of business signals"""

    EXPANSION = "expansion"
    DIGITAL_PRESENCE = "digital_presence"
    ENGAGEMENT = "engagement"
    ACTIVITY = "activity"
    CONTACTABILITY = "contactability"


class Signal(BaseModel):
    """Represents an inferred business signal"""

    entity_id: str = Field(..., min_length=1)
    signal_type: SignalType
    description: str = Field(..., min_length=1, max_length=1000)
    evidence_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)

    def has_evidence(self) -> bool:
        """Check if signal has supporting evidence"""
        return len(self.evidence_ids) > 0


class Opportunity(BaseModel):
    """Represents a business opportunity identified from signals"""

    entity_id: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1, max_length=1000)
    signal_ids: list[str] = Field(default_factory=list)
    relevance_score: float = Field(ge=0.0, le=1.0)

    def is_high_relevance(self, threshold: float = 0.7) -> bool:
        """Check if opportunity has high relevance"""
        return self.relevance_score >= threshold


class LeadStatus(str, Enum):
    """Status of a lead"""

    NEW = "new"
    QUALIFIED = "qualified"
    DISQUALIFIED = "disqualified"
    CONTACTED = "contacted"


class Lead(BaseModel):
    """Represents a qualified business lead"""

    entity: Entity
    opportunities: list[Opportunity] = Field(default_factory=list)
    signals: list[Signal] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    score: float = Field(ge=0.0, le=100.0)
    status: LeadStatus = LeadStatus.NEW
    qualification_reasons: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_utcnow)

    def is_qualified(self) -> bool:
        """Check if lead is qualified"""
        return self.status == LeadStatus.QUALIFIED

    def is_high_score(self, threshold: float = 70.0) -> bool:
        """Check if lead has a high score"""
        return self.score >= threshold

    def get_evidence_count(self) -> int:
        """Get the number of evidence items"""
        return len(self.evidence)

    def get_signal_count(self) -> int:
        """Get the number of signals"""
        return len(self.signals)

    def get_opportunity_count(self) -> int:
        """Get the number of opportunities"""
        return len(self.opportunities)

    def has_contact_info(self) -> bool:
        """Check if lead has contact information"""
        for identity in self.entity.identities:
            if identity.type in [EntityIdentityType.PHONE, EntityIdentityType.EMAIL]:
                return True
        return False
