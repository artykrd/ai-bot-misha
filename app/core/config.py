"""
Application configuration using Pydantic Settings.
Loads all configuration from environment variables (.env file).
"""
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # =====================================
    # TELEGRAM BOT CONFIGURATION
    # =====================================
    telegram_bot_token: str = Field(..., description="Main bot token from @BotFather")
    telegram_admin_bot_token: str = Field(..., description="Admin bot token from @BotFather")
    admin_user_ids: str = Field(..., description="Comma-separated admin user IDs")

    webhook_url: Optional[str] = Field(None, description="Webhook URL if using webhook mode")
    webhook_path: str = Field("/webhook", description="Webhook path")

    @field_validator("admin_user_ids")
    @classmethod
    def parse_admin_ids(cls, v: str) -> List[int]:
        """Parse comma-separated admin IDs into list of integers."""
        return [int(id_.strip()) for id_ in v.split(",") if id_.strip()]

    # =====================================
    # DATABASE CONFIGURATION
    # =====================================
    database_url: str = Field(..., description="PostgreSQL async database URL")
    db_pool_size: int = Field(50, description="Database connection pool size")
    db_max_overflow: int = Field(20, description="Max overflow connections")

    # =====================================
    # REDIS CONFIGURATION
    # =====================================
    redis_url: str = Field("redis://localhost:6379/0", description="Redis URL")
    redis_fsm_db: int = Field(1, description="Redis database for FSM states")

    # =====================================
    # AI API KEYS
    # =====================================
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(None, description="Anthropic API key")
    google_ai_api_key: Optional[str] = Field(None, description="Google AI API key")
    deepseek_api_key: Optional[str] = Field(None, description="DeepSeek API key")
    perplexity_api_key: Optional[str] = Field(None, description="Perplexity API key")
    stability_api_key: Optional[str] = Field(None, description="Stability AI API key")
    midjourney_api_key: Optional[str] = Field(None, description="Midjourney API key")
    replicate_api_key: Optional[str] = Field(None, description="Replicate API key")
    suno_api_key: Optional[str] = Field(None, description="Suno AI API key")
    luma_api_key: Optional[str] = Field(None, description="Luma Labs API key")
    hailuo_api_key: Optional[str] = Field(None, description="Hailuo (MiniMax) API key")
    kling_api_key: Optional[str] = Field(None, description="Kling AI API key (legacy)")
    kling_access_key: Optional[str] = Field(None, description="Kling AI access key for official API")
    kling_secret_key: Optional[str] = Field(None, description="Kling AI secret key for official API")
    aimlapi_key: Optional[str] = Field(None, description="AI/ML API unified key (fallback for multiple services)")
    removebg_api_key: Optional[str] = Field(None, description="Remove.bg API key")

    # =====================================
    # GOOGLE CLOUD / VERTEX AI
    # =====================================
    google_cloud_project: Optional[str] = Field(None, description="Google Cloud Project ID for Vertex AI")
    google_application_credentials: Optional[str] = Field(None, description="Path to Google Cloud credentials JSON file")

    # =====================================
    # PAYMENT CONFIGURATION
    # =====================================
    yukassa_shop_id: Optional[str] = Field(None, description="ЮKassa shop ID")
    yukassa_secret_key: Optional[str] = Field(None, description="ЮKassa secret key")
    payment_return_url: Optional[str] = Field(None, description="Payment return URL")

    # =====================================
    # APPLICATION SETTINGS
    # =====================================
    environment: str = Field("development", description="Environment (development/production)")
    debug: bool = Field(False, description="Debug mode")
    log_level: str = Field("INFO", description="Logging level")

    app_host: str = Field("127.0.0.1", description="FastAPI host")
    port: Optional[int] = Field(None, description="FastAPI port (ENV: PORT)")

    @property
    def app_port(self) -> int:
        """Get app port from PORT env variable or default to 8000."""
        return self.port if self.port is not None else 8000

    # =====================================
    # FILE STORAGE
    # =====================================
    storage_path: str = Field("./storage", description="Storage directory path")
    max_file_size_mb: int = Field(100, description="Maximum file size in MB")
    file_retention_days: int = Field(3, description="File retention period in days")

    # =====================================
    # RATE LIMITING
    # =====================================
    free_user_rate_limit: int = Field(5, description="Free user requests per hour")
    basic_rate_limit: int = Field(100, description="Basic subscription rate limit")
    premium_rate_limit: int = Field(500, description="Premium subscription rate limit")
    global_ip_rate_limit: int = Field(1000, description="Global IP rate limit")

    # =====================================
    # REFERRAL PROGRAM
    # =====================================
    user_referral_percentage: int = Field(50, description="User referral token percentage")
    partner_referral_percentage: int = Field(10, description="Partner referral money percentage")
    min_payout_amount: int = Field(500, description="Minimum payout amount in RUB")

    # =====================================
    # AI CACHE SETTINGS
    # =====================================
    enable_ai_cache: bool = Field(True, description="Enable AI response caching")
    ai_cache_ttl_hours: int = Field(24, description="AI cache TTL in hours")

    # =====================================
    # SECURITY
    # =====================================
    secret_key: str = Field(..., description="Secret key for security features")
    cors_origins: str = Field("*", description="CORS origins")

    @field_validator("cors_origins")
    @classmethod
    def parse_cors_origins(cls, v: str) -> List[str]:
        """Parse comma-separated CORS origins."""
        if v == "*":
            return ["*"]
        return [origin.strip() for origin in v.split(",") if origin.strip()]

    # =====================================
    # MONITORING
    # =====================================
    enable_metrics: bool = Field(False, description="Enable Prometheus metrics")
    metrics_port: int = Field(9090, description="Metrics port")
    sentry_dsn: Optional[str] = Field(None, description="Sentry DSN for error tracking")

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"

    @property
    def max_file_size_bytes(self) -> int:
        """Get max file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024


# Global settings instance
settings = Settings()
