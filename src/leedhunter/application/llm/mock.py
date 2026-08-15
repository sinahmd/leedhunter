"""
Mock LLM Provider

This provider returns pre-configured responses for testing.
No real LLM API calls are made.
"""

from leedhunter.application.llm.provider import LLMProvider, LLMResponse, LLMUsage


class MockLLMProvider(LLMProvider):
    """
    Mock LLM provider for testing

    Returns deterministic responses without making real API calls.
    """

    def __init__(
        self,
        responses: dict[str, str] | None = None,
        default_response: str = '{"result": "mock"}',
    ):
        self._responses = responses or {}
        self._default_response = default_response
        self._total_usage = LLMUsage()
        self._call_count = 0

    @property
    def name(self) -> str:
        return "mock"

    @property
    def model(self) -> str:
        return "mock-model"

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Generate a mock response"""
        self._call_count += 1

        # Try to find a matching response
        content = self._default_response
        for key, response in self._responses.items():
            if key.lower() in prompt.lower():
                content = response
                break

        # Simulate token usage
        usage = LLMUsage(
            prompt_tokens=len(prompt.split()),
            completion_tokens=len(content.split()),
            total_tokens=len(prompt.split()) + len(content.split()),
        )
        self._total_usage = self._total_usage + usage

        return LLMResponse(
            content=content,
            usage=usage,
            model=self.model,
            provider=self.name,
            success=True,
        )

    def get_total_usage(self) -> LLMUsage:
        return self._total_usage

    def get_call_count(self) -> int:
        return self._call_count

    def reset(self) -> None:
        """Reset usage tracking"""
        self._total_usage = LLMUsage()
        self._call_count = 0
