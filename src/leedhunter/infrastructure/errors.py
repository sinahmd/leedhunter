"""
Infrastructure-specific error types

These errors represent failures in external systems and infrastructure.
"""


class InfrastructureError(Exception):
    """Base exception for infrastructure errors"""

    pass


class ProviderError(InfrastructureError):
    """Raised when an external provider fails"""

    def __init__(self, provider: str, message: str, retryable: bool = True):
        self.provider = provider
        self.retryable = retryable
        super().__init__(f"Provider '{provider}' error: {message}")


class AuthenticationError(InfrastructureError):
    """Raised when authentication fails"""

    def __init__(self, provider: str, message: str = "Authentication failed"):
        self.provider = provider
        super().__init__(f"Authentication error for '{provider}': {message}")


class RateLimitError(InfrastructureError):
    """Raised when rate limits are exceeded"""

    def __init__(self, provider: str, retry_after: float | None = None):
        self.provider = provider
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded for '{provider}'")


class NetworkError(InfrastructureError):
    """Raised when network operations fail"""

    def __init__(self, message: str, retryable: bool = True):
        self.retryable = retryable
        super().__init__(f"Network error: {message}")


class StorageError(InfrastructureError):
    """Raised when storage operations fail"""

    pass
