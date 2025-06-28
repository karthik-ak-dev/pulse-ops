"""
Subscription and billing configuration for PulseOps healthcare management.

This module handles subscription plans, pricing, plan limits, billing settings,
and feature flags for different subscription tiers.
"""

from pydantic import Field
from pydantic_settings import BaseSettings


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
