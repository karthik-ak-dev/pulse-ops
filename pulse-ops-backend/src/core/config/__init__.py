"""
Configuration package for PulseOps healthcare management system.

This module provides a centralized configuration management system
that combines all configuration sections and provides utility functions
for accessing configuration throughout the application.
"""

from functools import lru_cache
from typing import Any, Dict

from .app import AppConfig
from .auth import AuthenticationConfig
from .cache import CacheConfig
from .database import DatabaseConfig
from .logging import LoggingConfig
from .notification import NotificationConfig
from .payment import PaymentConfig
from .security import SecurityConfig
from .subscription import SubscriptionConfig
from .whatsapp import WhatsAppConfig

# Export all configuration classes
__all__ = [
    "AppConfig",
    "AuthenticationConfig",
    "CacheConfig",
    "DatabaseConfig",
    "LoggingConfig",
    "NotificationConfig",
    "PaymentConfig",
    "SecurityConfig",
    "SubscriptionConfig",
    "WhatsAppConfig",
    "Config",
    "get_config",
    "get_app_config",
    "get_auth_config",
    "get_cache_config",
    "get_database_config",
    "get_logging_config",
    "get_notification_config",
    "get_payment_config",
    "get_security_config",
    "get_subscription_config",
    "get_whatsapp_config",
    "is_development",
    "is_production",
    "is_testing",
]


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
