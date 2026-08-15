"""
Provider Registry

This module manages search provider registration and selection.
"""

from leedhunter.application.search.provider import (
    ProviderHealth,
    ProviderStatus,
    SearchProvider,
)
from leedhunter.application.search.rate_limiter import RateLimitConfig, RateLimiter


class ProviderRegistry:
    """
    Registry for managing search providers

    Provides:
    - Provider registration
    - Provider selection based on health and availability
    - Rate limiting integration
    """

    def __init__(self):
        self._providers: dict[str, SearchProvider] = {}
        self._health_cache: dict[str, ProviderHealth] = {}
        self._rate_limiters: dict[str, RateLimiter] = {}
        self._default_provider: str | None = None

    def register(
        self,
        provider: SearchProvider,
        rate_limit_config: RateLimitConfig | None = None,
        is_default: bool = False,
    ) -> None:
        """
        Register a search provider

        Args:
            provider: The provider to register
            rate_limit_config: Optional rate limit configuration
            is_default: Whether this is the default provider
        """
        self._providers[provider.name] = provider

        # Set up rate limiter if config provided
        if rate_limit_config:
            self._rate_limiters[provider.name] = RateLimiter(rate_limit_config)

        # Set as default if specified or if it's the first provider
        if is_default or self._default_provider is None:
            self._default_provider = provider.name

    def unregister(self, provider_name: str) -> None:
        """
        Unregister a search provider

        Args:
            provider_name: The name of the provider to unregister
        """
        self._providers.pop(provider_name, None)
        self._health_cache.pop(provider_name, None)
        self._rate_limiters.pop(provider_name, None)

        # Reset default if this was the default
        if self._default_provider == provider_name:
            self._default_provider = next(iter(self._providers), None)

    def get_provider(self, name: str) -> SearchProvider | None:
        """
        Get a provider by name

        Args:
            name: The provider name

        Returns:
            The provider, or None if not found
        """
        return self._providers.get(name)

    def get_default_provider(self) -> SearchProvider | None:
        """
        Get the default provider

        Returns:
            The default provider, or None if no providers registered
        """
        if self._default_provider:
            return self._providers.get(self._default_provider)
        return None

    def set_default_provider(self, name: str) -> bool:
        """
        Set the default provider

        Args:
            name: The provider name

        Returns:
            True if the provider exists and was set as default
        """
        if name in self._providers:
            self._default_provider = name
            return True
        return False

    def list_providers(self) -> list[str]:
        """
        List all registered provider names

        Returns:
            List of provider names
        """
        return list(self._providers.keys())

    def get_available_providers(self) -> list[SearchProvider]:
        """
        Get all available providers

        Returns:
            List of available providers
        """
        available = []
        for provider in self._providers.values():
            health = self._health_cache.get(provider.name)
            if health is None or health.is_available():
                available.append(provider)
        return available

    async def get_provider_health(self, name: str) -> ProviderHealth | None:
        """
        Get health information for a provider

        Args:
            name: The provider name

        Returns:
            ProviderHealth, or None if provider not found
        """
        provider = self._providers.get(name)
        if not provider:
            return None

        try:
            health = await provider.get_health()
            self._health_cache[name] = health
            return health
        except Exception as e:
            # Cache failure
            health = ProviderHealth(
                status=ProviderStatus.UNAVAILABLE,
                error_message=str(e),
            )
            self._health_cache[name] = health
            return health

    async def check_all_health(self) -> dict[str, ProviderHealth]:
        """
        Check health of all providers

        Returns:
            Dictionary of provider name to health
        """
        health_map = {}
        for name in self._providers:
            health = await self.get_provider_health(name)
            if health:
                health_map[name] = health
        return health_map

    def get_rate_limiter(self, provider_name: str) -> RateLimiter | None:
        """
        Get rate limiter for a provider

        Args:
            provider_name: The provider name

        Returns:
            RateLimiter, or None if no rate limiter configured
        """
        return self._rate_limiters.get(provider_name)

    async def acquire_rate_limit(self, provider_name: str) -> bool:
        """
        Acquire rate limit for a provider

        Args:
            provider_name: The provider name

        Returns:
            True if rate limit acquired, False if rate limited
        """
        limiter = self._rate_limiters.get(provider_name)
        if limiter:
            return await limiter.acquire()
        return True

    def release_rate_limit(self, provider_name: str) -> None:
        """
        Release rate limit for a provider

        Args:
            provider_name: The provider name
        """
        limiter = self._rate_limiters.get(provider_name)
        if limiter:
            limiter.release()

    async def select_provider(
        self,
        preferred_provider: str | None = None,
    ) -> SearchProvider | None:
        """
        Select the best available provider

        Args:
            preferred_provider: Preferred provider name

        Returns:
            Selected provider, or None if no providers available
        """
        # Try preferred provider first
        if preferred_provider:
            provider = self._providers.get(preferred_provider)
            if provider:
                health = await self.get_provider_health(preferred_provider)
                if health and health.is_available():
                    return provider

        # Try default provider
        if self._default_provider:
            provider = self._providers.get(self._default_provider)
            if provider:
                health = await self.get_provider_health(self._default_provider)
                if health and health.is_available():
                    return provider

        # Try any available provider
        for provider in self._providers.values():
            health = await self.get_provider_health(provider.name)
            if health and health.is_available():
                return provider

        return None


# Global registry instance
_registry: ProviderRegistry | None = None


def get_provider_registry() -> ProviderRegistry:
    """
    Get the global provider registry

    Returns:
        The global ProviderRegistry instance
    """
    global _registry
    if _registry is None:
        _registry = ProviderRegistry()
    return _registry


def reset_provider_registry() -> None:
    """
    Reset the global provider registry

    This is primarily for testing.
    """
    global _registry
    _registry = None
