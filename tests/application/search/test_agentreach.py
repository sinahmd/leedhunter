"""
Tests for Agent-Reach adapter
"""

import pytest

from leedhunter.application.search.providers.agentreach import (
    AgentReachConfig,
    AgentReachProvider,
    MockAgentReachProvider,
)
from leedhunter.domain.models import SearchQuery


class TestAgentReachConfig:
    """Tests for AgentReachConfig"""

    def test_default_config(self):
        """Test default configuration"""
        config = AgentReachConfig()
        assert config.base_url == "https://api.agentreach.com"
        assert config.timeout == 30.0

    def test_custom_config(self):
        """Test custom configuration"""
        config = AgentReachConfig(
            api_key="test-key",
            base_url="https://custom.api.com",
            timeout=60.0,
        )
        assert config.api_key == "test-key"
        assert config.base_url == "https://custom.api.com"


class TestAgentReachProvider:
    """Tests for AgentReachProvider"""

    def test_provider_name(self):
        """Test provider name"""
        config = AgentReachConfig(api_key="test")
        provider = AgentReachProvider(config)
        assert provider.name == "agentreach"

    def test_supported_operators(self):
        """Test supported operators"""
        config = AgentReachConfig(api_key="test")
        provider = AgentReachProvider(config)
        assert "site:" in provider.supported_operators

    @pytest.mark.asyncio
    async def test_not_available_without_api_key(self):
        """Test not available without API key"""
        config = AgentReachConfig(api_key="")
        provider = AgentReachProvider(config)
        assert not await provider.is_available()

    @pytest.mark.asyncio
    async def test_search_not_implemented(self):
        """Test that search raises NotImplementedError"""
        config = AgentReachConfig(api_key="test")
        provider = AgentReachProvider(config)
        query = SearchQuery(terms=["test"])

        with pytest.raises(NotImplementedError):
            await provider.search(query)


class TestMockAgentReachProvider:
    """Tests for MockAgentReachProvider"""

    def setup_method(self):
        """Set up test fixtures"""
        self.results = [
            {
                "source_url": "https://instagram.com/test_biz",
                "observed_name": "Test Business",
                "observed_username": "test_biz",
                "observed_phone": "+98 912 123 4567",
                "metadata": {"platform": "instagram"},
            },
            {
                "source_url": "https://test-biz.com",
                "observed_name": "Test Business",
                "observed_domain": "test-biz.com",
                "observed_email": "info@test-biz.com",
                "metadata": {"platform": "website"},
            },
        ]
        self.provider = MockAgentReachProvider(results=self.results)

    def test_provider_name(self):
        """Test provider name"""
        assert self.provider.name == "agentreach"

    @pytest.mark.asyncio
    async def test_is_available(self):
        """Test provider is available"""
        assert await self.provider.is_available()

    @pytest.mark.asyncio
    async def test_is_not_available(self):
        """Test provider is not available"""
        provider = MockAgentReachProvider(available=False)
        assert not await provider.is_available()

    @pytest.mark.asyncio
    async def test_search(self):
        """Test search returns candidates"""
        query = SearchQuery(terms=["test"])
        result = await self.provider.search(query)

        assert result.success
        assert len(result.candidates) == 2
        assert result.provider == "agentreach"

    @pytest.mark.asyncio
    async def test_search_candidate_fields(self):
        """Test search result candidate fields"""
        query = SearchQuery(terms=["test"])
        result = await self.provider.search(query)

        candidate = result.candidates[0]
        assert candidate.source == "agentreach"
        assert candidate.observed_name == "Test Business"

    @pytest.mark.asyncio
    async def test_search_unavailable(self):
        """Test search when provider unavailable"""
        provider = MockAgentReachProvider(available=False)
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
    async def test_get_health_unavailable(self):
        """Test getting health when unavailable"""
        provider = MockAgentReachProvider(available=False)
        health = await provider.get_health()
        assert health.status.value == "unavailable"

    @pytest.mark.asyncio
    async def test_search_with_persian_results(self):
        """Test search with Persian results"""
        persian_results = [
            {
                "source_url": "https://instagram.com/test",
                "observed_name": "شرکت تست",
                "observed_username": "test_biz",
                "metadata": {"platform": "instagram"},
            },
        ]
        provider = MockAgentReachProvider(results=persian_results)
        query = SearchQuery(terms=["شرکت"])
        result = await provider.search(query)

        assert result.success
        assert result.candidates[0].observed_name == "شرکت تست"

    def test_architecture_independence(self):
        """Test that Agent-Reach is behind provider interface"""
        from leedhunter.application.search.provider import SearchProvider

        provider = MockAgentReachProvider()
        assert isinstance(provider, SearchProvider)
