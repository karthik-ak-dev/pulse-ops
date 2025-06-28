"""
Custom exceptions for the PulseOps healthcare management system.

This module provides centralized exception handling with custom exception
classes, error codes, HTTP status mappings, and error response formatting.
All exceptions include proper error codes, messages, and context for
debugging and user feedback.
"""

# flake8: noqa: E501

from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status
from enum import Enum


class ErrorCode(str, Enum):
    """Application-specific error codes for PulseOps."""

    # Authentication errors
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INVALID_TOKEN = "INVALID_TOKEN"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    OTP_EXPIRED = "OTP_EXPIRED"
    OTP_INVALID = "OTP_INVALID"
    OTP_MAX_ATTEMPTS = "OTP_MAX_ATTEMPTS"
    OTP_RATE_LIMIT_EXCEEDED = "OTP_RATE_LIMIT_EXCEEDED"
    ACCOUNT_LOCKED = "ACCOUNT_LOCKED"
    PASSWORD_RESET_REQUIRED = "PASSWORD_RESET_REQUIRED"

    # Resource errors
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_ALREADY_EXISTS = "RESOURCE_ALREADY_EXISTS"
    RESOURCE_IN_USE = "RESOURCE_IN_USE"
    RESOURCE_DELETED = "RESOURCE_DELETED"
    RESOURCE_EXPIRED = "RESOURCE_EXPIRED"

    # Business logic errors
    QUEUE_NOT_ACTIVE = "QUEUE_NOT_ACTIVE"
    QUEUE_ALREADY_STARTED = "QUEUE_ALREADY_STARTED"
    QUEUE_ALREADY_CLOSED = "QUEUE_ALREADY_CLOSED"
    TOKEN_ALREADY_COMPLETED = "TOKEN_ALREADY_COMPLETED"
    TOKEN_ALREADY_CANCELLED = "TOKEN_ALREADY_CANCELLED"
    DOCTOR_LIMIT_EXCEEDED = "DOCTOR_LIMIT_EXCEEDED"
    PATIENT_NOT_ASSOCIATED = "PATIENT_NOT_ASSOCIATED"
    PATIENT_ALREADY_ASSOCIATED = "PATIENT_ALREADY_ASSOCIATED"
    INVALID_QUEUE_STATUS = "INVALID_QUEUE_STATUS"
    INVALID_TOKEN_STATUS = "INVALID_TOKEN_STATUS"
    CONSULTATION_IN_PROGRESS = "CONSULTATION_IN_PROGRESS"
    APPOINTMENT_TIME_CONFLICT = "APPOINTMENT_TIME_CONFLICT"

    # Subscription and billing errors
    SUBSCRIPTION_EXPIRED = "SUBSCRIPTION_EXPIRED"
    SUBSCRIPTION_SUSPENDED = "SUBSCRIPTION_SUSPENDED"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    PAYMENT_REQUIRED = "PAYMENT_REQUIRED"
    BILLING_CYCLE_ERROR = "BILLING_CYCLE_ERROR"
    PLAN_DOWNGRADE_RESTRICTED = "PLAN_DOWNGRADE_RESTRICTED"

    # Validation errors
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INVALID_FORMAT = "INVALID_FORMAT"
    INVALID_PHONE_NUMBER = "INVALID_PHONE_NUMBER"
    INVALID_DATE_RANGE = "INVALID_DATE_RANGE"
    INVALID_TIME_SLOT = "INVALID_TIME_SLOT"
    DUPLICATE_ENTRY = "DUPLICATE_ENTRY"
    DATA_INTEGRITY_ERROR = "DATA_INTEGRITY_ERROR"

    # External service errors
    WHATSAPP_SERVICE_ERROR = "WHATSAPP_SERVICE_ERROR"
    WHATSAPP_RATE_LIMIT = "WHATSAPP_RATE_LIMIT"
    PAYMENT_SERVICE_ERROR = "PAYMENT_SERVICE_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    EXTERNAL_API_ERROR = "EXTERNAL_API_ERROR"
    SMS_SERVICE_ERROR = "SMS_SERVICE_ERROR"

    # System errors
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    MAINTENANCE_MODE = "MAINTENANCE_MODE"

    # Security errors
    SECURITY_ERROR = "SECURITY_ERROR"
    ENCRYPTION_ERROR = "ENCRYPTION_ERROR"
    DECRYPTION_ERROR = "DECRYPTION_ERROR"


