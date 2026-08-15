"""
Tests for LLM providers

All tests use mocked responses - no real API calls.
"""

import pytest

from leedhunter.application.llm.errors import (
    LLMAuthenticationError,
    LLMBudgetExceededError,
    LLMError,
    LLMInvalidResponseError,
    LLMProviderUnavailableError,
    LLMRateLimitError,
    LLMTimeoutError,
)
from leedhunter.application.llm.mock import MockLLMProvider
from leedhunter.application.llm.provider import LLMProvider, LLMResponse, LLMUsage
from leedhunter.application.llm.registry import LLMProviderRegistry


class TestLLMProviderProtocol:
    """Test LLMProvider protocol compliance"""

    def test_mock_provider_implements_protocol(self):
        """Test MockLLMProvider implements LLMProvider"""
        provider = MockLLMProvider()
        assert isinstance(provider, LLMProvider)

    def test_provider_has_name(self):
        """Test provider has name property"""
        provider = MockLLMProvider()
        assert provider.name == "mock"

    def test_provider_has_model(self):
        """Test provider has model property"""
        provider = MockLLMProvider()
        assert provider.model == "mock-model"

    @pytest.mark.asyncio
    async def test_provider_generate(self):
        """Test provider.generate() returns LLMResponse"""
        provider = MockLLMProvider()
        response = await provider.generate("test prompt")

        assert isinstance(response, LLMResponse)
        assert response.success is True


class TestLLMErrors:
    """Test LLM error types"""

    def test_llm_error(self):
        """Test LLMError base class"""
        error = LLMError("test error")
        assert str(error) == "test error"

    def test_authentication_error(self):
        """Test LLMAuthenticationError"""
        error = LLMAuthenticationError("anthropic", "Invalid key")
        assert error.provider == "anthropic"
        assert "anthropic" in str(error)
        assert "Invalid key" in str(error)

    def test_rate_limit_error(self):
        """Test LLMRateLimitError"""
        error = LLMRateLimitError("openai", retry_after=5.0)
        assert error.provider == "openai"
        assert error.retry_after == 5.0

    def test_timeout_error(self):
        """Test LLMTimeoutError"""
        error = LLMTimeoutError("anthropic", timeout=60.0)
        assert error.provider == "anthropic"
        assert error.timeout == 60.0

    def test_provider_unavailable_error(self):
        """Test LLMProviderUnavailableError"""
        error = LLMProviderUnavailableError("google", "Not installed")
        assert error.provider == "google"

    def test_invalid_response_error(self):
        """Test LLMInvalidResponseError"""
        error = LLMInvalidResponseError("openai", "Bad JSON")
        assert error.provider == "openai"

    def test_budget_exceeded_error(self):
        """Test LLMBudgetExceededError"""
        error = LLMBudgetExceededError("anthropic", "calls", 10)
        assert error.provider == "anthropic"
        assert error.budget_type == "calls"
        assert error.limit == 10


class TestLLMProviderRegistry:
    """Test LLM provider registry"""

    def setup_method(self):
        """Set up test fixtures"""
        self.registry = LLMProviderRegistry()

    def test_register_provider(self):
        """Test registering a provider"""
        provider = MockLLMProvider()
        self.registry.register(provider)

        assert "mock" in self.registry.list_providers()

    def test_unregister_provider(self):
        """Test unregistering a provider"""
        provider = MockLLMProvider()
        self.registry.register(provider)
        self.registry.unregister("mock")

        assert "mock" not in self.registry.list_providers()

    def test_get_provider(self):
        """Test getting a provider"""
        provider = MockLLMProvider()
        self.registry.register(provider)

        retrieved = self.registry.get_provider("mock")
        assert retrieved is provider

    def test_get_provider_not_found(self):
        """Test getting a non-existent provider"""
        retrieved = self.registry.get_provider("nonexistent")
        assert retrieved is None

    def test_set_default_provider(self):
        """Test setting default provider"""
        provider1 = MockLLMProvider()
        provider2 = MockLLMProvider()
        self.registry.register(provider1)
        self.registry.register(provider2, is_default=True)

        default = self.registry.get_default_provider()
        assert default is provider2

    def test_is_available(self):
        """Test is_available check"""
        assert self.registry.is_available() is False

        provider = MockLLMProvider()
        self.registry.register(provider)

        assert self.registry.is_available() is True


class TestMockLLMProvider:
    """Test MockLLMProvider"""

    def setup_method(self):
        """Set up test fixtures"""
        self.provider = MockLLMProvider()

    @pytest.mark.asyncio
    async def test_generate(self):
        """Test generating response"""
        response = await self.provider.generate("test prompt")

        assert response.success is True
        assert response.provider == "mock"

    @pytest.mark.asyncio
    async def test_generate_with_custom_response(self):
        """Test generating with custom responses"""
        provider = MockLLMProvider(
            responses={"hello": '{"result": "world"}'},
        )
        response = await provider.generate("hello there")

        assert response.content == '{"result": "world"}'

    @pytest.mark.asyncio
    async def test_usage_tracking(self):
        """Test usage tracking"""
        await self.provider.generate("test prompt")
        await self.provider.generate("another prompt")

        usage = self.provider.get_total_usage()
        assert usage.total_tokens > 0
        assert self.provider.get_call_count() == 2

    def test_reset(self):
        """Test resetting usage"""
        self.provider._total_usage = LLMUsage(100, 50, 150)
        self.provider._call_count = 5

        self.provider.reset()

        assert self.provider.get_call_count() == 0
        assert self.provider.get_total_usage().total_tokens == 0


class TestLLMDisabledBehavior:
    """Test that system works without LLM"""

    def test_no_llm_provider_created_when_disabled(self):
        """Test no provider created when LLM is disabled"""
        import os

        os.environ["LEEDHUNTER_LLM_ENABLED"] = "false"
        os.environ["LEEDHUNTER_LLM_API_KEY"] = ""

        from leedhunter.application.llm.registry import create_llm_provider_from_config
        from leedhunter.config import reset_settings

        reset_settings()

        provider = create_llm_provider_from_config()
        assert provider is None

    def test_no_llm_provider_created_when_no_key(self):
        """Test no provider created when API key is missing"""
        import os

        os.environ["LEEDHUNTER_LLM_ENABLED"] = "true"
        os.environ["LEEDHUNTER_LLM_API_KEY"] = ""

        from leedhunter.application.llm.registry import create_llm_provider_from_config
        from leedhunter.config import reset_settings

        reset_settings()

        provider = create_llm_provider_from_config()
        assert provider is None
