"""
Constants for the PulseOps healthcare management system.

This module contains all application-wide constants including:
- User roles and permissions
- Subscription plans and pricing
- Queue and token statuses
- Database table names and indexes
- API response codes and messages
- WhatsApp message templates
- Medical and healthcare constants
"""

# flake8: noqa: E501

from enum import Enum
from typing import List


# Note: User roles and permissions are now defined in src/core/permissions.py
# This provides comprehensive RBAC with data isolation and healthcare privacy compliance

# Note: Security utilities (JWT, password hashing, OTP, encryption) are in src/core/security.py
# This provides comprehensive security features including authentication, data protection, and audit logging


# =============================================================================
# SUBSCRIPTION PLANS & PRICING
# =============================================================================


class SubscriptionPlan(str, Enum):
    """Available subscription plans."""

    BASIC = "BASIC"
    PROFESSIONAL = "PROFESSIONAL"
    ENTERPRISE = "ENTERPRISE"


class BillingCycle(str, Enum):
    """Billing cycle options."""

    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    YEARLY = "YEARLY"


class SubscriptionStatus(str, Enum):
    """Subscription status."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    EXPIRED = "EXPIRED"
    PENDING = "PENDING"


# Subscription plan configurations
SUBSCRIPTION_PLANS = {
    SubscriptionPlan.BASIC: {
        "name": "Basic",
        "price_per_doctor": 799,
        "max_doctors": 3,
        "features": ["Basic dashboard", "WhatsApp notifications", "Standard support"],
    },
    SubscriptionPlan.PROFESSIONAL: {
        "name": "Professional",
        "price_per_doctor": 649,
        "max_doctors": 10,
        "features": [
            "Advanced analytics",
            "Multi-user access",
            "Priority support",
            "Custom reports",
        ],
    },
    SubscriptionPlan.ENTERPRISE: {
        "name": "Enterprise",
        "price_per_doctor": 549,
        "max_doctors": 50,
        "features": [
            "Unlimited features",
            "Dedicated support",
            "Custom integrations",
            "White-label options",
        ],
    },
}


# =============================================================================
# CLINIC & DOCTOR STATUS
# =============================================================================


class ClinicStatus(str, Enum):
    """Clinic status."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    PENDING = "PENDING"


class DoctorStatus(str, Enum):
    """Doctor status."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    ON_LEAVE = "ON_LEAVE"


# =============================================================================
# QUEUE MANAGEMENT
# =============================================================================


class QueueStatus(str, Enum):
    """Queue status for daily operations."""

    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    EMERGENCY = "EMERGENCY"
    CLOSED = "CLOSED"
    NOT_STARTED = "NOT_STARTED"


class PauseReason(str, Enum):
    """Reasons for queue pause."""

    LUNCH_BREAK = "LUNCH_BREAK"
    EMERGENCY = "EMERGENCY"
    TECHNICAL_ISSUE = "TECHNICAL_ISSUE"
    DOCTOR_UNAVAILABLE = "DOCTOR_UNAVAILABLE"
    OTHER = "OTHER"


# =============================================================================
# TOKEN MANAGEMENT
# =============================================================================


class TokenStatus(str, Enum):
    """Token status for patient bookings."""

    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CURRENT = "CURRENT"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    SKIPPED = "SKIPPED"
    NO_SHOW = "NO_SHOW"


class ConsultationType(str, Enum):
    """Types of medical consultations."""

    GENERAL = "GENERAL"
    SPECIALIST = "SPECIALIST"
    FOLLOW_UP = "FOLLOW_UP"
    EMERGENCY = "EMERGENCY"
    REVIEW = "REVIEW"


class PaymentStatus(str, Enum):
    """Payment status for tokens."""

    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"
    CANCELLED = "CANCELLED"


# =============================================================================
# PATIENT MANAGEMENT
# =============================================================================


class Gender(str, Enum):
    """Patient gender."""

    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"
    PREFER_NOT_TO_SAY = "PREFER_NOT_TO_SAY"


class BloodGroup(str, Enum):
    """Blood group types."""

    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"


class AssociationStatus(str, Enum):
    """Doctor-patient association status."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    TERMINATED = "TERMINATED"


# =============================================================================
# VISIT RECORDS & MEDICAL NOTES
# =============================================================================


