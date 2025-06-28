"""
Payment gateway configuration for PulseOps healthcare management system.

This module handles UPI payment settings, payment processing configuration,
currency settings, and refund configuration.
"""

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings


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
