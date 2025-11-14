"""Application configuration using pydantic-settings."""

from typing import Literal, Optional
from pydantic import Field, PostgresDsn, field_validator, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Ybryx Capital Backend"
    app_version: str = "0.1.0"
    debug: bool = Field(default=False, validation_alias="DEBUG")
    environment: Literal["development", "staging", "production"] = "development"

    # API
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        validation_alias="CORS_ORIGINS"
    )

    # Database - Postgres/Supabase
    database_url: PostgresDsn = Field(
        default="postgresql://postgres:postgres@localhost:5432/ybryx",
        validation_alias="DATABASE_URL"
    )
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_echo: bool = False

    # Supabase
    supabase_url: Optional[str] = Field(default=None, validation_alias="SUPABASE_URL")
    supabase_key: Optional[str] = Field(default=None, validation_alias="SUPABASE_ANON_KEY")
    supabase_service_key: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("SUPABASE_SERVICE_KEY", "SUPABASE_SERVICE_ROLE_KEY")
    )

    # LLM Configuration - Priority Order
    # 1. OpenAI GPT-5-nano for supervisor/routing (fast, cost-effective)
    #    NOTE: GPT-5 models require max_completion_tokens (not max_tokens)
    #    and reasoning_effort="minimal" for conversational tasks
    # 2. Anthropic Claude for primary reasoning
    openai_api_key: str = Field(validation_alias="OPENAI_API_KEY")
    openai_org_id: Optional[str] = Field(default=None, validation_alias="OPENAI_ORG_ID")
    openai_supervisor_model: str = "gpt-5-nano"

    anthropic_api_key: str = Field(validation_alias="ANTHROPIC_API_KEY")
    anthropic_primary_model: str = "claude-3-5-sonnet-20241022"

    # LLM Settings
    llm_temperature: float = 0.7
    llm_max_tokens: int = 4096
    llm_timeout: int = 60

    # Memory - Mem0
    mem0_api_key: Optional[str] = Field(default=None, validation_alias="MEM0_API_KEY")
    mem0_host: Optional[str] = Field(default=None, validation_alias="MEM0_HOST")
    mem0_collection_name: str = "ybryx_memory"

    # Vector Store (fallback if Mem0 not available)
    vector_store_type: Literal["chroma", "qdrant", "mem0"] = "mem0"
    chroma_persist_directory: str = "./data/chroma"
    qdrant_url: Optional[str] = Field(default=None, validation_alias="QDRANT_URL")
    qdrant_api_key: Optional[str] = Field(default=None, validation_alias="QDRANT_API_KEY")

    # Security
    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        validation_alias="SECRET_KEY"
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Feature Flags
    enable_compliance_checks: bool = True
    enable_dealer_notifications: bool = True
    enable_credit_scoring: bool = True
    enable_agent_streaming: bool = True

    # Logging
    log_level: str = "INFO"
    log_format: Literal["json", "console"] = "console"

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 60

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @property
    def async_database_url(self) -> str:
        """Get async database URL for asyncpg."""
        if isinstance(self.database_url, str):
            return self.database_url.replace("postgresql://", "postgresql+asyncpg://")
        return str(self.database_url).replace("postgresql://", "postgresql+asyncpg://")

    @property
    def sync_database_url(self) -> str:
        """Get sync database URL for psycopg2."""
        if isinstance(self.database_url, str):
            return self.database_url
        return str(self.database_url)


# Global settings instance
settings = Settings()
