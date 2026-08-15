"""
Tests for database models
"""

from leedhunter.infrastructure.database.models import (
    EntityIdentityModel,
    EntityModel,
    EvidenceModel,
    LeadModel,
    OpportunityModel,
    SignalModel,
)


class TestEntityModel:
    """Tests for EntityModel"""

    def test_create_entity(self):
        """Test creating an EntityModel"""
        entity = EntityModel(
            canonical_name="Test Business",
            canonical_domain="test.com",
        )
        assert entity.canonical_name == "Test Business"
        assert entity.canonical_domain == "test.com"

    def test_entity_repr(self):
        """Test EntityModel repr"""
        entity = EntityModel(id=1, canonical_name="Test Business")
        assert "Entity" in repr(entity)
        assert "Test Business" in repr(entity)


class TestEntityIdentityModel:
    """Tests for EntityIdentityModel"""

    def test_create_identity(self):
        """Test creating an EntityIdentityModel"""
        identity = EntityIdentityModel(
            entity_id=1,
            identity_type="website",
            value="https://test.com",
            normalized_value="test.com",
            is_primary=True,
            source="google",
            source_url="https://google.com",
        )
        assert identity.identity_type == "website"
        assert identity.is_primary is True

    def test_identity_repr(self):
        """Test EntityIdentityModel repr"""
        identity = EntityIdentityModel(
            id=1,
            identity_type="website",
            value="https://test.com",
        )
        assert "EntityIdentity" in repr(identity)


class TestEvidenceModel:
    """Tests for EvidenceModel"""

    def test_create_evidence(self):
        """Test creating an EvidenceModel"""
        evidence = EvidenceModel(
            entity_id=1,
            claim="Test claim",
            value="Test value",
            source="instagram",
            source_url="https://instagram.com/test",
            confidence=0.85,
        )
        assert evidence.claim == "Test claim"
        assert evidence.confidence == 0.85


class TestSignalModel:
    """Tests for SignalModel"""

    def test_create_signal(self):
        """Test creating a SignalModel"""
        signal = SignalModel(
            entity_id=1,
            signal_type="expansion",
            description="Expanding to new locations",
            confidence=0.8,
        )
        assert signal.signal_type == "expansion"
        assert signal.confidence == 0.8


class TestOpportunityModel:
    """Tests for OpportunityModel"""

    def test_create_opportunity(self):
        """Test creating an OpportunityModel"""
        opportunity = OpportunityModel(
            entity_id=1,
            description="Potential opportunity",
            relevance_score=0.75,
        )
        assert opportunity.relevance_score == 0.75


class TestLeadModel:
    """Tests for LeadModel"""

    def test_create_lead(self):
        """Test creating a LeadModel"""
        lead = LeadModel(
            entity_id=1,
            score=85.0,
            status="qualified",
        )
        assert lead.score == 85.0
        assert lead.status == "qualified"

    def test_lead_repr(self):
        """Test LeadModel repr"""
        lead = LeadModel(id=1, score=85.0, status="qualified")
        assert "Lead" in repr(lead)
        assert "85.0" in repr(lead)
