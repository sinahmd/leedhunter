"""
OpenAI LLM Provider Adapter

This module implements the LLM provider interface for OpenAI's API.
Also supports OpenAI-compatible endpoints (local servers, other providers).

Requires: pip install leedhunter[llm-openai]
"""

from dataclasses import dataclass
from typing import Any

from leedhunter.application.llm.errors import (
    LLMAuthenticationError,
    LLMProviderUnavailableError,
    LLMRateLimitError,
    LLMTimeoutError,
)
from leedhunter.application.llm.provider import LLMProvider, LLMResponse, LLMUsage
from leedhunter.infrastructure.retry import RetryConfig, retry_async


@dataclass
class OpenAIConfig:
    """Configuration for OpenAI provider"""

    api_key: str
    base_url: str | None = None  # For OpenAI-compatible endpoints
    model: str = "gpt-4"
    max_tokens: int = 4096
    temperature: float = 0.2
    timeout: float = 60.0
    max_retries: int = 3


class OpenAILLMProvider(LLMProvider):
    """
    OpenAI LLM provider.

    Uses the OpenAI API or OpenAI-compatible endpoints.
    """

    def __init__(self, config: OpenAIConfig):
        if not config.api_key:
            raise ValueError("OpenAI API key is required")

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
        """Get or create OpenAI client"""
        if self._client is None:
            try:
                import openai

                kwargs = {"api_key": self._config.api_key}
                if self._config.base_url:
                    kwargs["base_url"] = self._config.base_url
                self._client = openai.AsyncOpenAI(**kwargs)
            except ImportError:
                raise LLMProviderUnavailableError(
                    "openai",
                    "openai package not installed. Install with: pip install leedhunter[llm-openai]",
                )
        return self._client

    @property
    def name(self) -> str:
        if self._config.base_url:
            return "openai_compatible"
        return "openai"

    @property
    def model(self) -> str:
        return self._config.model

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """
        Generate a response from OpenAI

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

            # Build messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            # Call API with retry
            response = await retry_async(
                self._call_api,
                client,
                messages,
                min(max_tokens, self._config.max_tokens),
                min(temperature, self._config.temperature),
                config=self._retry_config,
            )

            # Extract usage
            usage = LLMUsage(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
            )
            self._total_usage = self._total_usage + usage

            # Extract content
            content = response.choices[0].message.content or ""

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
        max_tokens: int,
        temperature: float,
    ) -> Any:
        """Call the OpenAI API"""
        try:
            return await client.chat.completions.create(
                model=self._config.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )

        except Exception as e:
            error_str = str(e).lower()
            if "authentication" in error_str or "invalid api key" in error_str:
                raise LLMAuthenticationError("openai", str(e))
            elif "rate limit" in error_str:
                raise LLMRateLimitError("openai")
            elif "timeout" in error_str:
                raise LLMTimeoutError("openai", self._config.timeout)
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