class PulseOpsException(Exception):
    """Base exception class for all PulseOps-specific exceptions."""

    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        http_status: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ):
        """
        Initialize PulseOps exception.

        Args:
            error_code: Application-specific error code
            message: Human-readable error message
            details: Additional error context and details
            http_status: HTTP status code for API responses
        """
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        self.http_status = http_status
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "success": False,
            "error": {
                "code": self.error_code.value,
                "message": self.message,
                "details": self.details,
            },
        }


# Authentication Exceptions
class AuthenticationError(PulseOpsException):
    """Base class for authentication-related errors."""

    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            error_code=error_code,
            message=message,
            details=details,
            http_status=status.HTTP_401_UNAUTHORIZED,
        )


class InvalidCredentialsError(AuthenticationError):
    """Raised when login credentials are invalid."""

    def __init__(self, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            error_code=ErrorCode.INVALID_CREDENTIALS,
            message="Invalid WhatsApp number or password",
            details=details,
        )


class TokenExpiredError(AuthenticationError):
    """Raised when JWT token has expired."""

    def __init__(self, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            error_code=ErrorCode.TOKEN_EXPIRED,
            message="Access token has expired. Please login again",
            details=details,
        )


class InvalidTokenError(AuthenticationError):
    """Raised when JWT token is invalid or malformed."""

    def __init__(self, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            error_code=ErrorCode.INVALID_TOKEN,
            message="Invalid or malformed access token",
            details=details,
        )


class OTPExpiredError(AuthenticationError):
    """Raised when OTP has expired."""

    def __init__(self, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            error_code=ErrorCode.OTP_EXPIRED,
            message="OTP has expired. Please request a new one",
            details=details,
        )


class OTPInvalidError(AuthenticationError):
    """Raised when OTP is incorrect."""

    def __init__(self, attempts_remaining: int = 0):
        super().__init__(
            error_code=ErrorCode.OTP_INVALID,
            message="Invalid OTP provided",
            details={"attempts_remaining": attempts_remaining},
        )


class OTPMaxAttemptsError(AuthenticationError):
    """Raised when maximum OTP attempts exceeded."""

    def __init__(self, cooldown_minutes: int = 15):
        super().__init__(
            error_code=ErrorCode.OTP_MAX_ATTEMPTS,
            message="Maximum OTP attempts exceeded",
            details={"cooldown_minutes": cooldown_minutes},
        )


# Authorization Exceptions
class AuthorizationError(PulseOpsException):
    """Base class for authorization-related errors."""

    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            error_code=error_code,
            message=message,
            details=details,
            http_status=status.HTTP_403_FORBIDDEN,
        )


class InsufficientPermissionsError(AuthorizationError):
    """Raised when user lacks required permissions."""

    def __init__(
        self,
        required_permission: str,
        user_role: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        details.update(
            {
                "required_permission": required_permission,
                "user_role": user_role,
            }
        )
        super().__init__(
            error_code=ErrorCode.INSUFFICIENT_PERMISSIONS,
            message=f"Insufficient permissions. Required: {required_permission}",
            details=details,
        )


# Resource Exceptions
class ResourceError(PulseOpsException):
    """Base class for resource-related errors."""

    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        http_status: int = status.HTTP_400_BAD_REQUEST,
    ):
        details = details or {}
        details.update(
            {
                "resource_type": resource_type,
                "resource_id": resource_id,
            }
        )
        super().__init__(
            error_code=error_code,
            message=message,
            details=details,
            http_status=http_status,
        )


