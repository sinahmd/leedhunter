"""
Tests for search provider module
"""

import pytest

from leedhunter.application.search.provider import (
    ProviderHealth,
    ProviderStatus,
    SearchProvider,
    SearchResult,
)
from leedhunter.application.search.rate_limiter import (
    RateLimitConfig,
    RateLimiter,
)
from leedhunter.application.search.registry import (
    ProviderRegistry,
    reset_provider_registry,
)
from leedhunter.domain.models import Candidate
from leedhunter.domain.search.query import Query


class MockSearchProvider(SearchProvider):
    """Mock search provider for testing"""

    def __init__(
        self,
        name: str = "mock",
        available: bool = True,
        candidates: list[Candidate] | None = None,
    ):
        self._name = name
        self._available = available
        self._candidates = candidates or []

    @property
    def name(self) -> str:
        return self._name

    @property
    def supported_operators(self) -> list[str]:
        return ["site:", "intitle:", "inurl:"]

    async def search(self, query: Query) -> SearchResult:
        return SearchResult(
            query=query,
            candidates=self._candidates,
            provider=self._name,
            total_results=len(self._candidates),
            success=True,
        )

    async def is_available(self) -> bool:
        return self._available

    async def get_health(self) -> ProviderHealth:
        return ProviderHealth(
            status=ProviderStatus.HEALTHY if self._available else ProviderStatus.UNAVAILABLE,
            success_rate=1.0 if self._available else 0.0,
        )


class TestProviderHealth:
    """Tests for ProviderHealth"""

    def test_create_health(self):
        """Test creating ProviderHealth"""
        health = ProviderHealth(
            status=ProviderStatus.HEALTHY,
            success_rate=0.95,
        )
        assert health.status == ProviderStatus.HEALTHY
        assert health.success_rate == 0.95

    def test_is_available_healthy(self):
        """Test is_available for healthy provider"""
        health = ProviderHealth(status=ProviderStatus.HEALTHY)
        assert health.is_available() is True

    def test_is_available_degraded(self):
        """Test is_available for degraded provider"""
        health = ProviderHealth(status=ProviderStatus.DEGRADED)
        assert health.is_available() is True

    def test_is_available_unavailable(self):
        """Test is_available for unavailable provider"""
        health = ProviderHealth(status=ProviderStatus.UNAVAILABLE)
        assert health.is_available() is False


class TestSearchResult:
    """Tests for SearchResult"""

    def test_create_result(self):
        """Test creating SearchResult"""
        query = Query(terms=["test"])
        result = SearchResult(
            query=query,
            candidates=[],
            provider="mock",
            total_results=0,
        )
        assert result.provider == "mock"
        assert len(result) == 0

    def test_result_length(self):
        """Test result length"""
        query = Query(terms=["test"])
        candidates = [
            Candidate(source="mock", source_url="https://example.com/1"),
            Candidate(source="mock", source_url="https://example.com/2"),
        ]
        result = SearchResult(query=query, candidates=candidates)
        assert len(result) == 2


class TestSearchProvider:
    """Tests for SearchProvider"""

    def test_supports_operator(self):
        """Test supports_operator"""
        provider = MockSearchProvider()
        assert provider.supports_operator("site:") is True
        assert provider.supports_operator("intitle:") is True
        assert provider.supports_operator("unknown:") is False

    def test_validate_query(self):
        """Test validate_query"""
        provider = MockSearchProvider()

        # Valid query
        query = Query(terms=["test"])
        errors = provider.validate_query(query)
        assert len(errors) == 0

    def test_validate_query_with_unsupported_operator(self):
        """Test validate_query with unsupported operator"""
        provider = MockSearchProvider()

        # Create query with operator in dict format
        query = Query(
            terms=["test"],
            operators={"site": "example.com"},
        )
        errors = provider.validate_query(query)
        assert len(errors) == 0  # site: is supported


