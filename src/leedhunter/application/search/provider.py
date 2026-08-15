"""
Search Provider Interface

This module defines the protocol for search providers and related types.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from leedhunter.domain.models import Candidate
from leedhunter.domain.search.query import Query


class ProviderStatus(str, Enum):
    """Status of a search provider"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


@dataclass
class ProviderHealth:
    """Health information for a provider"""

    status: ProviderStatus
    last_check: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_success: datetime | None = None
    last_failure: datetime | None = None
    error_message: str | None = None
    success_rate: float = 1.0
    average_response_time: float = 0.0

    def is_available(self) -> bool:
        """Check if provider is available"""
        return self.status in [ProviderStatus.HEALTHY, ProviderStatus.DEGRADED]


@dataclass
class SearchResult:
    """Result from a search provider"""

    query: Query
    candidates: list[Candidate] = field(default_factory=list)
    provider: str = ""
    total_results: int = 0
    search_time: float = 0.0
    success: bool = True
    error_message: str | None = None

    def __len__(self) -> int:
        return len(self.candidates)


class SearchProvider(ABC):
    """
    Abstract base class for search providers

    All search providers must implement this interface.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the provider name"""
        pass

    @property
    @abstractmethod
    def supported_operators(self) -> list[str]:
        """Get list of supported search operators"""
        pass

    @abstractmethod
    async def search(self, query: Query) -> SearchResult:
        """
        Execute a search query

        Args:
            query: The search query to execute

        Returns:
            SearchResult with candidates
        """
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """
        Check if the provider is currently available

        Returns:
            True if the provider can accept requests
        """
        pass

    @abstractmethod
    async def get_health(self) -> ProviderHealth:
        """
        Get provider health information

        Returns:
            ProviderHealth with status and metrics
        """
        pass

    def supports_operator(self, operator: str) -> bool:
        """
        Check if provider supports an operator

        Args:
            operator: The operator to check (e.g., "site:", "intitle:")

        Returns:
            True if the operator is supported
        """
        return operator in self.supported_operators

    def validate_query(self, query: Query) -> list[str]:
        """
        Validate a query for this provider

        Args:
            query: The query to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check for unsupported operators (operators is a dict)
        for op_name in query.operators:
            op_prefix = f"{op_name}:"
            if not self.supports_operator(op_prefix):
                errors.append(f"Operator {op_prefix} not supported by {self.name}")

        return errors
