"""
Configuration management for PulseOps healthcare management system.

This module handles all application configuration including environment
variables, AWS settings, database configuration, authentication settings,
and feature flags. All configuration is environment-based with proper
validation and defaults.
"""

# flake8: noqa: E501

from functools import lru_cache
from typing import Any, Dict, List, Optional
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


class WhatsAppConfig(BaseSettings):
    """WhatsApp Business API configuration."""

    # WhatsApp Business API Settings
    whatsapp_access_token: SecretStr = Field(env="WHATSAPP_ACCESS_TOKEN")
    whatsapp_phone_number_id: str = Field(env="WHATSAPP_PHONE_NUMBER_ID")
    whatsapp_business_account_id: str = Field(env="WHATSAPP_BUSINESS_ACCOUNT_ID")
    whatsapp_api_version: str = Field(default="v18.0", env="WHATSAPP_API_VERSION")
    whatsapp_webhook_verify_token: SecretStr = Field(
        env="WHATSAPP_WEBHOOK_VERIFY_TOKEN"
    )

    # Message Templates
    registration_otp_template: str = Field(
        default="welcome_otp", env="WHATSAPP_REGISTRATION_OTP_TEMPLATE"
    )
    login_otp_template: str = Field(
        default="login_otp", env="WHATSAPP_LOGIN_OTP_TEMPLATE"
    )

    password_reset_otp_template: str = Field(
        default="password_reset_otp",
        env="WHATSAPP_PASSWORD_RESET_OTP_TEMPLATE",
    )
    appointment_reminder_template: str = Field(
        default="appointment_reminder",
        env="WHATSAPP_APPOINTMENT_REMINDER_TEMPLATE",
    )
    token_confirmation_template: str = Field(
        default="token_confirmation",
        env="WHATSAPP_TOKEN_CONFIRMATION_TEMPLATE",
    )

    # Rate Limiting
    messages_per_second: int = Field(default=5, env="WHATSAPP_MESSAGES_PER_SECOND")
    max_messages_per_day: int = Field(default=1000, env="WHATSAPP_MAX_MESSAGES_PER_DAY")

    # Webhook Settings
    webhook_path: str = Field(
        default="/api/v1/webhooks/whatsapp", env="WHATSAPP_WEBHOOK_PATH"
    )
    webhook_timeout_seconds: int = Field(default=10, env="WHATSAPP_WEBHOOK_TIMEOUT")


class PaymentConfig(BaseSettings):
    """Payment gateway configuration."""

    # UPI Payment Settings
    upi_merchant_id: str = Field(env="UPI_MERCHANT_ID")
    upi_merchant_key: SecretStr = Field(env="UPI_MERCHANT_KEY")
    upi_gateway_url: str = Field(env="UPI_GATEWAY_URL")

    # Payment Processing
    payment_timeout_seconds: int = Field(default=300, env="PAYMENT_TIMEOUT_SECONDS")
    payment_retry_attempts: int = Field(default=3, env="PAYMENT_RETRY_ATTEMPTS")

    # Currency and Formatting
    default_currency: str = Field(default="INR", env="DEFAULT_CURRENCY")
    currency_symbol: str = Field(default="₹", env="CURRENCY_SYMBOL")

    # Refund Settings
    refund_window_hours: int = Field(default=24, env="REFUND_WINDOW_HOURS")
    auto_refund_enabled: bool = Field(default=True, env="AUTO_REFUND_ENABLED")


class SubscriptionConfig(BaseSettings):
    """Subscription and billing configuration."""

    # Subscription Plans
    basic_plan_price: int = Field(default=799, env="BASIC_PLAN_PRICE")
    professional_plan_price: int = Field(default=649, env="PROFESSIONAL_PLAN_PRICE")
    enterprise_plan_price: int = Field(default=549, env="ENTERPRISE_PLAN_PRICE")

    # Plan Limits
    basic_max_doctors: int = Field(default=3, env="BASIC_MAX_DOCTORS")
    professional_max_doctors: int = Field(default=10, env="PROFESSIONAL_MAX_DOCTORS")
    enterprise_max_doctors: int = Field(default=50, env="ENTERPRISE_MAX_DOCTORS")

    # Billing Settings
    billing_cycle_days: int = Field(default=30, env="BILLING_CYCLE_DAYS")
    grace_period_days: int = Field(default=7, env="GRACE_PERIOD_DAYS")
    auto_upgrade_enabled: bool = Field(default=True, env="AUTO_UPGRADE_ENABLED")

    # Feature Flags
    analytics_enabled: bool = Field(default=True, env="ANALYTICS_ENABLED")
    custom_reports_enabled: bool = Field(default=True, env="CUSTOM_REPORTS_ENABLED")
    priority_support_enabled: bool = Field(default=True, env="PRIORITY_SUPPORT_ENABLED")


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


