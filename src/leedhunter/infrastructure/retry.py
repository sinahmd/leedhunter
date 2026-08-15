"""
Retry with exponential backoff

This module provides retry logic for flaky external services.
"""

import asyncio
import random
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TypeVar

from leedhunter.infrastructure.errors import (
    InfrastructureError,
    NetworkError,
    ProviderError,
    RateLimitError,
)

T = TypeVar("T")


@dataclass
class RetryConfig:
    """Configuration for retry behavior"""

    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True


class RetryableError(InfrastructureError):
    """Error that can be retried"""

    pass


def is_retryable(error: Exception) -> bool:
    """
    Check if an error is retryable

    Args:
        error: The exception to check

    Returns:
        True if the error is retryable
    """
    if isinstance(error, (NetworkError, RateLimitError)):
        return True
    if isinstance(error, ProviderError) and error.retryable:
        return True
    return bool(isinstance(error, RetryableError))


def calculate_delay(
    attempt: int,
    config: RetryConfig,
    retry_after: float | None = None,
) -> float:
    """
    Calculate delay for retry attempt

    Args:
        attempt: Current attempt number (0-based)
        config: Retry configuration
        retry_after: Server-specified retry delay

    Returns:
        Delay in seconds
    """
    # Use server-specified delay if available
    if retry_after is not None:
        return min(retry_after, config.max_delay)

    # Calculate exponential backoff
    delay = config.base_delay * (config.exponential_base**attempt)

    # Apply jitter to prevent thundering herd
    if config.jitter:
        delay = delay * (0.5 + random.random())

    # Cap at max delay
    return min(delay, config.max_delay)


async def retry_async(
    func: Callable[..., Any],
    *args: Any,
    config: RetryConfig | None = None,
    **kwargs: Any,
) -> Any:
    """
    Retry an async function with exponential backoff

    Args:
        func: Async function to retry
        *args: Positional arguments for func
        config: Retry configuration
        **kwargs: Keyword arguments for func

    Returns:
        Result of func

    Raises:
        The last exception if all retries fail
    """
    if config is None:
        config = RetryConfig()

    last_error = None

    for attempt in range(config.max_retries + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_error = e

            # Check if error is retryable
            if not is_retryable(e):
                raise

            # Don't sleep on last attempt
            if attempt < config.max_retries:
                # Get retry-after from rate limit error if available
                retry_after = None
                if isinstance(e, RateLimitError):
                    retry_after = e.retry_after

                delay = calculate_delay(attempt, config, retry_after)
                await asyncio.sleep(delay)

    # All retries exhausted
    raise last_error


def retry_sync(
    func: Callable[..., Any],
    *args: Any,
    config: RetryConfig | None = None,
    **kwargs: Any,
) -> Any:
    """
    Retry a sync function with exponential backoff

    Args:
        func: Sync function to retry
        *args: Positional arguments for func
        config: Retry configuration
        **kwargs: Keyword arguments for func

    Returns:
        Result of func

    Raises:
        The last exception if all retries fail
    """
    import time

    if config is None:
        config = RetryConfig()

    last_error = None

    for attempt in range(config.max_retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_error = e

            # Check if error is retryable
            if not is_retryable(e):
                raise

            # Don't sleep on last attempt
            if attempt < config.max_retries:
                # Get retry-after from rate limit error if available
                retry_after = None
                if isinstance(e, RateLimitError):
                    retry_after = e.retry_after

                delay = calculate_delay(attempt, config, retry_after)
                time.sleep(delay)

    # All retries exhausted
    raise last_error
