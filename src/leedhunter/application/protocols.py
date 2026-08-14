"""
Application protocols (interfaces)

These protocols define the contracts that infrastructure implementations must fulfill.
They enable dependency inversion and testability.
"""

from typing import Any, Protocol, runtime_checkable

from leedhunter.domain.models import Candidate
from leedhunter.domain.search.query import Query


@runtime_checkable
class SearchProvider(Protocol):
    """Interface for search providers (Google, Bing, etc.)"""

    async def search(self, query: Query) -> list[Candidate]:
        """Execute a search query and return candidates"""
        ...

    async def is_available(self) -> bool:
        """Check if the provider is currently available"""
        ...


@runtime_checkable
class LLMProvider(Protocol):
    """Interface for LLM providers"""

    async def analyze_intent(self, text: str) -> dict[str, Any]:
        """Analyze user intent from text"""
        ...

    async def extract_entities(self, text: str) -> dict[str, Any]:
        """Extract entity information from text"""
        ...

    async def compare_entities(
        self, entity_a: dict[str, Any], entity_b: dict[str, Any]
    ) -> dict[str, Any]:
        """Compare two entities for potential matching"""
        ...


@runtime_checkable
class PageFetcher(Protocol):
    """Interface for fetching web pages"""

    async def fetch(self, url: str) -> str:
        """Fetch a web page and return its content"""
        ...

    async def is_available(self) -> bool:
        """Check if the fetcher is currently available"""
        ...


@runtime_checkable
class Repository(Protocol):
    """Interface for data persistence"""

    async def save_entity(self, entity: Any) -> str:
        """Save an entity and return its ID"""
        ...

    async def get_entity(self, entity_id: str) -> Any | None:
        """Retrieve an entity by ID"""
        ...

    async def find_entity_by_identity(
        self, identity_type: str, normalized_value: str
    ) -> Any | None:
        """Find an entity by identity"""
        ...


@runtime_checkable
class CredentialStore(Protocol):
    """Interface for secure credential storage"""

    async def get(self, key: str) -> str | None:
        """Get a credential by key"""
        ...

    async def set(self, key: str, value: str) -> None:
        """Store a credential"""
        ...

    async def delete(self, key: str) -> None:
        """Delete a credential"""
        ...
