"""
Anthropic LLM Provider Adapter

This module implements the LLM provider interface for Anthropic's Claude API.

Requires: pip install leedhunter[llm-anthropic]
"""

import asyncio
from dataclasses import dataclass
from typing import Any, Optional

from leedhunter.application.llm.provider import LLMProvider, LLMResponse, LLMUsage
from leedhunter.application.llm.errors import (
    LLMAuthenticationError,
    LLMRateLimitError,
    LLMTimeoutError,
    LLMProviderUnavailableError,
    LLMInvalidResponseError,
)
from leedhunter.infrastructure.retry import RetryConfig, retry_async


@dataclass
class AnthropicConfig:
    """Configuration for Anthropic provider"""

    api_key: str
    model: str = "claude-3-sonnet-20240229"
    max_tokens: int = 4096
    temperature: float = 0.2
    timeout: float = 60.0
    max_retries: int = 3


class AnthropicLLMProvider(LLMProvider):
    """
    Anthropic Claude LLM provider.

    Uses the Anthropic API for Claude models.
    """

    def __init__(self, config: AnthropicConfig):
        if not config.api_key:
            raise ValueError("Anthropic API key is required")

        self._config = config
        self._client = None
        self._total_usage = LLMUsage()
        self._call_count = 0
        self._retry_config = RetryConfig(
            max_retries=config.max_retries,
            base_delay=1.0,
            max_delay=30.0,
        )

    def _get_client(self):
        """Get or create Anthropic client"""
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.AsyncAnthropic(
                    api_key=self._config.api_key,
                    timeout=self._config.timeout,
                )
            except ImportError:
                raise LLMProviderUnavailableError(
                    "anthropic",
                    "anthropic package not installed. Install with: pip install leedhunter[llm-anthropic]"
                )
        return self._client

    @property
    def name(self) -> str:
        return "anthropic"

    @property
    def model(self) -> str:
        return self._config.model

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """
        Generate a response from Claude

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens in response
            temperature: Temperature for generation

        Returns:
            LLMResponse with generated content
        """
        self._call_count += 1

        try:
            client = self._get_client()

            # Build message
            messages = [{"role": "user", "content": prompt}]

            # Call API with retry
            response = await retry_async(
                self._call_api,
                client,
                messages,
                system_prompt,
                min(max_tokens, self._config.max_tokens),
                min(temperature, self._config.temperature),
                config=self._retry_config,
            )

            # Extract usage
            usage = LLMUsage(
                prompt_tokens=response.usage.input_tokens,
                completion_tokens=response.usage.output_tokens,
                total_tokens=response.usage.input_tokens + response.usage.output_tokens,
            )
            self._total_usage = self._total_usage + usage

            # Extract content
            content = ""
            for block in response.content:
                if hasattr(block, "text"):
                    content += block.text

            return LLMResponse(
                content=content,
                usage=usage,
                model=self._config.model,
                provider=self.name,
                success=True,
            )

        except LLMAuthenticationError:
            raise
        except LLMRateLimitError:
            raise
        except LLMTimeoutError:
            raise
        except Exception as e:
            return LLMResponse(
                content="",
                usage=LLMUsage(),
                model=self._config.model,
                provider=self.name,
                success=False,
                error_message=str(e),
            )

    async def _call_api(
        self,
        client: Any,
        messages: list[dict],
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float,
    ) -> Any:
        """Call the Anthropic API"""
        try:
            kwargs = {
                "model": self._config.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
            if system_prompt:
                kwargs["system"] = system_prompt

            return await client.messages.create(**kwargs)

        except Exception as e:
            error_str = str(e).lower()
            if "authentication" in error_str or "invalid api key" in error_str:
                raise LLMAuthenticationError("anthropic", str(e))
            elif "rate limit" in error_str:
                raise LLMRateLimitError("anthropic")
            elif "timeout" in error_str:
                raise LLMTimeoutError("anthropic", self._config.timeout)
            else:
                raise

    def get_total_usage(self) -> LLMUsage:
        """Get total token usage"""
        return self._total_usage

    def get_call_count(self) -> int:
        """Get number of calls made"""
        return self._call_count

    async def close(self) -> None:
        """Close the client"""
        if self._client:
            await self._client.close()
            self._client = None
