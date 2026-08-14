"""
Tests for sandbox configuration
"""

import pytest

from leedhunter.infrastructure.sandbox.config import (
    SandboxConfig,
    SandboxManager,
)


class TestSandboxConfig:
    """Tests for SandboxConfig"""

    def test_default_config(self):
        """Test default sandbox configuration"""
        config = SandboxConfig()

        assert config.max_memory_mb == 512
        assert config.max_cpu_percent == 50.0
        assert config.headless is True

    def test_custom_config(self):
        """Test custom sandbox configuration"""
        config = SandboxConfig(
            max_memory_mb=1024,
            headless=False,
            allowed_domains=["example.com"],
        )

        assert config.max_memory_mb == 1024
        assert config.headless is False
        assert "example.com" in config.allowed_domains

    def test_from_env(self, monkeypatch):
        """Test loading from environment variables"""
        monkeypatch.setenv("LEEDHUNTER_SANDBOX_MAX_MEMORY_MB", "2048")
        monkeypatch.setenv("LEEDHUNTER_SANDBOX_HEADLESS", "false")

        config = SandboxConfig.from_env()

        assert config.max_memory_mb == 2048
        assert config.headless is False

    def test_is_domain_allowed_default(self):
        """Test domain allowed with default config"""
        config = SandboxConfig()

        assert config.is_domain_allowed("example.com") is True

    def test_is_domain_allowed_whitelist(self):
        """Test domain allowed with whitelist"""
        config = SandboxConfig(allowed_domains=["example.com", "test.com"])

        assert config.is_domain_allowed("example.com") is True
        assert config.is_domain_allowed("other.com") is False

    def test_is_domain_allowed_blacklist(self):
        """Test domain allowed with blacklist"""
        config = SandboxConfig(blocked_domains=["blocked.com"])

        assert config.is_domain_allowed("example.com") is True
        assert config.is_domain_allowed("blocked.com") is False


class TestSandboxManager:
    """Tests for SandboxManager"""

    def setup_method(self):
        """Set up test fixtures"""
        self.manager = SandboxManager()

    def test_default_manager(self):
        """Test default sandbox manager"""
        assert self.manager.config is not None
        assert self.manager.config.max_memory_mb == 512

    def test_custom_manager(self):
        """Test custom sandbox manager"""
        config = SandboxConfig(max_memory_mb=1024)
        manager = SandboxManager(config)

        assert manager.config.max_memory_mb == 1024

    def test_update_config(self):
        """Test updating configuration"""
        self.manager.update_config(max_memory_mb=2048, headless=False)

        assert self.manager.config.max_memory_mb == 2048
        assert self.manager.config.headless is False

    def test_validate_url_allowed(self):
        """Test validating allowed URL"""
        assert self.manager.validate_url("https://example.com") is True

    def test_validate_url_blocked(self):
        """Test validating blocked URL"""
        config = SandboxConfig(blocked_domains=["blocked.com"])
        manager = SandboxManager(config)

        assert manager.validate_url("https://blocked.com") is False

    def test_get_browser_options(self):
        """Test getting browser options"""
        options = self.manager.get_browser_options()

        assert "headless" in options
        assert "disable_images" in options
        assert options["headless"] is True

    def test_get_resource_limits(self):
        """Test getting resource limits"""
        limits = self.manager.get_resource_limits()

        assert "max_memory_mb" in limits
        assert "max_cpu_percent" in limits
        assert limits["max_memory_mb"] == 512