class VisitStatus(str, Enum):
    """Visit record status."""

    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"


class DiagnosisSeverity(str, Enum):
    """Diagnosis severity levels."""

    MILD = "MILD"
    MODERATE = "MODERATE"
    SEVERE = "SEVERE"
    CRITICAL = "CRITICAL"


class MedicationFrequency(str, Enum):
    """Medication frequency options."""

    ONCE_DAILY = "Once daily"
    TWICE_DAILY = "Twice daily"
    THREE_TIMES_DAILY = "Three times daily"
    FOUR_TIMES_DAILY = "Four times daily"
    AS_NEEDED = "As needed"
    BEFORE_MEALS = "Before meals"
    AFTER_MEALS = "After meals"
    AT_BEDTIME = "At bedtime"


# =============================================================================
# WHATSAPP INTEGRATION
# =============================================================================


class OTPRequestType(str, Enum):
    """Types of OTP requests."""

    REGISTRATION = "REGISTRATION"
    LOGIN = "LOGIN"
    PASSWORD_RESET = "PASSWORD_RESET"


class OTPStatus(str, Enum):
    """OTP request status."""

    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    EXPIRED = "EXPIRED"
    FAILED = "FAILED"


class WhatsAppMessageType(str, Enum):
    """Types of WhatsApp messages."""

    TEXT = "text"
    TEMPLATE = "template"
    MEDIA = "media"
    INTERACTIVE = "interactive"


class WhatsAppTemplateCategory(str, Enum):
    """WhatsApp template categories."""

    UTILITY = "UTILITY"
    MARKETING = "MARKETING"
    AUTHENTICATION = "AUTHENTICATION"


# =============================================================================
# API CONSTANTS
# =============================================================================

# HTTP status codes
HTTP_STATUS = {
    "OK": 200,
    "CREATED": 201,
    "NO_CONTENT": 204,
    "BAD_REQUEST": 400,
    "UNAUTHORIZED": 401,
    "FORBIDDEN": 403,
    "NOT_FOUND": 404,
    "CONFLICT": 409,
    "UNPROCESSABLE_ENTITY": 422,
    "INTERNAL_SERVER_ERROR": 500,
    "SERVICE_UNAVAILABLE": 503,
}

# API response messages
API_MESSAGES = {
    "SUCCESS": "Success",
    "CREATED": "Created successfully",
    "UPDATED": "Updated successfully",
    "DELETED": "Deleted successfully",
    "NOT_FOUND": "Resource not found",
    "UNAUTHORIZED": "Unauthorized access",
    "FORBIDDEN": "Access forbidden",
    "VALIDATION_ERROR": "Validation error",
    "INTERNAL_ERROR": "Internal server error",
    "SERVICE_UNAVAILABLE": "Service temporarily unavailable",
}

# Pagination defaults
PAGINATION = {
    "DEFAULT_PAGE_SIZE": 20,
    "MAX_PAGE_SIZE": 100,
    "DEFAULT_PAGE": 1,
}

# Rate limiting
RATE_LIMITS = {
    "OTP_REQUESTS_PER_HOUR": 5,
    "LOGIN_ATTEMPTS_PER_HOUR": 10,
    "API_REQUESTS_PER_MINUTE": 100,
}

# =============================================================================
# TIME & DATE CONSTANTS
# =============================================================================


class TimeSlot(str, Enum):
    """Time slot preferences."""

    MORNING = "MORNING"
    AFTERNOON = "AFTERNOON"
    EVENING = "EVENING"


class CommunicationMethod(str, Enum):
    """Preferred communication methods."""

    WHATSAPP = "WHATSAPP"
    SMS = "SMS"
    CALL = "CALL"
    EMAIL = "EMAIL"


# Default time formats
TIME_FORMATS = {
    "DISPLAY": "%H:%M",
    "DATETIME": "%Y-%m-%dT%H:%M:%SZ",
    "DATE": "%Y-%m-%d",
    "TIME": "%H:%M:%S",
}

# Default consultation duration (minutes)
DEFAULT_CONSULTATION_DURATION = 15

# Default queue hours
DEFAULT_QUEUE_HOURS = {
    "START_TIME": "09:00",
    "END_TIME": "17:00",
    "LUNCH_BREAK_START": "13:00",
    "LUNCH_BREAK_END": "14:00",
}


