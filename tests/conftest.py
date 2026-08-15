"""
Pytest configuration and fixtures
"""

import pytest

from leedhunter.config import Settings, reset_settings


@pytest.fixture(autouse=True)
def reset_config():
    """Reset settings before each test"""
    reset_settings()
    yield
    reset_settings()


@pytest.fixture
def test_settings():
    """Create test settings with mock values"""
    return Settings(
        debug=True,
        database=Settings().database.model_copy(update={"host": "localhost", "port": 5432}),
        redis=Settings().redis.model_copy(update={"host": "localhost", "port": 6379}),
        llm=Settings().llm.model_copy(update={"api_key": "test-key"}),
    )


@pytest.fixture
def sample_search_intent():
    """Sample SearchIntent for testing"""
    from leedhunter.domain.models import SearchIntent

    return SearchIntent(
        objective="Find auto importers in Mazandaran",
        location="Mazandaran",
        industry="Automotive",
        constraints=["import", "vehicles"],
    )


@pytest.fixture
def sample_candidate():
    """Sample Candidate for testing"""
    from datetime import datetime, timezone

    from leedhunter.domain.models import Candidate

    return Candidate(
        source="google",
        source_url="https://example.com",
        observed_name="Example Auto",
        observed_domain="example.com",
        observed_username="example_auto",
        observed_phone="+98 123 456 7890",
        observed_email="info@example.com",
        metadata={"platform": "website"},
        discovered_at=datetime.now(timezone.utc),
        query_id="test-query-1",
    )


@pytest.fixture
def sample_entity():
    """Sample Entity for testing"""
    from datetime import datetime, timezone

    from leedhunter.domain.models import Entity, EntityIdentity, EntityIdentityType

    return Entity(
        id="test-entity-1",
        canonical_name="Example Auto Importers",
        canonical_domain="example.com",
        identities=[
            EntityIdentity(
                type=EntityIdentityType.WEBSITE,
                value="https://example.com",
                normalized_value="example.com",
                is_primary=True,
                is_verified=True,
                source="google",
                source_url="https://example.com",
            ),
            EntityIdentity(
                type=EntityIdentityType.INSTAGRAM,
                value="@example_auto",
                normalized_value="example_auto",
                is_primary=False,
                is_verified=False,
                source="instagram",
                source_url="https://instagram.com/example_auto",
            ),
        ],
        metadata={"industry": "automotive", "location": "Mazandaran"},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_evidence():
    """Sample Evidence for testing"""
    from datetime import datetime, timezone

    from leedhunter.domain.models import Evidence

    return Evidence(
        entity_id="test-entity-1",
        claim="Opening new branch in Sari",
        value="New branch announcement",
        source="instagram",
        source_url="https://instagram.com/example_auto/123",
        observed_at=datetime.now(timezone.utc),
        confidence=0.85,
    )


@pytest.fixture
def sample_signal():
    """Sample Signal for testing"""
    from leedhunter.domain.models import Signal, SignalType

    return Signal(
        entity_id="test-entity-1",
        signal_type=SignalType.EXPANSION,
        description="Business expanding to new locations",
        evidence_ids=["evidence-1", "evidence-2"],
        confidence=0.8,
    )


@pytest.fixture
def sample_lead(sample_entity, sample_signal, sample_evidence):
    """Sample Lead for testing"""
    from datetime import datetime, timezone

    from leedhunter.domain.models import Lead, LeadStatus, Opportunity

    return Lead(
        entity=sample_entity,
        opportunities=[
            Opportunity(
                entity_id=sample_entity.id,
                description="Potential need for digital marketing services",
                signal_ids=[sample_signal.entity_id],
                relevance_score=0.75,
            ),
        ],
        signals=[sample_signal],
        evidence=[sample_evidence],
        score=85.0,
        status=LeadStatus.QUALIFIED,
        qualification_reasons=["Strong expansion signals", "Active social presence"],
        created_at=datetime.now(timezone.utc),
    )
