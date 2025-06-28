"""
Authentication configuration for PulseOps healthcare management system.

This module handles JWT settings, password requirements, OTP configuration,
and session management settings.
"""

from pydantic import Field, validator, SecretStr
from pydantic_settings import BaseSettings


class AuthenticationConfig(BaseSettings):
    """JWT and authentication configuration."""

    # JWT Settings
    jwt_secret_key: SecretStr = Field(env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(
        default=60,
        env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
    )
    jwt_refresh_token_expire_days: int = Field(
        default=7,
        env="JWT_REFRESH_TOKEN_EXPIRE_DAYS",
    )

    # Password Settings
    password_min_length: int = Field(default=8, env="PASSWORD_MIN_LENGTH")
    password_require_special_chars: bool = Field(
        default=True, env="PASSWORD_REQUIRE_SPECIAL_CHARS"
    )
    password_require_numbers: bool = Field(default=True, env="PASSWORD_REQUIRE_NUMBERS")
    password_require_uppercase: bool = Field(
        default=True, env="PASSWORD_REQUIRE_UPPERCASE"
    )

    # OTP Settings
    otp_length: int = Field(default=6, env="OTP_LENGTH")
    otp_expire_minutes: int = Field(default=5, env="OTP_EXPIRE_MINUTES")
    otp_max_attempts: int = Field(default=3, env="OTP_MAX_ATTEMPTS")
    otp_resend_cooldown_minutes: int = Field(
        default=2, env="OTP_RESEND_COOLDOWN_MINUTES"
    )
    otp_rate_limit_per_hour: int = Field(default=10, env="OTP_RATE_LIMIT_PER_HOUR")

    # Session Settings
    session_timeout_minutes: int = Field(
        default=480, env="SESSION_TIMEOUT_MINUTES"
    )  # 8 hours
    max_concurrent_sessions: int = Field(default=3, env="MAX_CONCURRENT_SESSIONS")

    @validator("jwt_secret_key")
    def validate_jwt_secret_key(cls, v: SecretStr) -> SecretStr:
        """Validate JWT secret key strength."""
        secret = v.get_secret_value()
        if len(secret) < 32:
            raise ValueError("JWT secret key must be at least 32 characters long")
        return v