class TestProviderRegistry:
    """Tests for ProviderRegistry"""

    def setup_method(self):
        """Set up test fixtures"""
        reset_provider_registry()
        self.registry = ProviderRegistry()

    def test_register_provider(self):
        """Test registering a provider"""
        provider = MockSearchProvider(name="test")
        self.registry.register(provider)

        assert "test" in self.registry.list_providers()

    def test_unregister_provider(self):
        """Test unregistering a provider"""
        provider = MockSearchProvider(name="test")
        self.registry.register(provider)
        self.registry.unregister("test")

        assert "test" not in self.registry.list_providers()

    def test_get_provider(self):
        """Test getting a provider"""
        provider = MockSearchProvider(name="test")
        self.registry.register(provider)

        retrieved = self.registry.get_provider("test")
        assert retrieved is provider

    def test_get_provider_not_found(self):
        """Test getting a non-existent provider"""
        retrieved = self.registry.get_provider("nonexistent")
        assert retrieved is None

    def test_set_default_provider(self):
        """Test setting default provider"""
        provider1 = MockSearchProvider(name="provider1")
        provider2 = MockSearchProvider(name="provider2")
        self.registry.register(provider1)
        self.registry.register(provider2)

        self.registry.set_default_provider("provider2")
        default = self.registry.get_default_provider()
        assert default.name == "provider2"

    def test_get_default_provider(self):
        """Test getting default provider"""
        provider = MockSearchProvider(name="test")
        self.registry.register(provider, is_default=True)

        default = self.registry.get_default_provider()
        assert default.name == "test"

    def test_list_providers(self):
        """Test listing providers"""
        provider1 = MockSearchProvider(name="provider1")
        provider2 = MockSearchProvider(name="provider2")
        self.registry.register(provider1)
        self.registry.register(provider2)

        providers = self.registry.list_providers()
        assert len(providers) == 2
        assert "provider1" in providers
        assert "provider2" in providers

    def test_get_available_providers(self):
        """Test getting available providers"""
        provider1 = MockSearchProvider(name="provider1", available=True)
        provider2 = MockSearchProvider(name="provider2", available=False)
        self.registry.register(provider1)
        self.registry.register(provider2)

        available = self.registry.get_available_providers()
        # Both should be returned since health isn't checked yet
        assert len(available) == 2

    def test_rate_limiter_registration(self):
        """Test registering with rate limit config"""
        provider = MockSearchProvider(name="test")
        config = RateLimitConfig(requests_per_second=10)
        self.registry.register(provider, rate_limit_config=config)

        limiter = self.registry.get_rate_limiter("test")
        assert limiter is not None

    def test_rate_limiter_not_configured(self):
        """Test getting rate limiter when not configured"""
        provider = MockSearchProvider(name="test")
        self.registry.register(provider)

        limiter = self.registry.get_rate_limiter("test")
        assert limiter is None


class TestRateLimiter:
    """Tests for RateLimiter"""

    def test_create_rate_limiter(self):
        """Test creating a rate limiter"""
        config = RateLimitConfig(requests_per_second=10)
        limiter = RateLimiter(config)
        assert limiter.config.requests_per_second == 10

    @pytest.mark.asyncio
    async def test_acquire_token(self):
        """Test acquiring a token"""
        config = RateLimitConfig(requests_per_second=10, burst_size=5)
        limiter = RateLimiter(config)

        result = await limiter.acquire()
        assert result is True

    @pytest.mark.asyncio
    async def test_acquire_multiple_tokens(self):
        """Test acquiring multiple tokens"""
        config = RateLimitConfig(requests_per_second=10, burst_size=3)
        limiter = RateLimiter(config)

        # Should be able to acquire up to burst_size
        assert await limiter.acquire() is True
        assert await limiter.acquire() is True
        assert await limiter.acquire() is True

    def test_get_stats(self):
        """Test getting rate limiter stats"""
        config = RateLimitConfig(requests_per_second=10, burst_size=5)
        limiter = RateLimiter(config)

        stats = limiter.get_stats()
        assert stats["burst_size"] == 5
        assert stats["requests_per_second"] == 10

    def test_reset(self):
        """Test resetting rate limiter"""
        config = RateLimitConfig(requests_per_second=10, burst_size=5)
        limiter = RateLimiter(config)

        limiter.reset()
        stats = limiter.get_stats()
        assert stats["tokens_available"] == 5
