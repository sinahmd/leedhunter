"""
LLM Error types

These errors represent failures in LLM operations.
"""


class LLMError(Exception):
    """Base exception for LLM errors"""

    pass


class LLMAuthenticationError(LLMError):
    """Raised when LLM authentication fails"""

    def __init__(self, provider: str, message: str = "Invalid API key"):
        self.provider = provider
        super().__init__(f"LLM authentication error for '{provider}': {message}")


class LLMRateLimitError(LLMError):
    """Raised when LLM rate limits are exceeded"""

    def __init__(self, provider: str, retry_after: float | None = None):
        self.provider = provider
        self.retry_after = retry_after
        super().__init__(f"LLM rate limit exceeded for '{provider}'")


class LLMTimeoutError(LLMError):
    """Raised when LLM request times out"""

    def __init__(self, provider: str, timeout: float):
        self.provider = provider
        self.timeout = timeout
        super().__init__(f"LLM request timed out for '{provider}' after {timeout}s")


class LLMProviderUnavailableError(LLMError):
    """Raised when LLM provider is unavailable"""

    def __init__(self, provider: str, message: str = "Provider unavailable"):
        self.provider = provider
        super().__init__(f"LLM provider '{provider}' unavailable: {message}")


class LLMInvalidResponseError(LLMError):
    """Raised when LLM response is invalid"""

    def __init__(self, provider: str, message: str = "Invalid response"):
        self.provider = provider
        super().__init__(f"LLM invalid response from '{provider}': {message}")


class LLMBudgetExceededError(LLMError):
    """Raised when LLM budget is exceeded"""

    def __init__(self, provider: str, budget_type: str, limit: float):
        self.provider = provider
        self.budget_type = budget_type
        self.limit = limit
        super().__init__(f"LLM budget exceeded for '{provider}': {budget_type} limit {limit}")
