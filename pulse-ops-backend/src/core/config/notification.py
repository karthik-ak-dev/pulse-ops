"""
Notification and messaging configuration for PulseOps healthcare management.

This module handles email settings, SMS settings (fallback for WhatsApp),
and notification template configuration.
"""

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings


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
