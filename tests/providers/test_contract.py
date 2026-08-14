"""
Provider contract tests

These tests verify that all search providers implement the interface correctly.
"""

import pytest
from typing import Optional

from leedhunter.application.search.provider import (
    SearchProvider,
    SearchResult,
    ProviderHealth,
    ProviderStatus,
)
from leedhunter.domain.search.query import Query, QueryBuilder
from leedhunter.domain.models import Candidate


class MockSearchProvider(SearchProvider):
    """Mock provider for testing"""

    def __init__(
        self,
        name: str = "mock",
        available: bool = True,
        candidates: Optional[list[Candidate]] = None,
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
            success=self._available,
        )

    async def is_available(self) -> bool:
        return self._available

    async def get_health(self) -> ProviderHealth:
        return ProviderHealth(
            status=ProviderStatus.HEALTHY if self._available else ProviderStatus.UNAVAILABLE,
        )


class TestProviderContract:
    """Test that providers implement the interface correctly"""

    def test_provider_has_name(self):
        """Test provider has name property"""
        provider = MockSearchProvider()
        assert provider.name == "mock"

    def test_provider_has_supported_operators(self):
        """Test provider has supported_operators property"""
        provider = MockSearchProvider()
        operators = provider.supported_operators
        assert isinstance(operators, list)
        assert "site:" in operators

    @pytest.mark.asyncio
    async def test_provider_search_returns_result(self):
        """Test provider.search() returns SearchResult"""
        provider = MockSearchProvider()
        query = QueryBuilder().add_term("test").build()

        result = await provider.search(query)

        assert isinstance(result, SearchResult)
        assert result.provider == "mock"
        assert isinstance(result.candidates, list)

    @pytest.mark.asyncio
    async def test_provider_is_available(self):
        """Test provider.is_available() returns bool"""
        provider = MockSearchProvider()
        available = await provider.is_available()
        assert isinstance(available, bool)

    @pytest.mark.asyncio
    async def test_provider_get_health(self):
        """Test provider.get_health() returns ProviderHealth"""
        provider = MockSearchProvider()
        health = await provider.get_health()
        assert isinstance(health, ProviderHealth)
        assert health.status in [
            ProviderStatus.HEALTHY,
            ProviderStatus.DEGRADED,
            ProviderStatus.UNAVAILABLE,
            ProviderStatus.UNKNOWN,
        ]

    def test_provider_supports_operator(self):
        """Test provider.supports_operator()"""
        provider = MockSearchProvider()
        assert provider.supports_operator("site:") is True
        assert provider.supports_operator("unknown:") is False

    @pytest.mark.asyncio
    async def test_provider_search_with_persian(self):
        """Test provider handles Persian text"""
        provider = MockSearchProvider()
        query = QueryBuilder().add_term("واردات خودرو").build()

        result = await provider.search(query)

        assert isinstance(result, SearchResult)

    @pytest.mark.asyncio
    async def test_provider_unavailable(self):
        """Test provider handles unavailability"""
        provider = MockSearchProvider(available=False)
        query = QueryBuilder().add_term("test").build()

        result = await provider.search(query)

        assert result.success is False

    @pytest.mark.asyncio
    async def test_provider_empty_query(self):
        """Test provider handles empty query"""
        provider = MockSearchProvider()
        query = Query()

        result = await provider.search(query)

        assert isinstance(result, SearchResult)


class TestSearchResultContract:
    """Test SearchResult structure"""

    def test_result_has_query(self):
        """Test result has query"""
        query = QueryBuilder().add_term("test").build()
        result = SearchResult(
            query=query,
            candidates=[],
            provider="test",
        )
        assert result.query == query

    def test_result_has_candidates(self):
        """Test result has candidates list"""
        query = QueryBuilder().add_term("test").build()
        result = SearchResult(
            query=query,
            candidates=[],
            provider="test",
        )
        assert isinstance(result.candidates, list)

    def test_result_has_provider(self):
        """Test result has provider name"""
        query = QueryBuilder().add_term("test").build()
        result = SearchResult(
            query=query,
            candidates=[],
            provider="test",
        )
        assert result.provider == "test"

    def test_result_has_success(self):
        """Test result has success flag"""
        query = QueryBuilder().add_term("test").build()
        result = SearchResult(
            query=query,
            candidates=[],
            provider="test",
            success=True,
        )
        assert result.success is True

    def test_result_has_total_results(self):
        """Test result has total_results"""
        query = QueryBuilder().add_term("test").build()
        result = SearchResult(
            query=query,
            candidates=[],
            provider="test",
            total_results=0,
        )
        assert result.total_results == 0


class TestCandidateContract:
    """Test Candidate structure"""

    def test_candidate_has_source(self):
        """Test candidate has source"""
        candidate = Candidate(
            source="test",
            source_url="https://example.com",
        )
        assert candidate.source == "test"

    def test_candidate_has_source_url(self):
        """Test candidate has source_url"""
        candidate = Candidate(
            source="test",
            source_url="https://example.com",
        )
        assert candidate.source_url == "https://example.com"

    def test_candidate_has_optional_fields(self):
        """Test candidate has optional fields"""
        candidate = Candidate(
            source="test",
            source_url="https://example.com",
            observed_name="Test",
            observed_domain="example.com",
            observed_phone="+1234567890",
            observed_email="test@example.com",
        )
        assert candidate.observed_name == "Test"
        assert candidate.observed_domain == "example.com"
        assert candidate.observed_phone == "+1234567890"
        assert candidate.observed_email == "test@example.com"
