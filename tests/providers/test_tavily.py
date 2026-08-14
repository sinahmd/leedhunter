"""
Tests for Tavily Search Provider

These tests use MockTavilySearchProvider to avoid requiring a real API key.
"""

import pytest
from pathlib import Path

from leedhunter.application.search.providers.tavily import (
    TavilySearchProvider,
    TavilyConfig,
    MockTavilySearchProvider,
)
from leedhunter.domain.search.query import Query, QueryBuilder


class TestTavilyConfig:
    """Tests for TavilyConfig"""

    def test_config_creation(self):
        """Test creating TavilyConfig"""
        config = TavilyConfig(api_key="test-key")

        assert config.api_key == "test-key"
        assert config.endpoint == "https://api.tavily.com/search"
        assert config.max_results == 10
        assert config.search_depth == "basic"

    def test_config_custom_values(self):
        """Test custom configuration"""
        config = TavilyConfig(
            api_key="test-key",
            max_results=20,
            search_depth="advanced",
            include_answer=True,
        )

        assert config.max_results == 20
        assert config.search_depth == "advanced"
        assert config.include_answer is True

    def test_config_domain_filters(self):
        """Test domain include/exclude filters"""
        config = TavilyConfig(
            api_key="test-key",
            include_domains=["example.com"],
            exclude_domains=["spam.com"],
        )

        assert "example.com" in config.include_domains
        assert "spam.com" in config.exclude_domains


class TestTavilySearchProvider:
    """Tests for TavilySearchProvider (requires API key)"""

    def test_provider_requires_api_key(self):
        """Test that provider requires API key"""
        with pytest.raises(ValueError, match="API key is required"):
            TavilySearchProvider(TavilyConfig(api_key=""))

    def test_provider_name(self):
        """Test provider name"""
        provider = TavilySearchProvider(TavilyConfig(api_key="test-key"))
        assert provider.name == "tavily"

    def test_provider_supported_operators(self):
        """Test supported operators"""
        provider = TavilySearchProvider(TavilyConfig(api_key="test-key"))
        operators = provider.supported_operators
        assert "site:" in operators
        assert "intitle:" in operators
        assert "inurl:" in operators


class TestMockTavilySearchProvider:
    """Tests for MockTavilySearchProvider"""

    def setup_method(self):
        """Set up test fixtures"""
        self.results = [
            {
                "source_url": "https://example1.com",
                "observed_name": "Business One",
                "observed_domain": "example1.com",
                "metadata": {"content": "Test business description"},
            },
            {
                "source_url": "https://example2.com",
                "observed_name": "Business Two",
                "observed_domain": "example2.com",
                "metadata": {"content": "Another business"},
            },
        ]
        self.provider = MockTavilySearchProvider(results=self.results)

    def test_provider_name(self):
        """Test provider name"""
        assert self.provider.name == "tavily"

    @pytest.mark.asyncio
    async def test_is_available(self):
        """Test provider is available"""
        assert await self.provider.is_available()

    @pytest.mark.asyncio
    async def test_is_not_available(self):
        """Test provider is not available"""
        provider = MockTavilySearchProvider(available=False)
        assert not await provider.is_available()

    @pytest.mark.asyncio
    async def test_search(self):
        """Test search returns candidates"""
        query = QueryBuilder().add_term("test").build()
        result = await self.provider.search(query)

        assert result.success
        assert len(result.candidates) == 2
        assert result.provider == "tavily"

    @pytest.mark.asyncio
    async def test_search_candidate_fields(self):
        """Test search result candidate fields"""
        query = QueryBuilder().add_term("test").build()
        result = await self.provider.search(query)

        candidate = result.candidates[0]
        assert candidate.source == "tavily"
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
        provider = MockTavilySearchProvider(results=persian_results)
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
        provider = MockTavilySearchProvider(available=False)
        query = QueryBuilder().add_term("test").build()
        result = await provider.search(query)

        assert not result.success
        assert len(result.candidates) == 0


class TestTavilyProviderContract:
    """Test that Tavily provider follows the contract"""

    def test_provider_has_name(self):
        """Test provider has name property"""
        provider = MockTavilySearchProvider()
        assert provider.name == "tavily"

    def test_provider_has_supported_operators(self):
        """Test provider has supported_operators property"""
        provider = MockTavilySearchProvider()
        operators = provider.supported_operators
        assert isinstance(operators, list)
        assert "site:" in operators

    @pytest.mark.asyncio
    async def test_provider_search_returns_result(self):
        """Test provider.search() returns SearchResult"""
        provider = MockTavilySearchProvider()
        query = QueryBuilder().add_term("test").build()

        result = await provider.search(query)

        from leedhunter.application.search.provider import SearchResult
        assert isinstance(result, SearchResult)
        assert result.provider == "tavily"
        assert isinstance(result.candidates, list)

    @pytest.mark.asyncio
    async def test_provider_is_available(self):
        """Test provider.is_available() returns bool"""
        provider = MockTavilySearchProvider()
        available = await provider.is_available()
        assert isinstance(available, bool)

    @pytest.mark.asyncio
    async def test_provider_get_health(self):
        """Test provider.get_health() returns ProviderHealth"""
        provider = MockTavilySearchProvider()
        health = await provider.get_health()

        from leedhunter.application.search.provider import ProviderHealth
        assert isinstance(health, ProviderHealth)


# Manual smoke test documentation
"""
Manual Smoke Test for Tavily Search Provider:

1. Get a Tavily API key from https://tavily.com/
   - Free tier available: 1,000 searches/month
   - No payment method required for testing

2. Set the environment variable:
   export LEEDHUNTER_SEARCH_TAVILY_API_KEY=your_api_key_here

3. Run a search:
   leedhunter search "auto importers Tehran" --provider tavily

4. Run a research job:
   leedhunter hunt "Find restaurants in Tehran" --provider tavily --verbose

5. Check the output:
   - Should return real web results
   - Should have source="tavily" in candidates
   - Should include metadata like title, content, and score

6. Test error handling:
   - Invalid API key should show clear error
   - Network issues should retry automatically
   - Rate limits should be handled gracefully

7. Verify partial results:
   - If some queries fail, others should still succeed
   - Check that failed_queries and coverage are populated
"""
