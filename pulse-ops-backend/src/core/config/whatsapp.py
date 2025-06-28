"""
WhatsApp Business API configuration for PulseOps healthcare management system.

This module handles WhatsApp Business API settings, message templates,
rate limiting, and webhook configuration.
"""

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings


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
