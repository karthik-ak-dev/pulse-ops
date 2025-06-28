"""
Database configuration for PulseOps healthcare management system.

This module handles DynamoDB configuration including AWS settings,
table names, performance settings, and connection parameters.
"""

from typing import Optional
from pydantic import Field, validator, SecretStr
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    """DynamoDB configuration settings."""

    # AWS DynamoDB Settings
    aws_region: str = Field(default="ap-south-1", env="AWS_REGION")
    aws_access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[SecretStr] = Field(
        default=None, env="AWS_SECRET_ACCESS_KEY"
    )

    # DynamoDB Table Names
    clinics_table: str = Field(default="pulseops-clinics", env="DYNAMODB_CLINICS_TABLE")
    users_table: str = Field(default="pulseops-users", env="DYNAMODB_USERS_TABLE")
    doctors_table: str = Field(default="pulseops-doctors", env="DYNAMODB_DOCTORS_TABLE")
    patients_table: str = Field(
        default="pulseops-patients", env="DYNAMODB_PATIENTS_TABLE"
    )
    associations_table: str = Field(
        default="pulseops-associations", env="DYNAMODB_ASSOCIATIONS_TABLE"
    )
    queues_table: str = Field(default="pulseops-queues", env="DYNAMODB_QUEUES_TABLE")
    tokens_table: str = Field(default="pulseops-tokens", env="DYNAMODB_TOKENS_TABLE")
    visits_table: str = Field(default="pulseops-visits", env="DYNAMODB_VISITS_TABLE")
    subscriptions_table: str = Field(
        default="pulseops-subscriptions", env="DYNAMODB_SUBSCRIPTIONS_TABLE"
    )
    otp_requests_table: str = Field(
        default="pulseops-otp-requests", env="DYNAMODB_OTP_REQUESTS_TABLE"
    )

    # DynamoDB Performance Settings
    read_capacity_units: int = Field(default=5, env="DYNAMODB_READ_CAPACITY")
    write_capacity_units: int = Field(default=5, env="DYNAMODB_WRITE_CAPACITY")

    # Connection Settings
    max_retries: int = Field(default=3, env="DYNAMODB_MAX_RETRIES")
    timeout_seconds: int = Field(default=30, env="DYNAMODB_TIMEOUT")

    @validator("aws_region")
    def validate_aws_region(cls, v: str) -> str:
        """Validate AWS region format."""
        valid_regions = ["ap-south-1"]
        if v not in valid_regions:
            raise ValueError(f"Invalid AWS region: {v}")
        return v
