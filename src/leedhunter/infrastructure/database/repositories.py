"""
Repository implementations

These repositories implement the application layer protocols and provide
data access for domain entities.
"""

import json
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from leedhunter.domain.models import (
    Entity,
    EntityIdentity,
    EntityIdentityType,
    Evidence,
    Lead,
    LeadStatus,
    Opportunity,
    Signal,
    SignalType,
)
from leedhunter.domain.normalization import (
    normalize_text,
    normalize_domain,
    normalize_phone,
    normalize_email,
    normalize_username,
)
from leedhunter.infrastructure.database.models import (
    EntityModel,
    EntityIdentityModel,
    EvidenceModel,
    LeadModel,
    OpportunityModel,
    SignalModel,
)


class EntityRepository:
    """Repository for Entity operations"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, entity: Entity) -> Entity:
        """Save an entity and return it with ID"""
        # Normalize Persian/Arabic text
        canonical_name_normalized = normalize_text(entity.canonical_name)
        canonical_domain_normalized = normalize_domain(entity.canonical_domain) if entity.canonical_domain else None

        # Check if entity exists
        if entity.id:
            result = await self.session.execute(
                select(EntityModel).where(EntityModel.id == int(entity.id))
            )
            model = result.scalar_one_or_none()
            if model:
                # Update existing
                model.canonical_name = entity.canonical_name
                model.canonical_name_normalized = canonical_name_normalized
                model.canonical_domain = entity.canonical_domain
                model.canonical_domain_normalized = canonical_domain_normalized
                model.metadata_json = json.dumps(entity.metadata) if entity.metadata else None
                model.updated_at = datetime.now(timezone.utc)
            else:
                # Create new with specified ID
                model = EntityModel(
                    id=int(entity.id),
                    canonical_name=entity.canonical_name,
                    canonical_name_normalized=canonical_name_normalized,
                    canonical_domain=entity.canonical_domain,
                    canonical_domain_normalized=canonical_domain_normalized,
                    metadata_json=json.dumps(entity.metadata) if entity.metadata else None,
                )
                self.session.add(model)
        else:
            # Create new
            model = EntityModel(
                canonical_name=entity.canonical_name,
                canonical_name_normalized=canonical_name_normalized,
                canonical_domain=entity.canonical_domain,
                canonical_domain_normalized=canonical_domain_normalized,
                metadata_json=json.dumps(entity.metadata) if entity.metadata else None,
            )
            self.session.add(model)

        await self.session.flush()

        # Update entity with generated ID
        entity.id = str(model.id)
        return entity

    async def get_by_id(self, entity_id: str) -> Optional[Entity]:
        """Get entity by ID"""
        result = await self.session.execute(
            select(EntityModel)
            .where(EntityModel.id == int(entity_id))
            .options(
                selectinload(EntityModel.identities),
                selectinload(EntityModel.evidence),
                selectinload(EntityModel.signals),
                selectinload(EntityModel.opportunities),
                selectinload(EntityModel.leads),
            )
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)

    async def get_by_domain(self, domain: str) -> Optional[Entity]:
        """Get entity by canonical domain"""
        result = await self.session.execute(
            select(EntityModel)
            .where(EntityModel.canonical_domain == domain)
            .options(
                selectinload(EntityModel.identities),
                selectinload(EntityModel.evidence),
                selectinload(EntityModel.signals),
                selectinload(EntityModel.opportunities),
                selectinload(EntityModel.leads),
            )
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)

    async def get_by_identity(
        self,
        identity_type: str,
        normalized_value: str,
    ) -> Optional[Entity]:
        """Get entity by identity"""
        result = await self.session.execute(
            select(EntityModel)
            .join(EntityIdentityModel)
            .where(
                EntityIdentityModel.identity_type == identity_type,
                EntityIdentityModel.normalized_value == normalized_value,
            )
            .options(
                selectinload(EntityModel.identities),
                selectinload(EntityModel.evidence),
                selectinload(EntityModel.signals),
                selectinload(EntityModel.opportunities),
                selectinload(EntityModel.leads),
            )
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[Entity]:
        """Get all entities with pagination"""
        result = await self.session.execute(
            select(EntityModel)
            .options(
                selectinload(EntityModel.identities),
                selectinload(EntityModel.evidence),
                selectinload(EntityModel.signals),
                selectinload(EntityModel.opportunities),
                selectinload(EntityModel.leads),
            )
            .limit(limit)
            .offset(offset)
        )
        models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def add_identity(self, entity_id: str, identity: EntityIdentity) -> None:
        """Add an identity to an entity"""
        # Normalize based on identity type
        value_normalized = self._normalize_identity_value(identity.type, identity.value)

        model = EntityIdentityModel(
            entity_id=int(entity_id),
            identity_type=identity.type.value,
            value=identity.value,
            value_normalized=value_normalized,
            normalized_value=identity.normalized_value,
            is_primary=identity.is_primary,
            is_verified=identity.is_verified,
            source=identity.source,
            source_url=identity.source_url,
        )
        self.session.add(model)
        await self.session.flush()

    def _normalize_identity_value(self, identity_type: EntityIdentityType, value: str) -> str:
        """Normalize identity value based on type"""
        if identity_type == EntityIdentityType.EMAIL:
            return normalize_email(value)
        elif identity_type == EntityIdentityType.PHONE:
            return normalize_phone(value)
        elif identity_type == EntityIdentityType.WEBSITE:
            return normalize_domain(value)
        elif identity_type in [EntityIdentityType.INSTAGRAM, EntityIdentityType.LINKEDIN]:
            return normalize_username(value)
        else:
            return normalize_text(value)

    async def delete(self, entity_id: str) -> bool:
        """Delete an entity by ID"""
        result = await self.session.execute(
            delete(EntityModel).where(EntityModel.id == int(entity_id))
        )
        return result.rowcount > 0

    def _to_domain(self, model: EntityModel) -> Entity:
        """Convert ORM model to domain model"""
        metadata = json.loads(model.metadata_json) if model.metadata_json else {}

        identities = []
        for identity_model in model.identities:
            identities.append(
                EntityIdentity(
                    type=EntityIdentityType(identity_model.identity_type),
                    value=identity_model.value,
                    normalized_value=identity_model.normalized_value,
                    is_primary=identity_model.is_primary,
                    is_verified=identity_model.is_verified,
                    source=identity_model.source,
                    source_url=identity_model.source_url,
                    discovered_at=identity_model.discovered_at,
                )
            )

        return Entity(
            id=str(model.id),
            canonical_name=model.canonical_name,
            canonical_domain=model.canonical_domain,
            identities=identities,
            metadata=metadata,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class EvidenceRepository:
    """Repository for Evidence operations"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, evidence: Evidence) -> Evidence:
        """Save evidence and return it with ID"""
        # Normalize Persian/Arabic text
        claim_normalized = normalize_text(evidence.claim)
        value_normalized = normalize_text(evidence.value)

        model = EvidenceModel(
            entity_id=int(evidence.entity_id),
            claim=evidence.claim,
            claim_normalized=claim_normalized,
            value=evidence.value,
            value_normalized=value_normalized,
            source=evidence.source,
            source_url=evidence.source_url,
            confidence=evidence.confidence,
        )
        self.session.add(model)
        await self.session.flush()

        evidence.entity_id = str(model.id)
        return evidence

    async def get_by_entity_id(self, entity_id: str) -> list[Evidence]:
        """Get all evidence for an entity"""
        result = await self.session.execute(
            select(EvidenceModel)
            .where(EvidenceModel.entity_id == int(entity_id))
            .order_by(EvidenceModel.observed_at.desc())
        )
        models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def get_by_id(self, evidence_id: str) -> Optional[Evidence]:
        """Get evidence by ID"""
        result = await self.session.execute(
            select(EvidenceModel).where(EvidenceModel.id == int(evidence_id))
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)

    async def delete(self, evidence_id: str) -> bool:
        """Delete evidence by ID"""
        result = await self.session.execute(
            delete(EvidenceModel).where(EvidenceModel.id == int(evidence_id))
        )
        return result.rowcount > 0

    def _to_domain(self, model: EvidenceModel) -> Evidence:
        """Convert ORM model to domain model"""
        return Evidence(
            entity_id=str(model.entity_id),
            claim=model.claim,
            value=model.value,
            source=model.source,
            source_url=model.source_url,
            observed_at=model.observed_at,
            confidence=model.confidence,
        )