# =============================================================================
# WHATSAPP MESSAGE TEMPLATES
# =============================================================================

WHATSAPP_TEMPLATES = {
    "CLINIC_REGISTRATION": {
        "name": "clinic_registration",
        "language": "en",
        "category": "UTILITY",
        "components": [
            {"type": "HEADER", "text": "Welcome to PulseOps!"},
            {
                "type": "BODY",
                "text": "Your clinic registration OTP is: {{otp}}. Valid for 5 minutes.",
            },
        ],
    },
    "LOGIN_OTP": {
        "name": "login_otp",
        "language": "en",
        "category": "AUTHENTICATION",
        "components": [
            {"type": "HEADER", "text": "PulseOps Login"},
            {
                "type": "BODY",
                "text": "Your login OTP is: {{otp}}. Valid for 5 minutes.",
            },
        ],
    },
    "PASSWORD_RESET": {
        "name": "password_reset",
        "language": "en",
        "category": "AUTHENTICATION",
        "components": [
            {"type": "HEADER", "text": "Password Reset"},
            {
                "type": "BODY",
                "text": "Your password reset OTP is: {{otp}}. Valid for 5 minutes.",
            },
        ],
    },
    "TOKEN_CONFIRMATION": {
        "name": "token_confirmation",
        "language": "en",
        "category": "UTILITY",
        "components": [
            {"type": "HEADER", "text": "Token Confirmed"},
            {
                "type": "BODY",
                "text": "Your token {{token_number}} has been confirmed for {{appointment_time}} with {{doctor_name}}. Payment of ₹{{amount}} received.",
            },
        ],
    },
    "APPOINTMENT_REMINDER": {
        "name": "appointment_reminder",
        "language": "en",
        "category": "UTILITY",
        "components": [
            {"type": "HEADER", "text": "Appointment Reminder"},
            {
                "type": "BODY",
                "text": "Hello {{patient_name}}, your appointment with {{doctor_name}} is scheduled for {{appointment_time}}. Your token number is {{token_number}}. Please arrive 10 minutes early.",
            },
        ],
    },
    "QUEUE_UPDATE": {
        "name": "queue_update",
        "language": "en",
        "category": "UTILITY",
        "components": [
            {"type": "HEADER", "text": "Queue Update"},
            {
                "type": "BODY",
                "text": "Currently serving: {{current_token}}. Your turn in ~{{estimated_wait}} minutes (Token {{your_token}}).",
            },
        ],
    },
    "CLINIC_ANNOUNCEMENT": {
        "name": "clinic_announcement",
        "language": "en",
        "category": "UTILITY",
        "components": [
            {"type": "HEADER", "text": "Clinic Announcement"},
            {"type": "BODY", "text": "{{clinic_name}}: {{announcement}}"},
        ],
    },
}

# =============================================================================
# LOGGING CONSTANTS
# =============================================================================


class LogLevel(str, Enum):
    """Log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogCategory(str, Enum):
    """Log categories for structured logging."""

    AUTHENTICATION = "AUTHENTICATION"
    QUEUE_MANAGEMENT = "QUEUE_MANAGEMENT"
    PATIENT_MANAGEMENT = "PATIENT_MANAGEMENT"
    PAYMENT = "PAYMENT"
    WHATSAPP = "WHATSAPP"
    DATABASE = "DATABASE"
    API = "API"
    SECURITY = "SECURITY"


# =============================================================================
# ENVIRONMENT CONSTANTS
# =============================================================================


class Environment(str, Enum):
    """Application environments."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


# AWS service names
AWS_SERVICES = {
    "DYNAMODB": "dynamodb",
    "LAMBDA": "lambda",
    "API_GATEWAY": "apigateway",
    "EVENTBRIDGE": "eventbridge",
    "CLOUDWATCH": "cloudwatch",
    "PARAMETER_STORE": "ssm",
    "SECRETS_MANAGER": "secretsmanager",
    "S3": "s3",
}

# External service names
EXTERNAL_SERVICES = {
    "WHATSAPP": "whatsapp",
    "STRIPE": "stripe",
    "TWILIO": "twilio",
    "UPI": "upi",
}
