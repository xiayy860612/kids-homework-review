"""Application configuration using Pydantic Settings."""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings.

    Attributes:
        DATABASE_URL: Database connection URL
        SECRET_KEY: Secret key for JWT signing
        ALGORITHM: JWT algorithm
        ACCESS_TOKEN_EXPIRE_MINUTES: Token expiration time in minutes
        FRONTEND_URL: Frontend URL for CORS
        COOKIE_SECURE: Whether cookies should be set with Secure flag
    """

    DATABASE_URL: str = "postgresql+asyncpg://postgres:s2u2m1234@localhost:5432/homework_review"
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    FRONTEND_URL: str = "http://localhost:3000"
    COOKIE_SECURE: bool = False  # Set to True in production with HTTPS

    # AI Analysis Configuration
    AI_API_BASE: str = "https://open.bigmodel.cn/api/paas/v4"
    AI_API_KEY: str = ""
    AI_MODEL: str = "glm-4v-plus"
    AI_TIMEOUT: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate DATABASE_URL format."""
        if not v.startswith(("postgresql+asyncpg://", "sqlite+aiosqlite://")):
            raise ValueError(
                "DATABASE_URL must use postgresql+asyncpg:// or sqlite+aiosqlite:// scheme"
            )
        return v


settings = Settings()
