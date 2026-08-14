"""
Agent-Reach Adapter

Agent-Reach is an external integration.
It MUST be behind AgentReachProvider.
It must implement LeedHunter's provider interfaces.

If Agent-Reach disappears tomorrow:
LeedHunter architecture must remain valid.

This module provides:
- AgentReachProvider: SearchProvider implementation
- AgentReachConfig: Configuration for Agent-Reach
- MockAgentReachProvider: For testing without real API
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

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
    AuthenticationError,
    RateLimitError,
    NetworkError,
)


@dataclass
class AgentReachConfig:
    """Configuration for Agent-Reach provider"""

    api_key: str = ""
    base_url: str = "https://api.agentreach.com"
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0


class AgentReachProvider(SearchProvider):
    """
    Agent-Reach search provider implementation.

    This is a real provider that would connect to Agent-Reach API.
    For testing, use MockAgentReachProvider instead.
    """

    def __init__(self, config: AgentReachConfig):
        self._config = config
        self._health = ProviderHealth(
            status=ProviderStatus.UNKNOWN,
        )

    @property
    def name(self) -> str:
        return "agentreach"

    @property
    def supported_operators(self) -> list[str]:
        return ["site:", "intitle:", "inurl:"]

    async def search(self, query: Query) -> SearchResult:
        """
        Execute search via Agent-Reach API.

        This is a placeholder for the real implementation.
        In production, this would make HTTP requests to Agent-Reach.
        """
        # This would be a real API call in production
        raise NotImplementedError(
            "AgentReachProvider requires real API integration. "
            "Use MockAgentReachProvider for testing."
        )

    async def is_available(self) -> bool:
        """Check if Agent-Reach is available"""
        if not self._config.api_key:
            return False
        return self._health.status in [
            ProviderStatus.HEALTHY,
            ProviderStatus.DEGRADED,
            ProviderStatus.UNKNOWN,
        ]

    async def get_health(self) -> ProviderHealth:
        """Get provider health"""
        return self._health


class MockAgentReachProvider(SearchProvider):
    """
    Mock Agent-Reach provider for testing.

    Returns realistic results without making real API calls.
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
        return "agentreach"

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

        # Convert results to candidates
        candidates = []
        for result in self._results:
            try:
                candidate = Candidate(
                    source="agentreach",
                    source_url=result.get("source_url", "https://example.com"),
                    observed_name=result.get("observed_name"),
                    observed_domain=result.get("observed_domain"),
                    observed_username=result.get("observed_username"),
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
        """Get number of searches performed"""
        return self._search_count