class SignalRepository:
    """Repository for Signal operations"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, signal: Signal) -> Signal:
        """Save a signal and return it with ID"""
        # Normalize Persian/Arabic text
        description_normalized = normalize_text(signal.description)

        model = SignalModel(
            entity_id=int(signal.entity_id),
            signal_type=signal.signal_type.value,
            description=signal.description,
            description_normalized=description_normalized,
            evidence_ids_json=json.dumps(signal.evidence_ids) if signal.evidence_ids else None,
            confidence=signal.confidence,
        )
        self.session.add(model)
        await self.session.flush()

        signal.entity_id = str(model.id)
        return signal

    async def get_by_entity_id(self, entity_id: str) -> list[Signal]:
        """Get all signals for an entity"""
        result = await self.session.execute(
            select(SignalModel)
            .where(SignalModel.entity_id == int(entity_id))
        )
        models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def get_by_id(self, signal_id: str) -> Optional[Signal]:
        """Get signal by ID"""
        result = await self.session.execute(
            select(SignalModel).where(SignalModel.id == int(signal_id))
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)

    async def delete(self, signal_id: str) -> bool:
        """Delete signal by ID"""
        result = await self.session.execute(
            delete(SignalModel).where(SignalModel.id == int(signal_id))
        )
        return result.rowcount > 0

    def _to_domain(self, model: SignalModel) -> Signal:
        """Convert ORM model to domain model"""
        evidence_ids = json.loads(model.evidence_ids_json) if model.evidence_ids_json else []
        return Signal(
            entity_id=str(model.entity_id),
            signal_type=SignalType(model.signal_type),
            description=model.description,
            evidence_ids=evidence_ids,
            confidence=model.confidence,
        )


class LeadRepository:
    """Repository for Lead operations"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, lead: Lead) -> Lead:
        """Save a lead and return it with ID"""
        # Check if lead exists for entity
        result = await self.session.execute(
            select(LeadModel).where(LeadModel.entity_id == int(lead.entity.id))
        )
        model = result.scalar_one_or_none()

        if model:
            # Update existing
            model.score = lead.score
            model.status = lead.status.value
            model.qualification_reasons_json = (
                json.dumps(lead.qualification_reasons) if lead.qualification_reasons else None
            )
        else:
            # Create new
            model = LeadModel(
                entity_id=int(lead.entity.id),
                score=lead.score,
                status=lead.status.value,
                qualification_reasons_json=(
                    json.dumps(lead.qualification_reasons) if lead.qualification_reasons else None
                ),
            )
            self.session.add(model)

        await self.session.flush()
        return lead

    async def get_by_entity_id(self, entity_id: str) -> Optional[Lead]:
        """Get lead by entity ID"""
        result = await self.session.execute(
            select(LeadModel)
            .where(LeadModel.entity_id == int(entity_id))
            .options(selectinload(LeadModel.entity).selectinload(EntityModel.identities))
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)

    async def get_by_id(self, lead_id: str) -> Optional[Lead]:
        """Get lead by ID"""
        result = await self.session.execute(
            select(LeadModel)
            .where(LeadModel.id == int(lead_id))
            .options(selectinload(LeadModel.entity).selectinload(EntityModel.identities))
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)

    async def get_all(
        self,
        status: Optional[str] = None,
        min_score: Optional[float] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Lead]:
        """Get all leads with optional filters"""
        query = select(LeadModel).options(
            selectinload(LeadModel.entity).selectinload(EntityModel.identities)
        )

        if status:
            query = query.where(LeadModel.status == status)
        if min_score is not None:
            query = query.where(LeadModel.score >= min_score)

        query = query.order_by(LeadModel.score.desc()).limit(limit).offset(offset)

        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self._to_domain(model) for model in models]

    async def delete(self, lead_id: str) -> bool:
        """Delete lead by ID"""
        result = await self.session.execute(
            delete(LeadModel).where(LeadModel.id == int(lead_id))
        )
        return result.rowcount > 0

    def _to_domain(self, model: LeadModel) -> Lead:
        """Convert ORM model to domain model"""
        qualification_reasons = (
            json.loads(model.qualification_reasons_json)
            if model.qualification_reasons_json
            else []
        )

        # Convert entity
        entity = self._entity_to_domain(model.entity)

        return Lead(
            entity=entity,
            score=model.score,
            status=LeadStatus(model.status),
            qualification_reasons=qualification_reasons,
            created_at=model.created_at,
        )

    def _entity_to_domain(self, model: EntityModel) -> Entity:
        """Convert entity ORM model to domain model"""
        metadata = json.loads(model.metadata_json) if model.metadata_json else {}

        identities = []
        for identity_model in model.identities:
            identities.append(
                EntityIdentity(
                    type=EntityIdentityType(identity_model.identity_type),
                    value=identity_model.value,
                    normalized_value=identity_model.normalized_value,
                    is_primary=identity_model.is_primary,
                    is_verified=identity_model.is_verified,
                    source=identity_model.source,
                    source_url=identity_model.source_url,
                    discovered_at=identity_model.discovered_at,
                )
            )

        return Entity(
            id=str(model.id),
            canonical_name=model.canonical_name,
            canonical_domain=model.canonical_domain,
            identities=identities,
            metadata=metadata,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
