"""
Tests for fixture search provider
"""

import pytest
from pathlib import Path

from leedhunter.application.search.providers.fixture import FixtureSearchProvider
from leedhunter.domain.models import SearchQuery


class TestFixtureSearchProvider:
    """Tests for FixtureSearchProvider"""

    def setup_method(self):
        """Set up test fixtures"""
        # Use the actual fixtures directory
        fixtures_dir = Path(__file__).parent.parent.parent / "fixtures" / "search"
        self.provider = FixtureSearchProvider(fixtures_dir=str(fixtures_dir))

    def test_provider_name(self):
        """Test provider name"""
        assert self.provider.name == "fixture"

    def test_supported_operators(self):
        """Test supported operators"""
        operators = self.provider.supported_operators
        assert "site:" in operators
        assert "intitle:" in operators

    @pytest.mark.asyncio
    async def test_is_available(self):
        """Test provider is available"""
        assert await self.provider.is_available() is True

    @pytest.mark.asyncio
    async def test_get_health(self):
        """Test getting health"""
        health = await self.provider.get_health()
        assert health.status.value == "healthy"

    @pytest.mark.asyncio
    async def test_search_auto_importers(self):
        """Test searching for auto importers"""
        query = SearchQuery(
            terms=["auto", "importers", "mazandaran"],
        )
        result = await self.provider.search(query)

        assert result.success is True
        assert result.provider == "fixture"
        assert len(result.candidates) > 0

    @pytest.mark.asyncio
    async def test_search_restaurants(self):
        """Test searching for restaurants"""
        query = SearchQuery(
            terms=["restaurant", "tehran"],
        )
        result = await self.provider.search(query)

        assert result.success is True
        assert len(result.candidates) > 0

    @pytest.mark.asyncio
    async def test_search_persian_terms(self):
        """Test searching with Persian terms"""
        query = SearchQuery(
            terms=["خودرو", "مازندران"],
        )
        result = await self.provider.search(query)

        assert result.success is True
        assert len(result.candidates) > 0

    @pytest.mark.asyncio
    async def test_search_default_fixture(self):
        """Test searching with default fixture"""
        query = SearchQuery(
            terms=["unknown", "query"],
        )
        result = await self.provider.search(query)

        assert result.success is True
        # Should use default fixture
        assert len(result.candidates) > 0

    @pytest.mark.asyncio
    async def test_search_with_default_fixture_name(self):
        """Test searching with specified default fixture"""
        fixtures_dir = Path(__file__).parent.parent.parent / "fixtures" / "search"
        provider = FixtureSearchProvider(
            fixtures_dir=str(fixtures_dir),
            default_fixture="tehran_restaurants.json"
        )
        query = SearchQuery(terms=["test"])
        result = await provider.search(query)

        assert result.success is True
        assert len(result.candidates) > 0

    @pytest.mark.asyncio
    async def test_search_empty_fixture(self):
        """Test searching with non-existent fixture"""
        provider = FixtureSearchProvider(
            default_fixture="nonexistent.json"
        )
        query = SearchQuery(terms=["test"])
        result = await provider.search(query)

        assert result.success is True
        assert len(result.candidates) == 0

    @pytest.mark.asyncio
    async def test_candidate_fields(self):
        """Test that candidates have correct fields"""
        query = SearchQuery(terms=["auto", "mazandaran"])
        result = await self.provider.search(query)

        assert len(result.candidates) > 0
        candidate = result.candidates[0]

        assert candidate.source is not None
        assert candidate.source_url is not None
        assert candidate.metadata is not None

    @pytest.mark.asyncio
    async def test_add_fixture(self):
        """Test adding fixture programmatically"""
        self.provider.add_fixture("test", [
            {
                "source": "test",
                "source_url": "https://test.com",
                "observed_name": "Test Business",
            }
        ])

        query = SearchQuery(terms=["test"])
        # Force use of test fixture
        self.provider._default_fixture = "test"
        result = await self.provider.search(query)

        assert len(result.candidates) == 1
        assert result.candidates[0].observed_name == "Test Business"

    @pytest.mark.asyncio
    async def test_clear_fixtures(self):
        """Test clearing fixtures"""
        self.provider.add_fixture("test", [{"source": "test", "source_url": "https://test.com"}])
        self.provider.clear_fixtures()

        query = SearchQuery(terms=["test"])
        self.provider._default_fixture = "test"
        result = await self.provider.search(query)

        assert len(result.candidates) == 0

    @pytest.mark.asyncio
    async def test_search_time_recorded(self):
        """Test that search time is recorded"""
        query = SearchQuery(terms=["auto", "mazandaran"])
        result = await self.provider.search(query)

        assert result.search_time >= 0

    @pytest.mark.asyncio
    async def test_total_results(self):
        """Test total results count"""
        query = SearchQuery(terms=["auto", "mazandaran"])
        result = await self.provider.search(query)

        assert result.total_results == len(result.candidates)

    @pytest.mark.asyncio
    async def test_validate_query(self):
        """Test query validation"""
        query = SearchQuery(terms=["test"])
        errors = self.provider.validate_query(query)
        assert len(errors) == 0

    @pytest.mark.asyncio
    async def test_validate_query_with_operator(self):
        """Test query validation with supported operator"""
        query = SearchQuery(
            terms=["test"],
            operators={"site": "example.com"},
        )
        errors = self.provider.validate_query(query)
        assert len(errors) == 0
