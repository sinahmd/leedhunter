"""
Tavily Search Provider

This provider uses the Tavily Search API for web search.
Tavily is designed for AI/RAG workflows and returns structured results.

API Documentation: https://docs.tavily.com/
Pricing: Free tier available (1,000 searches/month)

Terms of Service: https://tavily.com/terms
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from urllib.parse import urlparse

import httpx

from leedhunter.application.search.provider import (
    ProviderHealth,
    ProviderStatus,
    SearchProvider,
    SearchResult,
)
from leedhunter.domain.models import Candidate
from leedhunter.domain.search.query import Query
from leedhunter.infrastructure.errors import (
    AuthenticationError,
    ProviderError,
    RateLimitError,
)
from leedhunter.infrastructure.retry import RetryConfig, retry_async


@dataclass
class TavilyConfig:
    """Configuration for Tavily search provider"""

    api_key: str
    endpoint: str = "https://api.tavily.com/search"
    max_results: int = 10
    timeout: float = 30.0
    search_depth: str = "basic"  # "basic" or "advanced"
    include_answer: bool = False
    include_raw_content: bool = False
    include_domains: list[str] = field(default_factory=list)
    exclude_domains: list[str] = field(default_factory=list)


class TavilySearchProvider(SearchProvider):
    """
    Tavily Search API provider.

    Uses official Tavily Search API designed for AI/RAG workflows.
    Requires API key from https://tavily.com/
    """

    def __init__(self, config: TavilyConfig):
        if not config.api_key:
            raise ValueError("Tavily API key is required")

        self._config = config
        self._health = ProviderHealth(
            status=ProviderStatus.UNKNOWN,
        )
        self._search_count = 0
        self._retry_config = RetryConfig(
            max_retries=3,
            base_delay=1.0,
            max_delay=30.0,
        )

    @property
    def name(self) -> str:
        return "tavily"

    @property
    def supported_operators(self) -> list[str]:
        return ["site:", "intitle:", "inurl:"]

    async def search(self, query: Query) -> SearchResult:
        """
        Execute search via Tavily Search API

        Args:
            query: Search query

        Returns:
            SearchResult with candidates
        """
        start_time = datetime.now(timezone.utc)
        self._search_count += 1
        query_string = query.to_string()

        try:
            response = await retry_async(
                self._execute_search,
                query_string,
                config=self._retry_config,
            )

            candidates = self._parse_results(response, query)
            end_time = datetime.now(timezone.utc)
            search_time = (end_time - start_time).total_seconds()

            self._health = ProviderHealth(
                status=ProviderStatus.HEALTHY,
                last_success=end_time,
                success_rate=1.0,
            )

            return SearchResult(
                query=query,
                candidates=candidates,
                provider=self.name,
                total_results=len(candidates),
                search_time=search_time,
                success=True,
            )

        except AuthenticationError:
            self._health = ProviderHealth(
                status=ProviderStatus.UNAVAILABLE,
                error_message="Invalid API key",
            )
            return SearchResult(
                query=query,
                candidates=[],
                provider=self.name,
                total_results=0,
                success=False,
                error_message="Invalid Tavily API key",
            )

        except RateLimitError as e:
            self._health = ProviderHealth(
                status=ProviderStatus.DEGRADED,
                error_message="Rate limited",
            )
            return SearchResult(
                query=query,
                candidates=[],
                provider=self.name,
                total_results=0,
                success=False,
                error_message=f"Rate limited: {e}",
            )

        except Exception as e:
            self._health = ProviderHealth(
                status=ProviderStatus.DEGRADED,
                error_message=str(e),
            )
            return SearchResult(
                query=query,
                candidates=[],
                provider=self.name,
                total_results=0,
                success=False,
                error_message=str(e),
            )

    async def _execute_search(self, query_string: str) -> dict:
        """
        Execute Tavily Search API call

        Args:
            query_string: Query string to search

        Returns:
            API response as dictionary
        """
        headers = {
            "Content-Type": "application/json",
        }

        payload = {
            "api_key": self._config.api_key,
            "query": query_string,
            "max_results": self._config.max_results,
            "search_depth": self._config.search_depth,
            "include_answer": self._config.include_answer,
            "include_raw_content": self._config.include_raw_content,
        }

        if self._config.include_domains:
            payload["include_domains"] = self._config.include_domains

        if self._config.exclude_domains:
            payload["exclude_domains"] = self._config.exclude_domains

        async with httpx.AsyncClient(timeout=self._config.timeout) as client:
            response = await client.post(
                self._config.endpoint,
                headers=headers,
                json=payload,
            )

            if response.status_code == 401 or response.status_code == 403:
                raise AuthenticationError("tavily", "Invalid API key")
            elif response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                raise RateLimitError(
                    "tavily",
                    retry_after=float(retry_after) if retry_after else None,
                )
            elif response.status_code != 200:
                raise ProviderError(
                    "tavily",
                    f"API error: {response.status_code}",
                    retryable=response.status_code >= 500,
                )

            return response.json()

    def _parse_results(self, response: dict, query: Query) -> list[Candidate]:
        """
        Parse Tavily API response into candidates

        Args:
            response: API response dictionary
            query: Original search query

        Returns:
            List of Candidate objects
        """
        candidates = []
        query_id = self._generate_query_id(query)
        observed_at = datetime.now(timezone.utc)

        # Get results from response
        results = response.get("results", [])

        for result in results:
            try:
                url = result.get("url", "")
                if not url:
                    continue

                parsed = urlparse(url)
                domain = parsed.netloc if parsed.netloc else None

                # Build metadata preserving raw provenance
                metadata = {
                    "title": result.get("title", ""),
                    "content": result.get("content", ""),
                    "score": result.get("score", 0.0),
                }

                # Add raw_content if available
                if "raw_content" in result and result["raw_content"]:
                    metadata["raw_content"] = result["raw_content"]

                candidate = Candidate(
                    source="tavily",
                    source_url=url,
                    observed_name=result.get("title"),
                    observed_domain=domain,
                    metadata=metadata,
                    discovered_at=observed_at,
                    query_id=query_id,
                )
                candidates.append(candidate)

            except Exception:
                continue

        return candidates

    def _generate_query_id(self, query: Query) -> str:
        """Generate a stable ID for a query"""
        content = f"{query.terms}:{query.exact_phrases}:{query.operators}"
        return f"q_{hashlib.md5(content.encode()).hexdigest()[:12]}"

    async def is_available(self) -> bool:
        """Check if provider is available"""
        return bool(self._config.api_key)

    async def get_health(self) -> ProviderHealth:
        """Get provider health"""
        return self._health


class MockTavilySearchProvider(SearchProvider):
    """
    Mock Tavily provider for testing.

    Returns configurable results without making real API calls.
    """

    def __init__(
        self,
        results: list[dict] | None = None,
        available: bool = True,
    ):
        self._results = results or []
        self._available = available
        self._search_count = 0

    @property
    def name(self) -> str:
        return "tavily"

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
                    source="tavily",
                    source_url=result.get("source_url", "https://example.com"),
                    observed_name=result.get("observed_name"),
                    observed_domain=result.get("observed_domain"),
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
