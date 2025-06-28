"""
Security configuration for PulseOps healthcare management system.

This module handles CORS settings, rate limiting, API security,
audit logging, and data privacy configuration.
"""

from typing import Any, List
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class SecurityConfig(BaseSettings):
    """Security and access control configuration."""

    # CORS Settings
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        env="CORS_ALLOW_METHODS",
    )
    cors_allow_headers: List[str] = Field(default=["*"], env="CORS_ALLOW_HEADERS")

    # Rate Limiting
    rate_limit_requests_per_minute: int = Field(
        default=60, env="RATE_LIMIT_REQUESTS_PER_MINUTE"
    )
    rate_limit_burst_size: int = Field(default=100, env="RATE_LIMIT_BURST_SIZE")

    # API Security
    api_key_header: str = Field(default="X-API-Key", env="API_KEY_HEADER")
    api_key_required: bool = Field(default=False, env="API_KEY_REQUIRED")

    # Audit Logging
    audit_log_enabled: bool = Field(default=True, env="AUDIT_LOG_ENABLED")
    audit_log_retention_days: int = Field(default=365, env="AUDIT_LOG_RETENTION_DAYS")

    # Data Privacy
    data_encryption_enabled: bool = Field(default=True, env="DATA_ENCRYPTION_ENABLED")
    pii_masking_enabled: bool = Field(default=True, env="PII_MASKING_ENABLED")

    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v: Any) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
