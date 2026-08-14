"""
Search provider module

This module implements the search provider interface and registry.
"""

from leedhunter.application.search.provider import (
    SearchProvider,
    SearchResult,
    ProviderStatus,
    ProviderHealth,
)

from leedhunter.application.search.registry import (
    ProviderRegistry,
    get_provider_registry,
)

from leedhunter.application.search.rate_limiter import (
    RateLimiter,
    RateLimitConfig,
)

__all__ = [
    # Provider
    "SearchProvider",
    "SearchResult",
    "ProviderStatus",
    "ProviderHealth",
    # Registry
    "ProviderRegistry",
    "get_provider_registry",
    # Rate Limiting
    "RateLimiter",
    "RateLimitConfig",
]
