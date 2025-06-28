"""
Logging and monitoring configuration for PulseOps healthcare management system.

This module handles log levels, CloudWatch settings, structured logging,
and performance monitoring configuration.
"""

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class LoggingConfig(BaseSettings):
    """Logging and monitoring configuration."""

    # Log Levels
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT",
    )

    # CloudWatch Settings
    cloudwatch_enabled: bool = Field(default=True, env="CLOUDWATCH_ENABLED")
    cloudwatch_log_group: str = Field(
        default="pulseops-api", env="CLOUDWATCH_LOG_GROUP"
    )
    cloudwatch_region: str = Field(default="ap-south-1", env="CLOUDWATCH_REGION")

    # Structured Logging
    structured_logging_enabled: bool = Field(
        default=True, env="STRUCTURED_LOGGING_ENABLED"
    )
    correlation_id_header: str = Field(
        default="X-Correlation-ID", env="CORRELATION_ID_HEADER"
    )

    # Performance Monitoring
    performance_monitoring_enabled: bool = Field(
        default=True, env="PERFORMANCE_MONITORING_ENABLED"
    )
    slow_query_threshold_ms: int = Field(default=1000, env="SLOW_QUERY_THRESHOLD_MS")

    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {v}")
        return v.upper()
