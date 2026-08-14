"""
Tests for domain models
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

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
    SearchQuery,
    Signal,
    SignalType,
)


class TestSearchIntent:
    """Tests for SearchIntent model"""

    def test_create_minimal_intent(self):
        """Test creating a SearchIntent with minimal fields"""
        intent = SearchIntent(objective="Find auto importers")
        assert intent.objective == "Find auto importers"
        assert intent.location is None
        assert intent.industry is None
        assert intent.constraints == []

    def test_create_full_intent(self):
        """Test creating a SearchIntent with all fields"""
        intent = SearchIntent(
            objective="Find auto importers in Mazandaran",
            location="Mazandaran",
            industry="Automotive",
            constraints=["import", "vehicles"],
        )
        assert intent.objective == "Find auto importers in Mazandaran"
        assert intent.location == "Mazandaran"
        assert intent.industry == "Automotive"
        assert intent.constraints == ["import", "vehicles"]


class TestSearchQuery:
    """Tests for SearchQuery model"""

    def test_create_minimal_query(self):
        """Test creating a SearchQuery with minimal fields"""
        query = SearchQuery()
        assert query.terms == []
        assert query.exact_phrases == []
        assert query.operators == {}
        assert query.exclusions == []
        assert query.provider is None

    def test_create_full_query(self):
        """Test creating a SearchQuery with all fields"""
        query = SearchQuery(
            terms=["auto", "importers"],
            exact_phrases=["واردات خودرو"],
            operators={"site": "instagram.com"},
            exclusions=["used", "parts"],
            provider="google",
        )
        assert query.terms == ["auto", "importers"]
        assert query.exact_phrases == ["واردات خودرو"]
        assert query.operators == {"site": "instagram.com"}
        assert query.exclusions == ["used", "parts"]
        assert query.provider == "google"


class TestCandidate:
    """Tests for Candidate model"""

    def test_create_candidate(self, sample_candidate):
        """Test creating a Candidate"""
        assert sample_candidate.source == "google"
        assert sample_candidate.source_url == "https://example.com"
        assert sample_candidate.observed_name == "Example Auto"
        assert sample_candidate.observed_domain == "example.com"

    def test_candidate_optional_fields(self):
        """Test Candidate with optional fields as None"""
        candidate = Candidate(
            source="google",
            source_url="https://example.com",
        )
        assert candidate.observed_name is None
        assert candidate.observed_domain is None
        assert candidate.observed_username is None


class TestEntityIdentity:
    """Tests for EntityIdentity model"""

    def test_create_identity(self):
        """Test creating an EntityIdentity"""
        identity = EntityIdentity(
            type=EntityIdentityType.WEBSITE,
            value="https://example.com",
            normalized_value="example.com",
            is_primary=True,
            is_verified=True,
            source="google",
            source_url="https://example.com",
        )
        assert identity.type == EntityIdentityType.WEBSITE
        assert identity.value == "https://example.com"
        assert identity.normalized_value == "example.com"
        assert identity.is_primary is True
        assert identity.is_verified is True

    def test_identity_type_enum(self):
        """Test EntityIdentityType enum values"""
        assert EntityIdentityType.WEBSITE == "website"
        assert EntityIdentityType.INSTAGRAM == "instagram"
        assert EntityIdentityType.LINKEDIN == "linkedin"
        assert EntityIdentityType.PHONE == "phone"
        assert EntityIdentityType.EMAIL == "email"
        assert EntityIdentityType.GOOGLE_PROFILE == "google_profile"


class TestEntity:
    """Tests for Entity model"""

    def test_create_entity(self, sample_entity):
        """Test creating an Entity"""
        assert sample_entity.canonical_name == "Example Auto Importers"
        assert sample_entity.canonical_domain == "example.com"
        assert len(sample_entity.identities) == 2

    def test_entity_with_no_id(self):
        """Test Entity with no ID (new entity)"""
        entity = Entity(
            canonical_name="New Business",
        )
        assert entity.id is None
        assert entity.canonical_name == "New Business"


class TestEvidence:
    """Tests for Evidence model"""

    def test_create_evidence(self, sample_evidence):
        """Test creating Evidence"""
        assert sample_evidence.entity_id == "test-entity-1"
        assert sample_evidence.claim == "Opening new branch in Sari"
        assert sample_evidence.confidence == 0.85

    def test_evidence_confidence_bounds(self):
        """Test Evidence confidence validation"""
        # Valid confidence
        evidence = Evidence(
            entity_id="test",
            claim="test claim",
            value="test value",
            source="test",
            source_url="https://test.com",
            confidence=0.5,
        )
        assert evidence.confidence == 0.5

        # Invalid confidence (too high)
        with pytest.raises(ValidationError):
            Evidence(
                entity_id="test",
                claim="test claim",
                value="test value",
                source="test",
                source_url="https://test.com",
                confidence=1.5,
            )

        # Invalid confidence (negative)
        with pytest.raises(ValidationError):
            Evidence(
                entity_id="test",
                claim="test claim",
                value="test value",
                source="test",
                source_url="https://test.com",
                confidence=-0.1,
            )


class TestSignal:
    """Tests for Signal model"""

    def test_create_signal(self, sample_signal):
        """Test creating a Signal"""
        assert sample_signal.entity_id == "test-entity-1"
        assert sample_signal.signal_type == SignalType.EXPANSION
        assert sample_signal.confidence == 0.8

    def test_signal_type_enum(self):
        """Test SignalType enum values"""
        assert SignalType.EXPANSION == "expansion"
        assert SignalType.DIGITAL_PRESENCE == "digital_presence"
        assert SignalType.ENGAGEMENT == "engagement"
        assert SignalType.ACTIVITY == "activity"
        assert SignalType.CONTACTABILITY == "contactability"


class TestOpportunity:
    """Tests for Opportunity model"""

    def test_create_opportunity(self):
        """Test creating an Opportunity"""
        opportunity = Opportunity(
            entity_id="test-entity-1",
            description="Potential need for services",
            signal_ids=["signal-1"],
            relevance_score=0.75,
        )
        assert opportunity.entity_id == "test-entity-1"
        assert opportunity.relevance_score == 0.75


class TestLead:
    """Tests for Lead model"""

    def test_create_lead(self, sample_lead):
        """Test creating a Lead"""
        assert sample_lead.entity.canonical_name == "Example Auto Importers"
        assert sample_lead.score == 85.0
        assert sample_lead.status == LeadStatus.QUALIFIED
        assert len(sample_lead.opportunities) == 1
        assert len(sample_lead.signals) == 1
        assert len(sample_lead.evidence) == 1

    def test_lead_status_enum(self):
        """Test LeadStatus enum values"""
        assert LeadStatus.NEW == "new"
        assert LeadStatus.QUALIFIED == "qualified"
        assert LeadStatus.DISQUALIFIED == "disqualified"
        assert LeadStatus.CONTACTED == "contacted"

    def test_lead_score_bounds(self):
        """Test Lead score validation"""
        # Valid score
        entity = Entity(canonical_name="Test Business")
        lead = Lead(
            entity=entity,
            score=50.0,
        )
        assert lead.score == 50.0

        # Invalid score (too high)
        with pytest.raises(ValidationError):
            Lead(
                entity=entity,
                score=101.0,
            )

        # Invalid score (negative)
        with pytest.raises(ValidationError):
            Lead(
                entity=entity,
                score=-1.0,
            )
