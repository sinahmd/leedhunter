"""
LLM Provider Registry

This module manages LLM provider registration and selection.
"""

from leedhunter.application.llm.provider import LLMProvider


class LLMProviderRegistry:
    """
    Registry for managing LLM providers.

    Provides provider registration, selection, and health checking.
    """

    def __init__(self):
        self._providers: dict[str, LLMProvider] = {}
        self._default_provider: str | None = None

    def register(self, provider: LLMProvider, is_default: bool = False) -> None:
        """
        Register an LLM provider

        Args:
            provider: The provider to register
            is_default: Whether this is the default provider
        """
        self._providers[provider.name] = provider

        if is_default or self._default_provider is None:
            self._default_provider = provider.name

    def unregister(self, provider_name: str) -> None:
        """
        Unregister an LLM provider

        Args:
            provider_name: The name of the provider to unregister
        """
        self._providers.pop(provider_name, None)

        if self._default_provider == provider_name:
            self._default_provider = next(iter(self._providers), None)

    def get_provider(self, name: str) -> LLMProvider | None:
        """
        Get a provider by name

        Args:
            name: The provider name

        Returns:
            The provider, or None if not found
        """
        return self._providers.get(name)

    def get_default_provider(self) -> LLMProvider | None:
        """
        Get the default provider

        Returns:
            The default provider, or None if no providers registered
        """
        if self._default_provider:
            return self._providers.get(self._default_provider)
        return None

    def list_providers(self) -> list[str]:
        """
        List all registered provider names

        Returns:
            List of provider names
        """
        return list(self._providers.keys())

    def is_available(self) -> bool:
        """
        Check if any provider is available

        Returns:
            True if at least one provider is registered
        """
        return len(self._providers) > 0


def create_llm_provider_from_config() -> LLMProvider | None:
    """
    Create an LLM provider from configuration

    Returns:
        LLMProvider if configured, None otherwise
    """
    from leedhunter.config import LLMProviderType, get_settings

    settings = get_settings()
    llm_settings = settings.llm

    # Check if LLM is enabled
    if not llm_settings.enabled:
        return None

    # Check if API key is provided
    if not llm_settings.api_key:
        return None

    # Create provider based on configuration
    if llm_settings.provider == LLMProviderType.ANTHROPIC:
        return _create_anthropic_provider(llm_settings)
    elif llm_settings.provider == LLMProviderType.OPENAI:
        return _create_openai_provider(llm_settings)
    elif llm_settings.provider == LLMProviderType.OPENAI_COMPATIBLE:
        return _create_openai_compatible_provider(llm_settings)
    else:
        return None


def _create_anthropic_provider(llm_settings) -> LLMProvider | None:
    """Create Anthropic provider"""
    try:
        from leedhunter.application.llm.providers.anthropic import (
            AnthropicConfig,
            AnthropicLLMProvider,
        )

        config = AnthropicConfig(
            api_key=llm_settings.api_key,
            model=llm_settings.model,
            max_tokens=llm_settings.max_tokens,
            temperature=llm_settings.temperature,
            timeout=llm_settings.timeout_seconds,
        )
        return AnthropicLLMProvider(config)
    except ImportError:
        return None


def _create_openai_provider(llm_settings) -> LLMProvider | None:
    """Create OpenAI provider"""
    try:
        from leedhunter.application.llm.providers.openai import OpenAIConfig, OpenAILLMProvider

        config = OpenAIConfig(
            api_key=llm_settings.api_key,
            model=llm_settings.model,
            max_tokens=llm_settings.max_tokens,
            temperature=llm_settings.temperature,
            timeout=llm_settings.timeout_seconds,
        )
        return OpenAILLMProvider(config)
    except ImportError:
        return None


def _create_openai_compatible_provider(llm_settings) -> LLMProvider | None:
    """Create OpenAI-compatible provider"""
    try:
        from leedhunter.application.llm.providers.openai import OpenAIConfig, OpenAILLMProvider

        config = OpenAIConfig(
            api_key=llm_settings.api_key,
            base_url=llm_settings.base_url,
            model=llm_settings.model,
            max_tokens=llm_settings.max_tokens,
            temperature=llm_settings.temperature,
            timeout=llm_settings.timeout_seconds,
        )
        return OpenAILLMProvider(config)
    except ImportError:
        return None
