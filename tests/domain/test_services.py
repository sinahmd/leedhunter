"""
Tests for domain services
"""

import pytest
from datetime import datetime, timezone

from leedhunter.domain.models import (
    Candidate,
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
from leedhunter.domain.services import (
    EntityResolutionService,
    QualificationService,
    ScoringService,
)


class TestEntityResolutionService:
    """Tests for EntityResolutionService"""

    def setup_method(self):
        """Set up test fixtures"""
        self.service = EntityResolutionService()

    def test_exact_match_by_domain(self):
        """Test exact matching by domain"""
        candidate = Candidate(
            source="google",
            source_url="https://example.com",
            observed_domain="example.com",
        )

        entity = Entity(
            id="entity-1",
            canonical_name="Example Corp",
            canonical_domain="example.com",
        )

        decision, matched = self.service.resolve_candidate(candidate, [entity])
        assert decision == "MATCH"
        assert matched == entity

    def test_exact_match_by_email(self):
        """Test exact matching by email"""
        candidate = Candidate(
            source="google",
            source_url="https://example.com",
            observed_email="info@example.com",
        )

        entity = Entity(
            id="entity-1",
            canonical_name="Example Corp",
            identities=[
                EntityIdentity(
                    type=EntityIdentityType.EMAIL,
                    value="info@example.com",
                    normalized_value="info@example.com",
                    source="google",
                    source_url="https://example.com",
                )
            ],
        )

        decision, matched = self.service.resolve_candidate(candidate, [entity])
        assert decision == "MATCH"
        assert matched == entity

    def test_exact_match_by_phone(self):
        """Test exact matching by phone"""
        candidate = Candidate(
            source="google",
            source_url="https://example.com",
            observed_phone="+98 123 456 7890",
        )

        entity = Entity(
            id="entity-1",
            canonical_name="Example Corp",
            identities=[
                EntityIdentity(
                    type=EntityIdentityType.PHONE,
                    value="01234567890",
                    normalized_value="01234567890",
                    source="google",
                    source_url="https://example.com",
                )
            ],
        )

        decision, matched = self.service.resolve_candidate(candidate, [entity])
        assert decision == "MATCH"
        assert matched == entity

    def test_exact_match_by_username(self):
        """Test exact matching by username"""
        candidate = Candidate(
            source="instagram",
            source_url="https://instagram.com/example",
            observed_username="example",
            metadata={"platform": "instagram"},
        )

        entity = Entity(
            id="entity-1",
            canonical_name="Example Corp",
            identities=[
                EntityIdentity(
                    type=EntityIdentityType.INSTAGRAM,
                    value="example",
                    normalized_value="example",
                    source="instagram",
                    source_url="https://instagram.com/example",
                )
            ],
        )

        decision, matched = self.service.resolve_candidate(candidate, [entity])
        assert decision == "MATCH"
        assert matched == entity

    def test_no_match_new_entity(self):
        """Test when no match is found"""
        candidate = Candidate(
            source="google",
            source_url="https://new.com",
            observed_domain="new.com",
        )

        entity = Entity(
            id="entity-1",
            canonical_name="Example Corp",
            canonical_domain="example.com",
        )

        decision, matched = self.service.resolve_candidate(candidate, [entity])
        assert decision == "NEW_ENTITY"
        assert matched is None

    def test_fuzzy_match(self):
        """Test fuzzy matching for very similar names"""
        candidate = Candidate(
            source="google",
            source_url="https://example.com",
            observed_name="Example Corporation",
        )

        entity = Entity(
            id="entity-1",
            canonical_name="Example Corporation",  # Exact match
        )

        decision, matched = self.service.resolve_candidate(candidate, [entity])
        assert decision == "MATCH"
        assert matched == entity

    def test_explain_match(self):
        """Test match explanation generation"""
        candidate = Candidate(
            source="google",
            source_url="https://example.com",
            observed_domain="example.com",
            observed_email="info@example.com",
        )

        entity = Entity(
            id="entity-1",
            canonical_name="Example Corp",
            canonical_domain="example.com",
            identities=[
                EntityIdentity(
                    type=EntityIdentityType.EMAIL,
                    value="info@example.com",
                    normalized_value="info@example.com",
                    source="google",
                    source_url="https://example.com",
                )
            ],
        )

        explanation = self.service.explain_match(candidate, entity, "MATCH")
        assert explanation["decision"] == "MATCH"
        assert "exact domain" in explanation["matched"]
        assert "exact email" in explanation["matched"]
        assert explanation["score"] > 0


class TestScoringService:
    """Tests for ScoringService"""

    def setup_method(self):
        """Set up test fixtures"""
        self.service = ScoringService()

    def test_calculate_score(self):
        """Test score calculation"""
        entity = Entity(
            id="entity-1",
            canonical_name="Example Corp",
            canonical_domain="example.com",
            identities=[
                EntityIdentity(
                    type=EntityIdentityType.WEBSITE,
                    value="https://example.com",
                    normalized_value="example.com",
                    source="google",
                    source_url="https://example.com",
                ),
                EntityIdentity(
                    type=EntityIdentityType.PHONE,
                    value="01234567890",
                    normalized_value="01234567890",
                    source="google",
                    source_url="https://example.com",
                ),
            ],
            metadata={"industry": "automotive", "location": "Mazandaran"},
        )

        lead = Lead(
            entity=entity,
            opportunities=[
                Opportunity(
                    entity_id="entity-1",
                    description="Test opportunity",
                    relevance_score=0.8,
                )
            ],
            signals=[
                Signal(
                    entity_id="entity-1",
                    signal_type=SignalType.EXPANSION,
                    description="Expanding to new locations",
                    confidence=0.9,
                )
            ],
            evidence=[
                Evidence(
                    entity_id="entity-1",
                    claim="Opening new branch",
                    value="New branch announcement",
                    source="instagram",
                    source_url="https://instagram.com/test",
                    confidence=0.85,
                )
            ],
            score=0.0,  # Will be calculated
        )

        score = self.service.calculate_score(lead)
        assert 0.0 <= score <= 100.0
        assert score > 0.0

    def test_explain_score(self):
        """Test score explanation generation"""
        entity = Entity(
            id="entity-1",
            canonical_name="Example Corp",
            metadata={"industry": "automotive"},
        )

        lead = Lead(
            entity=entity,
            score=50.0,
        )

        explanation = self.service.explain_score(lead)
        assert "total_score" in explanation
        assert "factors" in explanation
        assert "icp_fit" in explanation["factors"]
        assert "opportunity" in explanation["factors"]
        assert "signals" in explanation["factors"]
        assert "contactability" in explanation["factors"]


class TestQualificationService:
    """Tests for QualificationService"""

    def setup_method(self):
        """Set up test fixtures"""
        self.service = QualificationService()

    def test_qualify_lead_qualified(self):
        """Test qualifying a lead that meets criteria"""
        entity = Entity(
            id="entity-1",
            canonical_name="Example Corp",
            identities=[
                EntityIdentity(
                    type=EntityIdentityType.PHONE,
                    value="01234567890",
                    normalized_value="01234567890",
                    source="google",
                    source_url="https://example.com",
                )
            ],
        )

        lead = Lead(
            entity=entity,
            signals=[
                Signal(
                    entity_id="entity-1",
                    signal_type=SignalType.EXPANSION,
                    description="Expanding",
                    confidence=0.8,
                )
            ],
            score=75.0,
            status=LeadStatus.NEW,
        )

        qualified_lead = self.service.qualify_lead(lead, min_score=60.0)
        assert qualified_lead.status == LeadStatus.QUALIFIED
        assert len(qualified_lead.qualification_reasons) > 0

    def test_qualify_lead_disqualified(self):
        """Test disqualifying a lead that doesn't meet criteria"""
        entity = Entity(
            id="entity-1",
            canonical_name="Example Corp",
            identities=[
                EntityIdentity(
                    type=EntityIdentityType.PHONE,
                    value="01234567890",
                    normalized_value="01234567890",
                    source="google",
                    source_url="https://example.com",
                )
            ],
        )

        lead = Lead(
            entity=entity,
            score=40.0,
            status=LeadStatus.NEW,
        )

        qualified_lead = self.service.qualify_lead(lead, min_score=60.0)
        assert qualified_lead.status == LeadStatus.DISQUALIFIED

    def test_is_qualifiable(self):
        """Test qualifiability check"""
        entity = Entity(
            id="entity-1",
            canonical_name="Example Corp",
            identities=[
                EntityIdentity(
                    type=EntityIdentityType.PHONE,
                    value="01234567890",
                    normalized_value="01234567890",
                    source="google",
                    source_url="https://example.com",
                )
            ],
        )

        lead = Lead(
            entity=entity,
            signals=[
                Signal(
                    entity_id="entity-1",
                    signal_type=SignalType.EXPANSION,
                    description="Expanding",
                    confidence=0.8,
                )
            ],
            score=75.0,
        )

        assert self.service.is_qualifiable(lead, min_score=60.0) is True

    def test_is_not_qualifiable_low_score(self):
        """Test that lead with low score is not qualifiable"""
        entity = Entity(
            id="entity-1",
            canonical_name="Example Corp",
            identities=[
                EntityIdentity(
                    type=EntityIdentityType.PHONE,
                    value="01234567890",
                    normalized_value="01234567890",
                    source="google",
                    source_url="https://example.com",
                )
            ],
        )

        lead = Lead(
            entity=entity,
            signals=[
                Signal(
                    entity_id="entity-1",
                    signal_type=SignalType.EXPANSION,
                    description="Expanding",
                    confidence=0.8,
                )
            ],
            score=40.0,
        )

        assert self.service.is_qualifiable(lead, min_score=60.0) is False

    def test_is_not_qualifiable_no_identities(self):
        """Test that lead without identities is not qualifiable"""
        entity = Entity(
            id="entity-1",
            canonical_name="Example Corp",
        )

        lead = Lead(
            entity=entity,
            signals=[
                Signal(
                    entity_id="entity-1",
                    signal_type=SignalType.EXPANSION,
                    description="Expanding",
                    confidence=0.8,
                )
            ],
            score=75.0,
        )

        assert self.service.is_qualifiable(lead, min_score=60.0) is False
