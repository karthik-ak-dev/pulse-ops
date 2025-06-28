"""
Application configuration for PulseOps healthcare management system.

This module handles main application settings, server configuration,
API settings, health checks, and feature flags.
"""

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    """Main application configuration."""

    # Application Settings
    app_name: str = Field(default="PulseOps API", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    app_description: str = Field(
        default="Healthcare Management System API", env="APP_DESCRIPTION"
    )
    debug: bool = Field(default=False, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")

    # Server Settings
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    workers: int = Field(default=1, env="WORKERS")

    # API Settings
    api_prefix: str = Field(default="/api/v1", env="API_PREFIX")
    docs_url: str = Field(default="/docs", env="DOCS_URL")
    redoc_url: str = Field(default="/redoc", env="REDOC_URL")

    # Health Check
    health_check_path: str = Field(default="/health", env="HEALTH_CHECK_PATH")
    health_check_interval_seconds: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")

    # Feature Flags
    real_time_updates_enabled: bool = Field(
        default=True, env="REAL_TIME_UPDATES_ENABLED"
    )
    analytics_enabled: bool = Field(default=True, env="ANALYTICS_ENABLED")
    webhook_processing_enabled: bool = Field(
        default=True, env="WEBHOOK_PROCESSING_ENABLED"
    )

    @validator("environment")
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        valid_environments = ["development", "staging", "production", "testing"]
        if v not in valid_environments:
            raise ValueError(f"Invalid environment: {v}")
        return v
