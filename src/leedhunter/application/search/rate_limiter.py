"""
Rate Limiter

This module provides rate limiting for search providers.
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting"""

    requests_per_second: float = 1.0
    requests_per_minute: float = 60.0
    requests_per_hour: float = 1000.0
    burst_size: int = 1
    cooldown_seconds: float = 1.0


class RateLimiter:
    """
    Rate limiter for search providers

    Implements token bucket algorithm with configurable limits.
    """

    def __init__(self, config: RateLimitConfig):
        """
        Initialize rate limiter

        Args:
            config: Rate limit configuration
        """
        self.config = config
        self._tokens: float = config.burst_size
        self._last_update: datetime = datetime.now(timezone.utc)
        self._request_count_minute: int = 0
        self._request_count_hour: int = 0
        self._minute_start: datetime = datetime.now(timezone.utc)
        self._hour_start: datetime = datetime.now(timezone.utc)
        self._lock = asyncio.Lock()

    async def acquire(self) -> bool:
        """
        Acquire a rate limit token

        Returns:
            True if token acquired, False if rate limited
        """
        async with self._lock:
            now = datetime.now(timezone.utc)

            # Update token bucket
            self._update_tokens(now)

            # Check hourly limit
            self._update_hourly_count(now)
            if self._request_count_hour >= self.config.requests_per_hour:
                return False

            # Check minute limit
            self._update_minute_count(now)
            if self._request_count_minute >= self.config.requests_per_minute:
                return False

            # Try to acquire token
            if self._tokens >= 1:
                self._tokens -= 1
                self._request_count_minute += 1
                self._request_count_hour += 1
                return True

            return False

    def release(self) -> None:
        """
        Release a rate limit token

        This is called when a request completes successfully.
        """
        # Token bucket automatically replenishes
        pass

    def _update_tokens(self, now: datetime) -> None:
        """Update token bucket based on elapsed time"""
        elapsed = (now - self._last_update).total_seconds()
        new_tokens = elapsed * self.config.requests_per_second
        self._tokens = min(
            self.config.burst_size,
            self._tokens + new_tokens,
        )
        self._last_update = now

    def _update_minute_count(self, now: datetime) -> None:
        """Update minute request count"""
        elapsed = (now - self._minute_start).total_seconds()
        if elapsed >= 60:
            self._request_count_minute = 0
            self._minute_start = now

    def _update_hourly_count(self, now: datetime) -> None:
        """Update hourly request count"""
        elapsed = (now - self._hour_start).total_seconds()
        if elapsed >= 3600:
            self._request_count_hour = 0
            self._hour_start = now

    async def wait_if_needed(self) -> None:
        """
        Wait if rate limited

        This will block until a token is available.
        """
        while not await self.acquire():
            await asyncio.sleep(self.config.cooldown_seconds)

    def get_stats(self) -> dict:
        """
        Get rate limiter statistics

        Returns:
            Dictionary with rate limiter stats
        """
        return {
            "tokens_available": int(self._tokens),
            "burst_size": self.config.burst_size,
            "requests_this_minute": self._request_count_minute,
            "requests_this_hour": self._request_count_hour,
            "requests_per_second": self.config.requests_per_second,
            "requests_per_minute": self.config.requests_per_minute,
            "requests_per_hour": self.config.requests_per_hour,
        }

    def reset(self) -> None:
        """Reset rate limiter state"""
        self._tokens = self.config.burst_size
        self._last_update = datetime.now(timezone.utc)
        self._request_count_minute = 0
        self._request_count_hour = 0
        self._minute_start = datetime.now(timezone.utc)
        self._hour_start = datetime.now(timezone.utc)
