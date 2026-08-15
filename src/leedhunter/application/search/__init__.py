"""
Search provider module

This module implements the search provider interface and registry.
"""

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
    get_provider_registry,
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