class ResourceNotFoundError(ResourceError):
    """Raised when a requested resource is not found."""

    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            error_code=ErrorCode.RESOURCE_NOT_FOUND,
            message=f"{resource_type} with ID '{resource_id}' not found",
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            http_status=status.HTTP_404_NOT_FOUND,
        )


class ResourceAlreadyExistsError(ResourceError):
    """Raised when trying to create a resource that already exists."""

    def __init__(
        self,
        resource_type: str,
        identifier: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        message = f"{resource_type} with identifier '{identifier}' already exists"
        super().__init__(
            error_code=ErrorCode.RESOURCE_ALREADY_EXISTS,
            message=message,
            resource_type=resource_type,
            resource_id=identifier,
            details=details,
            http_status=status.HTTP_409_CONFLICT,
        )


class ResourceInUseError(ResourceError):
    """Raised when trying to delete a resource that is in use."""

    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        used_by: List[str],
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        details["used_by"] = used_by
        super().__init__(
            error_code=ErrorCode.RESOURCE_IN_USE,
            message=f"{resource_type} '{resource_id}' is currently in use",
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            http_status=status.HTTP_409_CONFLICT,
        )


# Business Logic Exceptions
class BusinessLogicError(PulseOpsException):
    """Base class for business logic violations."""

    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            error_code=error_code,
            message=message,
            details=details,
            http_status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class QueueNotActiveError(BusinessLogicError):
    """Raised when trying to operate on inactive queue."""

    def __init__(self, queue_status: str, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        details["current_status"] = queue_status
        super().__init__(
            error_code=ErrorCode.QUEUE_NOT_ACTIVE,
            message=f"Queue is not active. Current status: {queue_status}",
            details=details,
        )


class TokenAlreadyCompletedError(BusinessLogicError):
    """Raised when trying to modify a completed token."""

    def __init__(self, token_id: str, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        details["token_id"] = token_id
        super().__init__(
            error_code=ErrorCode.TOKEN_ALREADY_COMPLETED,
            message=f"Token {token_id} has already been completed",
            details=details,
        )


class DoctorLimitExceededError(BusinessLogicError):
    """Raised when clinic exceeds doctor limit for subscription plan."""

    def __init__(
        self,
        current_count: int,
        max_allowed: int,
        plan_name: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        details.update(
            {
                "current_count": current_count,
                "max_allowed": max_allowed,
                "plan_name": plan_name,
            }
        )
        message = (
            f"Doctor limit exceeded. Current: {current_count}, "
            f"Max: {max_allowed} for {plan_name} plan"
        )
        super().__init__(
            error_code=ErrorCode.DOCTOR_LIMIT_EXCEEDED,
            message=message,
            details=details,
        )


class PatientNotAssociatedError(BusinessLogicError):
    """Raised when patient is not associated with doctor."""

    def __init__(
        self,
        patient_id: str,
        doctor_id: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        details.update(
            {
                "patient_id": patient_id,
                "doctor_id": doctor_id,
            }
        )
        message = f"Patient {patient_id} is not associated with doctor {doctor_id}"
        super().__init__(
            error_code=ErrorCode.PATIENT_NOT_ASSOCIATED,
            message=message,
            details=details,
        )


# Validation Exceptions
class ValidationError(PulseOpsException):
    """Base class for input validation errors."""

    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        field_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        if field_name:
            details["field_name"] = field_name
        super().__init__(
            error_code=error_code,
            message=message,
            details=details,
            http_status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class InvalidInputError(ValidationError):
    """Raised when input data is invalid."""

    def __init__(
        self,
        field_name: str,
        value: Any,
        expected_format: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        details.update(
            {
                "provided_value": str(value),
                "expected_format": expected_format,
            }
        )
        super().__init__(
            error_code=ErrorCode.INVALID_INPUT,
            message=f"Invalid input for field '{field_name}'. Expected: {expected_format}",
            field_name=field_name,
            details=details,
        )


class MissingRequiredFieldError(ValidationError):
    """Raised when required field is missing."""

    def __init__(self, field_name: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            error_code=ErrorCode.MISSING_REQUIRED_FIELD,
            message=f"Required field '{field_name}' is missing",
            field_name=field_name,
            details=details,
        )


class InvalidPhoneNumberError(ValidationError):
    """Raised when phone number format is invalid."""

    def __init__(self, phone_number: str, details: Optional[Dict[str, Any]] = None):
        details = details or {}
        details["provided_number"] = phone_number
        super().__init__(
            error_code=ErrorCode.INVALID_PHONE_NUMBER,
            message=f"Invalid phone number format: {phone_number}",
            field_name="phone_number",
            details=details,
        )


# External Service Exceptions
class ExternalServiceError(PulseOpsException):
    """Base class for external service errors."""

    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        service_name: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        details["service_name"] = service_name
        super().__init__(
            error_code=error_code,
            message=message,
            details=details,
            http_status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class WhatsAppServiceError(ExternalServiceError):
    """Raised when WhatsApp service encounters an error."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            error_code=ErrorCode.WHATSAPP_SERVICE_ERROR,
            message=f"WhatsApp service error: {message}",
            service_name="WhatsApp Business API",
            details=details,
        )


class PaymentServiceError(ExternalServiceError):
    """Raised when payment service encounters an error."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            error_code=ErrorCode.PAYMENT_SERVICE_ERROR,
            message=f"Payment service error: {message}",
            service_name="Payment Gateway",
            details=details,
        )


class DatabaseError(ExternalServiceError):
    """Raised when database operation fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            error_code=ErrorCode.DATABASE_ERROR,
            message=f"Database error: {message}",
            service_name="DynamoDB",
            details=details,
        )


# Subscription Exceptions
class SubscriptionError(PulseOpsException):
    """Base class for subscription-related errors."""

    def __init__(
        self,
        error_code: ErrorCode,
        message: str,
        clinic_id: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        details["clinic_id"] = clinic_id
        super().__init__(
            error_code=error_code,
            message=message,
            details=details,
            http_status=status.HTTP_402_PAYMENT_REQUIRED,
        )


class SubscriptionExpiredError(SubscriptionError):
    """Raised when subscription has expired."""

    def __init__(self, clinic_id: str, expired_date: str):
        super().__init__(
            error_code=ErrorCode.SUBSCRIPTION_EXPIRED,
            message="Subscription has expired. Please renew to continue using the service",
            clinic_id=clinic_id,
            details={"expired_date": expired_date},
        )


class PaymentRequiredError(SubscriptionError):
    """Raised when payment is required for service access."""

    def __init__(self, clinic_id: str, amount_due: float):
        super().__init__(
            error_code=ErrorCode.PAYMENT_REQUIRED,
            message="Payment required to access this service",
            clinic_id=clinic_id,
            details={"amount_due": amount_due},
        )


# Security Exceptions
class SecurityError(PulseOpsException):
    """Base class for security-related errors."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            error_code=ErrorCode.SECURITY_ERROR,
            message=message,
            details=details,
            http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class RateLimitExceededError(PulseOpsException):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        identifier: str,
        limit: int,
        window_seconds: int,
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        details.update(
            {
                "identifier": identifier,
                "limit": limit,
                "window_seconds": window_seconds,
                "retry_after": window_seconds,
            }
        )
        super().__init__(
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            message=f"Rate limit exceeded: {limit} requests per {window_seconds} seconds",
            details=details,
            http_status=status.HTTP_429_TOO_MANY_REQUESTS,
        )


# Utility Functions
def create_http_exception(exception: PulseOpsException) -> HTTPException:
    """
    Convert PulseOps exception to FastAPI HTTPException.

    Args:
        exception: PulseOps exception instance

    Returns:
        HTTPException: FastAPI-compatible exception
    """
    return HTTPException(
        status_code=exception.http_status,
        detail=exception.to_dict(),
    )


def handle_database_error(error: Exception) -> DatabaseError:
    """
    Convert database errors to PulseOps DatabaseError.

    Args:
        error: Original database exception

    Returns:
        DatabaseError: Standardized database error
    """
    return DatabaseError(
        message=str(error),
        details={"original_error": type(error).__name__},
    )


def handle_validation_errors(errors: List[Dict[str, Any]]) -> ValidationError:
    """
    Convert Pydantic validation errors to PulseOps ValidationError.

    Args:
        errors: List of Pydantic validation errors

    Returns:
        ValidationError: Standardized validation error
    """
    if not errors:
        return ValidationError(
            error_code=ErrorCode.INVALID_INPUT,
            message="Validation failed",
        )

    first_error = errors[0]
    field_name = ".".join(str(loc) for loc in first_error.get("loc", []))

    return InvalidInputError(
        field_name=field_name,
        value=first_error.get("input", ""),
        expected_format=first_error.get("msg", "Valid input"),
        details={"all_errors": errors},
    )


# Error message mappings for consistent responses
ERROR_MESSAGES = {
    ErrorCode.INVALID_CREDENTIALS: "Invalid WhatsApp number or password",
    ErrorCode.TOKEN_EXPIRED: "Access token has expired. Please login again",
    ErrorCode.INVALID_TOKEN: "Invalid or malformed access token",
    ErrorCode.INSUFFICIENT_PERMISSIONS: "Insufficient permissions to perform this action",
    ErrorCode.OTP_EXPIRED: "OTP has expired. Please request a new one",
    ErrorCode.OTP_INVALID: "Invalid OTP provided",
    ErrorCode.OTP_MAX_ATTEMPTS: "Maximum OTP attempts exceeded. Please try again later",
    ErrorCode.RESOURCE_NOT_FOUND: "Requested resource not found",
    ErrorCode.RESOURCE_ALREADY_EXISTS: "Resource already exists",
    ErrorCode.RESOURCE_IN_USE: "Resource is currently in use and cannot be deleted",
    ErrorCode.QUEUE_NOT_ACTIVE: "Queue is not active for this operation",
    ErrorCode.TOKEN_ALREADY_COMPLETED: "Token has already been completed",
    ErrorCode.DOCTOR_LIMIT_EXCEEDED: "Doctor limit exceeded for current subscription plan",
    ErrorCode.PATIENT_NOT_ASSOCIATED: "Patient is not associated with this doctor",
    ErrorCode.INVALID_QUEUE_STATUS: "Invalid queue status for this operation",
    ErrorCode.INVALID_INPUT: "Invalid input provided",
    ErrorCode.MISSING_REQUIRED_FIELD: "Required field is missing",
    ErrorCode.INVALID_FORMAT: "Invalid format provided",
    ErrorCode.WHATSAPP_SERVICE_ERROR: "WhatsApp service is temporarily unavailable",
    ErrorCode.PAYMENT_SERVICE_ERROR: "Payment service is temporarily unavailable",
    ErrorCode.DATABASE_ERROR: "Database operation failed",
    ErrorCode.SUBSCRIPTION_EXPIRED: "Subscription has expired",
    ErrorCode.PAYMENT_REQUIRED: "Payment required to access this service",
    ErrorCode.SECURITY_ERROR: "Security error occurred",
    ErrorCode.RATE_LIMIT_EXCEEDED: "Rate limit exceeded",
    ErrorCode.ENCRYPTION_ERROR: "Data encryption failed",
    ErrorCode.DECRYPTION_ERROR: "Data decryption failed",
}


def get_error_message(error_code: ErrorCode) -> str:
    """
    Get standard error message for error code.

    Args:
        error_code: Error code enum value

    Returns:
        str: Standard error message
    """
    return ERROR_MESSAGES.get(error_code, "An error occurred")
