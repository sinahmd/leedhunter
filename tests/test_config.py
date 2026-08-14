"""
Tests for configuration module
"""

import pytest
from leedhunter.config import (
    DatabaseSettings,
    LLMProviderType,
    LLMSettings,
    RedisSettings,
    Settings,
    get_settings,
    reset_settings,
)


class TestDatabaseSettings:
    """Tests for DatabaseSettings"""

    def test_default_values(self):
        """Test default database settings"""
        settings = DatabaseSettings()
        assert settings.host == "localhost"
        assert settings.port == 5432
        assert settings.user == "leedhunter"
        assert settings.password == ""
        assert settings.name == "leedhunter"

    def test_url_generation(self):
        """Test database URL generation"""
        settings = DatabaseSettings(
            host="db.example.com",
            port=5433,
            user="testuser",
            password="testpass",
            name="testdb",
        )
        url = settings.url
        assert "postgresql+asyncpg://" in url
        assert "testuser:testpass@db.example.com:5433/testdb" in url

    def test_sync_url_generation(self):
        """Test synchronous database URL generation"""
        settings = DatabaseSettings()
        url = settings.sync_url
        assert "postgresql://" in url
        assert "+asyncpg" not in url

    def test_from_env(self, monkeypatch):
        """Test loading from environment variables"""
        monkeypatch.setenv("LEEDHUNTER_DB_HOST", "envhost")
        monkeypatch.setenv("LEEDHUNTER_DB_PORT", "5433")
        settings = DatabaseSettings()
        assert settings.host == "envhost"
        assert settings.port == 5433


class TestRedisSettings:
    """Tests for RedisSettings"""

    def test_default_values(self):
        """Test default Redis settings"""
        settings = RedisSettings()
        assert settings.host == "localhost"
        assert settings.port == 6379
        assert settings.password is None
        assert settings.db == 0

    def test_url_generation(self):
        """Test Redis URL generation"""
        settings = RedisSettings()
        url = settings.url
        assert url == "redis://localhost:6379/0"

    def test_url_with_password(self):
        """Test Redis URL with password"""
        settings = RedisSettings(password="secret")
        url = settings.url
        assert "redis://:secret@localhost:6379/0" in url

    def test_custom_db(self):
        """Test Redis with custom database"""
        settings = RedisSettings(db=5)
        url = settings.url
        assert url.endswith("/5")


class TestLLMSettings:
    """Tests for LLMSettings"""

    def test_default_values(self):
        """Test default LLM settings"""
        settings = LLMSettings()
        assert settings.provider == LLMProviderType.ANTHROPIC
        assert settings.model == "claude-3-sonnet-20240229"
        assert settings.max_tokens == 4096
        assert settings.temperature == 0.7

    def test_provider_enum(self):
        """Test LLM provider enum values"""
        assert LLMProviderType.ANTHROPIC == "anthropic"
        assert LLMProviderType.OPENAI == "openai"
        assert LLMProviderType.GOOGLE == "google"

    def test_custom_settings(self):
        """Test custom LLM settings"""
        settings = LLMSettings(
            provider=LLMProviderType.OPENAI,
            api_key="test-key",
            model="gpt-4",
            max_tokens=8192,
            temperature=0.5,
        )
        assert settings.provider == LLMProviderType.OPENAI
        assert settings.api_key == "test-key"
        assert settings.model == "gpt-4"


class TestSettings:
    """Tests for main Settings"""

    def test_default_settings(self):
        """Test default application settings"""
        settings = Settings()
        assert settings.app_name == "LeedHunter"
        assert settings.version == "0.1.0"
        assert settings.debug is False

    def test_debug_mode(self):
        """Test debug mode setting"""
        settings = Settings(debug=True)
        assert settings.debug is True

    def test_database_settings(self):
        """Test database settings are included"""
        settings = Settings()
        assert isinstance(settings.database, DatabaseSettings)
        assert settings.database.host == "localhost"

    def test_redis_settings(self):
        """Test Redis settings are included"""
        settings = Settings()
        assert isinstance(settings.redis, RedisSettings)

    def test_llm_settings(self):
        """Test LLM settings are included"""
        settings = Settings()
        assert isinstance(settings.llm, LLMSettings)

    def test_load_method(self):
        """Test Settings.load() method"""
        settings = Settings.load()
        assert isinstance(settings, Settings)


class TestGetSettings:
    """Tests for get_settings function"""

    def setup_method(self):
        """Reset settings before each test"""
        reset_settings()

    def teardown_method(self):
        """Reset settings after each test"""
        reset_settings()

    def test_get_settings_returns_instance(self):
        """Test get_settings returns a Settings instance"""
        settings = get_settings()
        assert isinstance(settings, Settings)

    def test_get_settings_caches_instance(self):
        """Test get_settings returns the same instance"""
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2

    def test_reset_settings(self):
        """Test reset_settings clears the cache"""
        settings1 = get_settings()
        reset_settings()
        settings2 = get_settings()
        assert settings1 is not settings2
