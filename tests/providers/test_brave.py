"""
Tests for Brave Search Provider

These tests use MockBraveSearchProvider to avoid requiring a real API key.
"""

import pytest

from leedhunter.application.search.providers.brave import (
    BraveConfig,
    BraveSearchProvider,
    MockBraveSearchProvider,
)
from leedhunter.domain.search.query import QueryBuilder


class TestBraveConfig:
    """Tests for BraveConfig"""

    def test_config_creation(self):
        """Test creating BraveConfig"""
        config = BraveConfig(api_key="test-key")

        assert config.api_key == "test-key"
        assert config.endpoint == "https://api.search.brave.com/res/v1/web/search"
        assert config.max_results == 10

    def test_config_custom_values(self):
        """Test custom configuration"""
        config = BraveConfig(
            api_key="test-key",
            max_results=20,
            country="IR",
            search_lang="fa",
        )

        assert config.max_results == 20
        assert config.country == "IR"
        assert config.search_lang == "fa"


class TestBraveSearchProvider:
    """Tests for BraveSearchProvider (requires API key)"""

    def test_provider_requires_api_key(self):
        """Test that provider requires API key"""
        with pytest.raises(ValueError, match="API key is required"):
            BraveSearchProvider(BraveConfig(api_key=""))

    def test_provider_name(self):
        """Test provider name"""
        provider = BraveSearchProvider(BraveConfig(api_key="test-key"))
        assert provider.name == "brave"

    def test_provider_supported_operators(self):
        """Test supported operators"""
        provider = BraveSearchProvider(BraveConfig(api_key="test-key"))
        operators = provider.supported_operators
        assert "site:" in operators
        assert "intitle:" in operators
        assert "inurl:" in operators


class TestMockBraveSearchProvider:
    """Tests for MockBraveSearchProvider"""

    def setup_method(self):
        """Set up test fixtures"""
        self.results = [
            {
                "source_url": "https://example1.com",
                "observed_name": "Business One",
                "observed_domain": "example1.com",
                "metadata": {"description": "Test business"},
            },
            {
                "source_url": "https://example2.com",
                "observed_name": "Business Two",
                "observed_domain": "example2.com",
            },
        ]
        self.provider = MockBraveSearchProvider(results=self.results)

    def test_provider_name(self):
        """Test provider name"""
        assert self.provider.name == "brave"

    @pytest.mark.asyncio
    async def test_is_available(self):
        """Test provider is available"""
        assert await self.provider.is_available()

    @pytest.mark.asyncio
    async def test_is_not_available(self):
        """Test provider is not available"""
        provider = MockBraveSearchProvider(available=False)
        assert not await provider.is_available()

    @pytest.mark.asyncio
    async def test_search(self):
        """Test search returns candidates"""
        query = QueryBuilder().add_term("test").build()
        result = await self.provider.search(query)

        assert result.success
        assert len(result.candidates) == 2
        assert result.provider == "brave"

    @pytest.mark.asyncio
    async def test_search_candidate_fields(self):
        """Test search result candidate fields"""
        query = QueryBuilder().add_term("test").build()
        result = await self.provider.search(query)

        candidate = result.candidates[0]
        assert candidate.source == "brave"
        assert candidate.observed_name == "Business One"
        assert candidate.observed_domain == "example1.com"

    @pytest.mark.asyncio
    async def test_search_with_persian(self):
        """Test search with Persian results"""
        persian_results = [
            {
                "source_url": "https://example.com",
                "observed_name": "شرکت تست",
                "observed_domain": "example.com",
            },
        ]
        provider = MockBraveSearchProvider(results=persian_results)
        query = QueryBuilder().add_term("شرکت").build()
        result = await provider.search(query)

        assert result.success
        assert result.candidates[0].observed_name == "شرکت تست"

    @pytest.mark.asyncio
    async def test_search_count(self):
        """Test search count tracking"""
        query = QueryBuilder().add_term("test").build()

        await self.provider.search(query)
        await self.provider.search(query)

        assert self.provider.get_search_count() == 2

    @pytest.mark.asyncio
    async def test_get_health(self):
        """Test getting health"""
        health = await self.provider.get_health()
        assert health.status.value == "healthy"

    @pytest.mark.asyncio
    async def test_search_unavailable(self):
        """Test search when provider unavailable"""
        provider = MockBraveSearchProvider(available=False)
        query = QueryBuilder().add_term("test").build()
        result = await provider.search(query)

        assert not result.success
        assert len(result.candidates) == 0


class TestBraveProviderContract:
    """Test that Brave provider follows the contract"""

    def test_provider_has_name(self):
        """Test provider has name property"""
        provider = MockBraveSearchProvider()
        assert provider.name == "brave"

    def test_provider_has_supported_operators(self):
        """Test provider has supported_operators property"""
        provider = MockBraveSearchProvider()
        operators = provider.supported_operators
        assert isinstance(operators, list)
        assert "site:" in operators

    @pytest.mark.asyncio
    async def test_provider_search_returns_result(self):
        """Test provider.search() returns SearchResult"""
        provider = MockBraveSearchProvider()
        query = QueryBuilder().add_term("test").build()

        result = await provider.search(query)

        from leedhunter.application.search.provider import SearchResult

        assert isinstance(result, SearchResult)
        assert result.provider == "brave"
        assert isinstance(result.candidates, list)

    @pytest.mark.asyncio
    async def test_provider_is_available(self):
        """Test provider.is_available() returns bool"""
        provider = MockBraveSearchProvider()
        available = await provider.is_available()
        assert isinstance(available, bool)

    @pytest.mark.asyncio
    async def test_provider_get_health(self):
        """Test provider.get_health() returns ProviderHealth"""
        provider = MockBraveSearchProvider()
        health = await provider.get_health()

        from leedhunter.application.search.provider import ProviderHealth

        assert isinstance(health, ProviderHealth)


# Manual smoke test documentation
"""
Manual Smoke Test for Brave Search Provider:

1. Get a Brave Search API key from https://brave.com/search/api/

2. Set the environment variable:
   export LEEDHUNTER_SEARCH_BRAVE_API_KEY=your_api_key_here

3. Run a search:
   leedhunter search "auto importers Tehran" --provider brave

4. Run a research job:
   leedhunter hunt "Find restaurants in Tehran" --provider brave --verbose

5. Check the output:
   - Should return real web results
   - Should have source="brave" in candidates
   - Should include metadata like title and description

6. Test error handling:
   - Invalid API key should show clear error
   - Network issues should retry automatically
"""
