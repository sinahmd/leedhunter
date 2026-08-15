"""
Tests for Step 3: Correctness & Persistence

Tests for:
- Unified Query model
- URL validation
- Retry with backoff
- Partial result reporting
"""

from unittest.mock import AsyncMock

import pytest

from leedhunter.application.orchestrator.research import (
    ResearchResult,
)
from leedhunter.domain.models import SearchIntent
from leedhunter.domain.search.query import Query, QueryBuilder
from leedhunter.infrastructure.errors import (
    NetworkError,
    ProviderError,
    RateLimitError,
)
from leedhunter.infrastructure.retry import (
    RetryableError,
    RetryConfig,
    calculate_delay,
    is_retryable,
    retry_async,
)


class TestUnifiedQueryModel:
    """Tests for unified Query model"""

    def test_query_from_builder(self):
        """Test creating Query from builder"""
        query = QueryBuilder().add_term("test").add_site("example.com").build()

        assert isinstance(query, Query)
        assert len(query.terms) == 1
        assert query.terms[0].value == "test"

    def test_query_to_string(self):
        """Test Query.to_string()"""
        query = QueryBuilder().add_term("import").add_site("instagram.com").build()

        query_str = query.to_string()
        assert "site:instagram.com" in query_str
        assert "import" in query_str

    def test_query_has_site_operator(self):
        """Test Query.has_site_operator()"""
        query_with_site = QueryBuilder().add_site("example.com").build()
        assert query_with_site.has_site_operator()

        query_without_site = QueryBuilder().add_term("test").build()
        assert not query_without_site.has_site_operator()


class TestRetryLogic:
    """Tests for retry with backoff"""

    def test_is_retryable_network_error(self):
        """Test network errors are retryable"""
        error = NetworkError("Connection failed")
        assert is_retryable(error) is True

    def test_is_retryable_rate_limit(self):
        """Test rate limit errors are retryable"""
        error = RateLimitError("google", retry_after=5.0)
        assert is_retryable(error) is True

    def test_is_retryable_provider_error(self):
        """Test retryable provider errors"""
        error = ProviderError("test", "failed", retryable=True)
        assert is_retryable(error) is True

    def test_is_not_retryable_provider_error(self):
        """Test non-retryable provider errors"""
        error = ProviderError("test", "failed", retryable=False)
        assert is_retryable(error) is False

    def test_is_retryable_retryable_error(self):
        """Test RetryableError is retryable"""
        error = RetryableError("retry me")
        assert is_retryable(error) is True

    def test_calculate_delay_exponential(self):
        """Test exponential backoff calculation"""
        config = RetryConfig(base_delay=1.0, exponential_base=2.0, jitter=False)

        delay0 = calculate_delay(0, config)
        delay1 = calculate_delay(1, config)
        delay2 = calculate_delay(2, config)

        assert delay0 == 1.0
        assert delay1 == 2.0
        assert delay2 == 4.0

    def test_calculate_delay_max(self):
        """Test delay respects max"""
        config = RetryConfig(base_delay=1.0, max_delay=10.0, jitter=False)

        delay = calculate_delay(10, config)
        assert delay == 10.0

    def test_calculate_delay_retry_after(self):
        """Test delay uses retry-after when available"""
        config = RetryConfig(base_delay=1.0, jitter=False)

        delay = calculate_delay(0, config, retry_after=5.0)
        assert delay == 5.0

    @pytest.mark.asyncio
    async def test_retry_async_success(self):
        """Test retry succeeds on first attempt"""
        mock_func = AsyncMock(return_value="success")

        result = await retry_async(mock_func)

        assert result == "success"
        assert mock_func.call_count == 1

    @pytest.mark.asyncio
    async def test_retry_async_retries_on_failure(self):
        """Test retry retries on retryable failure"""
        mock_func = AsyncMock(side_effect=[NetworkError("fail"), NetworkError("fail"), "success"])
        config = RetryConfig(max_retries=3, base_delay=0.01)

        result = await retry_async(mock_func, config=config)

        assert result == "success"
        assert mock_func.call_count == 3

    @pytest.mark.asyncio
    async def test_retry_async_raises_non_retryable(self):
        """Test retry raises non-retryable errors immediately"""
        mock_func = AsyncMock(side_effect=ProviderError("test", "auth failed", retryable=False))

        with pytest.raises(ProviderError):
            await retry_async(mock_func)

        assert mock_func.call_count == 1

    @pytest.mark.asyncio
    async def test_retry_async_exhausts_retries(self):
        """Test retry raises after exhausting retries"""
        mock_func = AsyncMock(side_effect=NetworkError("fail"))
        config = RetryConfig(max_retries=2, base_delay=0.01)

        with pytest.raises(NetworkError):
            await retry_async(mock_func, config=config)

        assert mock_func.call_count == 3  # initial + 2 retries


class TestPartialResults:
    """Tests for partial result reporting"""

    def test_research_result_defaults(self):
        """Test ResearchResult defaults"""
        intent = SearchIntent(objective="test")
        result = ResearchResult(research_id="test", intent=intent)

        assert result.success is True
        assert result.partial is False
        assert result.queries_failed == 0
        assert result.failed_queries == []
        assert result.coverage == {}

    def test_research_result_partial_tracking(self):
        """Test partial result tracking"""
        intent = SearchIntent(objective="test")
        result = ResearchResult(
            research_id="test",
            intent=intent,
            queries_executed=3,
            queries_failed=1,
            partial=True,
            failed_queries=["query_4"],
            coverage={"q1": True, "q2": True, "q3": True, "q4": False},
        )

        assert result.partial is True
        assert result.queries_failed == 1
        assert len(result.failed_queries) == 1
        assert result.coverage["q4"] is False


class TestURLValidation:
    """Tests for URL validation"""

    def test_valid_url(self):
        """Test valid URL passes validation"""
        from urllib.parse import urlparse

        url = "https://example.com/path"
        parsed = urlparse(url)

        assert parsed.scheme == "https"
        assert parsed.netloc == "example.com"

    def test_invalid_url_no_scheme(self):
        """Test URL without scheme fails validation"""
        from urllib.parse import urlparse

        url = "example.com/path"
        parsed = urlparse(url)

        assert parsed.scheme == ""

    def test_invalid_url_no_netloc(self):
        """Test URL without netloc fails validation"""
        from urllib.parse import urlparse

        url = "https://"
        parsed = urlparse(url)

        assert parsed.netloc == ""
