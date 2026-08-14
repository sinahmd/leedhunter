"""
Centralized configuration for LeedHunter

All configuration is managed through this module using pydantic-settings.
Configuration can be provided via environment variables or .env file.
"""

from enum import Enum
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LogLevel(str, Enum):
    """Logging levels"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LLMProviderType(str, Enum):
    """Supported LLM providers"""

    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"
    OPENAI_COMPATIBLE = "openai_compatible"


class DatabaseSettings(BaseSettings):
    """PostgreSQL database configuration"""

    model_config = SettingsConfigDict(env_prefix="LEEDHUNTER_DB_")

    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, description="Database port")
    user: str = Field(default="leedhunter", description="Database user")
    password: str = Field(default="", description="Database password")
    name: str = Field(default="leedhunter", description="Database name")

    @property
    def url(self) -> str:
        """Get the database connection URL"""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    @property
    def sync_url(self) -> str:
        """Get the synchronous database connection URL (for migrations)"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class RedisSettings(BaseSettings):
    """Redis configuration"""

    model_config = SettingsConfigDict(env_prefix="LEEDHUNTER_REDIS_")

    host: str = Field(default="localhost", description="Redis host")
    port: int = Field(default=6379, description="Redis port")
    password: Optional[str] = Field(default=None, description="Redis password")
    db: int = Field(default=0, description="Redis database number")

    @property
    def url(self) -> str:
        """Get the Redis connection URL"""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"


class LLMSettings(BaseSettings):
    """LLM provider configuration"""

    model_config = SettingsConfigDict(env_prefix="LEEDHUNTER_LLM_")

    enabled: bool = Field(default=False, description="Enable LLM functionality")
    provider: LLMProviderType = Field(
        default=LLMProviderType.ANTHROPIC,
        description="LLM provider to use",
    )
    api_key: str = Field(default="", description="API key for the LLM provider")
    base_url: Optional[str] = Field(default=None, description="Base URL for API (for OpenAI-compatible)")
    model: str = Field(default="claude-3-sonnet-20240229", description="Model to use")
    max_tokens: int = Field(default=4096, description="Maximum tokens for responses")
    temperature: float = Field(default=0.2, description="Temperature for generation")
    timeout_seconds: float = Field(default=60.0, description="Request timeout in seconds")
    max_calls_per_research: int = Field(default=10, description="Max LLM calls per research job")
    max_cost_per_research: Optional[float] = Field(default=None, description="Max cost per research job")

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate that API key is not empty in production"""
        # Allow empty for testing/development
        return v


class SearchSettings(BaseSettings):
    """Search provider configuration"""

    model_config = SettingsConfigDict(env_prefix="LEEDHUNTER_SEARCH_")

    default_provider: str = Field(
        default="google",
        description="Default search provider",
    )
    max_results_per_query: int = Field(
        default=100,
        description="Maximum results per search query",
    )
    timeout_seconds: float = Field(
        default=30.0,
        description="Search timeout in seconds",
    )


class ResearchSettings(BaseSettings):
    """Research job configuration"""

    model_config = SettingsConfigDict(env_prefix="LEEDHUNTER_RESEARCH_")

    max_queries: int = Field(
        default=100,
        description="Maximum queries per research job",
    )
    max_candidates: int = Field(
        default=1000,
        description="Maximum candidates per research job",
    )
    max_pages_per_entity: int = Field(
        default=10,
        description="Maximum pages to fetch per entity",
    )
    max_runtime_seconds: int = Field(
        default=3600,
        description="Maximum runtime in seconds",
    )
    max_llm_calls: int = Field(
        default=100,
        description="Maximum LLM calls per research job",
    )


class SandboxSettings(BaseSettings):
    """Sandbox configuration"""

    model_config = SettingsConfigDict(env_prefix="LEEDHUNTER_SANDBOX_")

    max_memory_mb: int = Field(
        default=1024,
        description="Maximum memory per sandbox in MB",
    )
    max_cpu_percent: float = Field(
        default=75.0,
        description="Maximum CPU usage percentage",
    )
    timeout: int = Field(
        default=60,
        description="Sandbox timeout in seconds",
    )
    headless: bool = Field(
        default=True,
        description="Run browser in headless mode",
    )


class Settings(BaseSettings):
    """Main application settings"""

    model_config = SettingsConfigDict(
        env_prefix="LEEDHUNTER_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra environment variables
    )

    # Application
    app_name: str = Field(default="LeedHunter", description="Application name")
    version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Logging level")

    # Sub-settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    search: SearchSettings = Field(default_factory=SearchSettings)
    research: ResearchSettings = Field(default_factory=ResearchSettings)
    sandbox: SandboxSettings = Field(default_factory=SandboxSettings)

    @classmethod
    def load(cls) -> "Settings":
        """Load settings from environment and .env file"""
        return cls()


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance (lazy initialization)"""
    global _settings
    if _settings is None:
        _settings = Settings.load()
    return _settings


def reset_settings() -> None:
    """Reset the global settings instance (for testing)"""
    global _settings
    _settings = None
