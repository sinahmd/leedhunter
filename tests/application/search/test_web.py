"""
Tests for web search provider
"""

import pytest

from leedhunter.application.search.providers.web import (
    WebSearchConfig,
    WebSearchProvider,
    MockWebSearchProvider,
)
from leedhunter.domain.models import SearchQuery


class TestWebSearchConfig:
    """Tests for WebSearchConfig"""

    def test_default_config(self):
        """Test default configuration"""
        config = WebSearchConfig()
        assert config.timeout == 30.0
        assert config.max_results == 10

    def test_custom_config(self):
        """Test custom configuration"""
        config = WebSearchConfig(
            api_key="test-key",
            base_url="https://custom.api.com",
            timeout=60.0,
        )
        assert config.api_key == "test-key"


class TestWebSearchProvider:
    """Tests for WebSearchProvider"""

    def test_provider_name(self):
        """Test provider name"""
        config = WebSearchConfig()
        provider = WebSearchProvider(config)
        assert provider.name == "web"

    def test_supported_operators(self):
        """Test supported operators"""
        config = WebSearchConfig()
        provider = WebSearchProvider(config)
        assert "site:" in provider.supported_operators
        assert "intitle:" in provider.supported_operators

    @pytest.mark.asyncio
    async def test_search_not_implemented(self):
        """Test that search raises NotImplementedError"""
        config = WebSearchConfig()
        provider = WebSearchProvider(config)
        query = SearchQuery(terms=["test"])

        with pytest.raises(NotImplementedError):
            await provider.search(query)


class TestMockWebSearchProvider:
    """Tests for MockWebSearchProvider"""

    def setup_method(self):
        """Set up test fixtures"""
        self.results = [
            {
                "source_url": "https://example1.com",
                "observed_name": "Business One",
                "observed_domain": "example1.com",
            },
            {
                "source_url": "https://example2.com",
                "observed_name": "Business Two",
                "observed_domain": "example2.com",
                "metadata": {"location": "Tehran"},
            },
        ]
        self.provider = MockWebSearchProvider(results=self.results)

    def test_provider_name(self):
        """Test provider name"""
        assert self.provider.name == "web"

    @pytest.mark.asyncio
    async def test_is_available(self):
        """Test provider is available"""
        assert await self.provider.is_available()

    @pytest.mark.asyncio
    async def test_is_not_available(self):
        """Test provider is not available"""
        provider = MockWebSearchProvider(available=False)
        assert not await provider.is_available()

    @pytest.mark.asyncio
    async def test_search(self):
        """Test search returns candidates"""
        query = SearchQuery(terms=["business"])
        result = await self.provider.search(query)

        assert result.success
        assert len(result.candidates) == 2
        assert result.provider == "web"

    @pytest.mark.asyncio
    async def test_search_candidate_fields(self):
        """Test search result candidate fields"""
        query = SearchQuery(terms=["business"])
        result = await self.provider.search(query)

        candidate = result.candidates[0]
        assert candidate.source == "web"
        assert candidate.observed_name == "Business One"
        assert candidate.observed_domain == "example1.com"

    @pytest.mark.asyncio
    async def test_search_with_metadata(self):
        """Test search result with metadata"""
        query = SearchQuery(terms=["business"])
        result = await self.provider.search(query)

        candidate = result.candidates[1]
        assert candidate.metadata.get("location") == "Tehran"

    @pytest.mark.asyncio
    async def test_search_unavailable(self):
        """Test search when provider unavailable"""
        provider = MockWebSearchProvider(available=False)
        query = SearchQuery(terms=["test"])
        result = await provider.search(query)

        assert not result.success
        assert len(result.candidates) == 0

    @pytest.mark.asyncio
    async def test_search_count(self):
        """Test search count tracking"""
        query = SearchQuery(terms=["test"])

        await self.provider.search(query)
        await self.provider.search(query)

        assert self.provider.get_search_count() == 2

    @pytest.mark.asyncio
    async def test_get_health(self):
        """Test getting health"""
        health = await self.provider.get_health()
        assert health.status.value == "healthy"

    @pytest.mark.asyncio
    async def test_search_persian(self):
        """Test search with Persian results"""
        persian_results = [
            {
                "source_url": "https://example.com",
                "observed_name": "شرکت تست",
                "observed_domain": "example.com",
            },
        ]
        provider = MockWebSearchProvider(results=persian_results)
        query = SearchQuery(terms=["شرکت"])
        result = await provider.search(query)

        assert result.success
        assert result.candidates[0].observed_name == "شرکت تست"

    def test_architecture_independence(self):
        """Test that web search is behind provider interface"""
        from leedhunter.application.search.provider import SearchProvider

        provider = MockWebSearchProvider()
        assert isinstance(provider, SearchProvider)
