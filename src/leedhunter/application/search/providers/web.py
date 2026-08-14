"""
Web Search Provider

This module implements HTTP-based web search providers.
It supports multiple search engines with proper error handling and rate limiting.

Provider failures must be isolated:
- Search engine unavailable does NOT mean research failed
- Multiple providers can be used as fallbacks
"""

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import quote_plus

import httpx

from leedhunter.application.search.provider import (
    SearchProvider,
    SearchResult,
    ProviderHealth,
    ProviderStatus,
)
from leedhunter.domain.models import Candidate
from leedhunter.domain.search.query import Query
from leedhunter.infrastructure.errors import (
    ProviderError,
    NetworkError,
    RateLimitError,
)


@dataclass
class WebSearchConfig:
    """Configuration for web search provider"""

    api_key: str = ""
    base_url: str = ""
    timeout: float = 30.0
    max_results: int = 10
    user_agent: str = "LeedHunter/0.1"


class WebSearchProvider(SearchProvider):
    """
    Base web search provider.

    This is a template for real web search implementations.
    Subclasses must implement the actual search API integration.
    """

    def __init__(self, config: WebSearchConfig):
        self._config = config
        self._health = ProviderHealth(
            status=ProviderStatus.UNKNOWN,
        )
        self._search_count = 0

    @property
    def name(self) -> str:
        return "web"

    @property
    def supported_operators(self) -> list[str]:
        return ["site:", "intitle:", "inurl:"]

    async def search(self, query: Query) -> SearchResult:
        """Execute web search"""
        raise NotImplementedError("Subclasses must implement search()")

    async def is_available(self) -> bool:
        """Check if provider is available"""
        return self._health.status in [
            ProviderStatus.HEALTHY,
            ProviderStatus.DEGRADED,
            ProviderStatus.UNKNOWN,
        ]

    async def get_health(self) -> ProviderHealth:
        """Get provider health"""
        return self._health

    def _build_query_string(self, query: Query) -> str:
        """Build query string from Query"""
        parts = []

        # Add operators
        for op_name, op_value in query.operators.items():
            parts.append(f"{op_name}:{op_value}")

        # Add exact phrases
        for phrase in query.exact_phrases:
            parts.append(f'"{phrase}"')

        # Add terms
        parts.extend(query.terms)

        # Add exclusions
        for exclusion in query.exclusions:
            parts.append(f"-{exclusion}")

        return " ".join(parts)


class MockWebSearchProvider(SearchProvider):
    """
    Mock web search provider for testing.

    Returns configurable results without making HTTP requests.
    """

    def __init__(
        self,
        results: Optional[list[dict]] = None,
        available: bool = True,
    ):
        self._results = results or []
        self._available = available
        self._search_count = 0

    @property
    def name(self) -> str:
        return "web"

    @property
    def supported_operators(self) -> list[str]:
        return ["site:", "intitle:", "inurl:"]

    async def search(self, query: Query) -> SearchResult:
        """Execute mock search"""
        self._search_count += 1

        if not self._available:
            return SearchResult(
                query=query,
                candidates=[],
                provider=self.name,
                total_results=0,
                success=False,
                error_message="Provider unavailable",
            )

        candidates = []
        for result in self._results:
            try:
                candidate = Candidate(
                    source="web",
                    source_url=result.get("source_url", "https://example.com"),
                    observed_name=result.get("observed_name"),
                    observed_domain=result.get("observed_domain"),
                    observed_phone=result.get("observed_phone"),
                    observed_email=result.get("observed_email"),
                    metadata=result.get("metadata", {}),
                )
                candidates.append(candidate)
            except Exception:
                continue

        return SearchResult(
            query=query,
            candidates=candidates,
            provider=self.name,
            total_results=len(candidates),
            success=True,
        )

    async def is_available(self) -> bool:
        """Check if provider is available"""
        return self._available

    async def get_health(self) -> ProviderHealth:
        """Get provider health"""
        return ProviderHealth(
            status=ProviderStatus.HEALTHY if self._available else ProviderStatus.UNAVAILABLE,
            success_rate=1.0 if self._available else 0.0,
        )

    def get_search_count(self) -> int:
        """Get search count"""
        return self._search_count
