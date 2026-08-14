"""
Sandbox Configuration

This module provides sandbox configuration for isolating browser and provider execution.

When browser/provider execution requires isolation:
LeedHunter → Sandbox → browser, temporary files, provider sessions

The user-facing CLI should remain simple.
The user should not need to understand Docker/container internals to perform research.
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SandboxConfig:
    """Configuration for sandbox execution"""

    # Resource limits
    max_memory_mb: int = 512
    max_cpu_percent: float = 50.0
    max_timeout_seconds: int = 300

    # Network settings
    allowed_domains: list[str] = field(default_factory=list)
    blocked_domains: list[str] = field(default_factory=list)

    # File system settings
    temp_dir: Optional[str] = None
    max_temp_size_mb: int = 100

    # Browser settings
    headless: bool = True
    disable_images: bool = True
    disable_javascript: bool = False

    # Provider settings
    provider_timeout: float = 30.0
    max_retries: int = 3

    @classmethod
    def from_env(cls) -> "SandboxConfig":
        """Load configuration from environment variables"""
        return cls(
            max_memory_mb=int(os.getenv("LEEDHUNTER_SANDBOX_MAX_MEMORY_MB", "512")),
            max_cpu_percent=float(os.getenv("LEEDHUNTER_SANDBOX_MAX_CPU_PERCENT", "50.0")),
            max_timeout_seconds=int(os.getenv("LEEDHUNTER_SANDBOX_TIMEOUT", "300")),
            headless=os.getenv("LEEDHUNTER_SANDBOX_HEADLESS", "true").lower() == "true",
            disable_images=os.getenv("LEEDHUNTER_SANDBOX_DISABLE_IMAGES", "true").lower() == "true",
            disable_javascript=os.getenv("LEEDHUNTER_SANDBOX_DISABLE_JS", "false").lower() == "true",
            provider_timeout=float(os.getenv("LEEDHUNTER_SANDBOX_PROVIDER_TIMEOUT", "30.0")),
            max_retries=int(os.getenv("LEEDHUNTER_SANDBOX_MAX_RETRIES", "3")),
        )

    def is_domain_allowed(self, domain: str) -> bool:
        """Check if a domain is allowed"""
        if self.blocked_domains and domain in self.blocked_domains:
            return False
        if self.allowed_domains:
            return domain in self.allowed_domains
        return True


class SandboxManager:
    """
    Manages sandbox execution.

    This is a configuration manager. Actual sandbox execution
    (Docker, containers) would be implemented separately.
    """

    def __init__(self, config: Optional[SandboxConfig] = None):
        self._config = config or SandboxConfig.from_env()

    @property
    def config(self) -> SandboxConfig:
        """Get sandbox configuration"""
        return self._config

    def update_config(self, **kwargs) -> None:
        """Update sandbox configuration"""
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)

    def validate_url(self, url: str) -> bool:
        """
        Validate if a URL is allowed in the sandbox

        Args:
            url: URL to validate

        Returns:
            True if URL is allowed
        """
        from urllib.parse import urlparse

        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            return self._config.is_domain_allowed(domain)
        except Exception:
            return False

    def get_browser_options(self) -> dict:
        """Get browser options for sandbox"""
        return {
            "headless": self._config.headless,
            "disable_images": self._config.disable_images,
            "disable_javascript": self._config.disable_javascript,
            "timeout": self._config.provider_timeout,
        }

    def get_resource_limits(self) -> dict:
        """Get resource limits"""
        return {
            "max_memory_mb": self._config.max_memory_mb,
            "max_cpu_percent": self._config.max_cpu_percent,
            "max_timeout_seconds": self._config.max_timeout_seconds,
        }