class NotificationConfig(BaseSettings):
    """Notification and messaging configuration."""

    # Email Settings (for admin notifications)
    email_enabled: bool = Field(default=False, env="EMAIL_ENABLED")
    email_smtp_host: str = Field(default="", env="EMAIL_SMTP_HOST")
    email_smtp_port: int = Field(default=587, env="EMAIL_SMTP_PORT")
    email_username: str = Field(default="", env="EMAIL_USERNAME")
    email_password: SecretStr = Field(default="", env="EMAIL_PASSWORD")
    email_from_address: str = Field(default="", env="EMAIL_FROM_ADDRESS")

    # SMS Settings (fallback for WhatsApp)
    sms_enabled: bool = Field(default=False, env="SMS_ENABLED")
    sms_provider: str = Field(default="", env="SMS_PROVIDER")
    sms_api_key: SecretStr = Field(default="", env="SMS_API_KEY")
    sms_sender_id: str = Field(default="", env="SMS_SENDER_ID")

    # Notification Templates
    notification_templates_path: str = Field(
        default="templates/notifications", env="NOTIFICATION_TEMPLATES_PATH"
    )


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


class Config:
    """Main configuration class that combines all configuration sections."""

    def __init__(self):
        self.app = AppConfig()
        self.database = DatabaseConfig()
        self.auth = AuthenticationConfig()
        self.whatsapp = WhatsAppConfig()
        self.payment = PaymentConfig()
        self.subscription = SubscriptionConfig()
        self.security = SecurityConfig()
        self.logging = LoggingConfig()
        self.cache = CacheConfig()
        self.notification = NotificationConfig()

    def get_all_settings(self) -> Dict[str, Any]:
        """Get all configuration settings as a dictionary."""
        return {
            "app": self.app.dict(),
            "database": self.database.dict(),
            "auth": self.auth.dict(),
            "whatsapp": self.whatsapp.dict(),
            "payment": self.payment.dict(),
            "subscription": self.subscription.dict(),
            "security": self.security.dict(),
            "logging": self.logging.dict(),
            "cache": self.cache.dict(),
            "notification": self.notification.dict(),
        }

    def validate_configuration(self) -> None:
        """Validate the complete configuration."""
        # Validate required settings for production
        if self.app.environment == "production":
            if not self.auth.jwt_secret_key.get_secret_value():
                raise ValueError("JWT secret key is required in production")
            if not self.whatsapp.whatsapp_access_token.get_secret_value():
                raise ValueError("WhatsApp access token is required in production")
            if not self.whatsapp.whatsapp_webhook_verify_token.get_secret_value():
                raise ValueError(
                    "WhatsApp webhook verify token is required in production"
                )

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.app.environment == "development"

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app.environment == "production"

    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.app.environment == "testing"


@lru_cache()
def get_config() -> Config:
    """
    Get cached configuration instance.

    Returns:
        Config: Application configuration instance

    Note:
        This function is cached to avoid reloading configuration on every call.
        Use this function to get configuration throughout the application.
    """
    config = Config()
    config.validate_configuration()
    return config


# Convenience functions for accessing specific configuration sections
def get_database_config() -> DatabaseConfig:
    """Get database configuration."""
    return get_config().database


def get_auth_config() -> AuthenticationConfig:
    """Get authentication configuration."""
    return get_config().auth


def get_whatsapp_config() -> WhatsAppConfig:
    """Get WhatsApp configuration."""
    return get_config().whatsapp


def get_payment_config() -> PaymentConfig:
    """Get payment configuration."""
    return get_config().payment


def get_subscription_config() -> SubscriptionConfig:
    """Get subscription configuration."""
    return get_config().subscription


def get_security_config() -> SecurityConfig:
    """Get security configuration."""
    return get_config().security


def get_logging_config() -> LoggingConfig:
    """Get logging configuration."""
    return get_config().logging


def get_cache_config() -> CacheConfig:
    """Get cache configuration."""
    return get_config().cache


def get_notification_config() -> NotificationConfig:
    """Get notification configuration."""
    return get_config().notification


def get_app_config() -> AppConfig:
    """Get application configuration."""
    return get_config().app


# Environment-specific configuration helpers
def is_development() -> bool:
    """Check if running in development environment."""
    return get_config().is_development()


def is_production() -> bool:
    """Check if running in production environment."""
    return get_config().is_production()


def is_testing() -> bool:
    """Check if running in testing environment."""
    return get_config().is_testing()


# Configuration validation on module import
try:
    _config = get_config()
except Exception as e:
    print(f"Configuration validation failed: {e}")
    raise
