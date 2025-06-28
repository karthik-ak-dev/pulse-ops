"""
Caching configuration for PulseOps healthcare management system.

This module handles Redis settings, cache TTL configuration,
and cache key management.
"""

from typing import Optional
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings


class CacheConfig(BaseSettings):
    """Caching configuration."""

    # Redis Settings
    redis_enabled: bool = Field(default=False, env="REDIS_ENABLED")
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_password: Optional[SecretStr] = Field(default=None, env="REDIS_PASSWORD")
    redis_db: int = Field(default=0, env="REDIS_DB")

    # Cache TTL Settings
    session_cache_ttl_seconds: int = Field(
        default=1800, env="SESSION_CACHE_TTL_SECONDS"
    )  # 30 minutes
    otp_cache_ttl_seconds: int = Field(
        default=300, env="OTP_CACHE_TTL_SECONDS"
    )  # 5 minutes
    user_cache_ttl_seconds: int = Field(
        default=3600, env="USER_CACHE_TTL_SECONDS"
    )  # 1 hour
    queue_cache_ttl_seconds: int = Field(
        default=60, env="QUEUE_CACHE_TTL_SECONDS"
    )  # 1 minute

    # Cache Keys
    cache_key_prefix: str = Field(default="pulseops", env="CACHE_KEY_PREFIX")
