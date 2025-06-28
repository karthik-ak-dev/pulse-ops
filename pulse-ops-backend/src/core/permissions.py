"""
Permissions and access control for the PulseOps healthcare management system.

This module provides comprehensive role-based access control (RBAC) including:
- User roles and permission definitions
- Access control decorators and utilities
- Data isolation enforcement
- Healthcare privacy compliance
- JWT token permission validation
"""

# flake8: noqa: E501

from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union
from functools import wraps
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timezone
import logging

from src.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    InsufficientPermissionsError,
    TokenExpiredError,
    InvalidTokenError,
)


# =============================================================================
# USER ROLES & PERMISSIONS
# =============================================================================


class UserRole(str, Enum):
    """User roles in the PulseOps system."""

    ADMIN = "ADMIN"
    DOCTOR = "DOCTOR"


class UserStatus(str, Enum):
    """User account status."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    PENDING = "PENDING"


class Permission(str, Enum):
    """System permissions for role-based access control."""

    # =============================================================================
    # ADMIN PERMISSIONS (Full clinic access)
    # =============================================================================

    # Doctor Management
    MANAGE_DOCTORS = "manage_doctors"
    VIEW_ALL_DOCTORS = "view_all_doctors"
    ADD_DOCTOR = "add_doctor"
    EDIT_DOCTOR = "edit_doctor"
    REMOVE_DOCTOR = "remove_doctor"

    # Queue Management (All doctors)
    VIEW_ALL_QUEUES = "view_all_queues"
    MANAGE_ALL_QUEUES = "manage_all_queues"
    START_ANY_QUEUE = "start_any_queue"
    PAUSE_ANY_QUEUE = "pause_any_queue"
    CLOSE_ANY_QUEUE = "close_any_queue"

    # Patient Data Access (Clinic-wide)
    VIEW_ALL_PATIENT_ASSOCIATIONS = "view_all_patient_associations"
    VIEW_ALL_VISIT_RECORDS = "view_all_visit_records"
    VIEW_ALL_MEDICAL_NOTES = "view_all_medical_notes"
    VIEW_DOCTOR_NOTES = "view_doctor_notes"
    EXPORT_PATIENT_DATA = "export_patient_data"
    MANAGE_PATIENT_PRIVACY = "manage_patient_privacy"

    # Financial & Subscription Management
    VIEW_SUBSCRIPTION = "view_subscription"
    MANAGE_SUBSCRIPTION = "manage_subscription"
    MANAGE_PAYMENTS = "manage_payments"
    VIEW_REVENUE = "view_revenue"
    VIEW_BILLING_HISTORY = "view_billing_history"
    DOWNLOAD_REPORTS = "download_reports"
    MANAGE_PRICING = "manage_pricing"

    # System Administration
    CONFIGURE_WHATSAPP = "configure_whatsapp"
    MANAGE_SETTINGS = "manage_settings"
    MANAGE_USERS = "manage_users"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    MANAGE_CLINIC_PROFILE = "manage_clinic_profile"

    # Analytics & Reporting (Clinic-wide)
    VIEW_CLINIC_ANALYTICS = "view_clinic_analytics"
    VIEW_DOCTOR_PERFORMANCE = "view_doctor_performance"
    GENERATE_REPORTS = "generate_reports"
    EXPORT_ANALYTICS = "export_analytics"

    # =============================================================================
    # DOCTOR PERMISSIONS (Limited to own patients and queue)
    # =============================================================================

    # Own Queue Management
    VIEW_OWN_QUEUE = "view_own_queue"
    MANAGE_OWN_QUEUE = "manage_own_queue"
    START_OWN_QUEUE = "start_own_queue"
    PAUSE_OWN_QUEUE = "pause_own_queue"
    CLOSE_OWN_QUEUE = "close_own_queue"
    CALL_NEXT_PATIENT = "call_next_patient"
    SKIP_PATIENT = "skip_patient"

    # Own Token Management
    MANAGE_OWN_TOKENS = "manage_own_tokens"
    CREATE_TOKEN = "create_token"
    UPDATE_TOKEN_STATUS = "update_token_status"
    CANCEL_TOKEN = "cancel_token"
    VIEW_TOKEN_HISTORY = "view_token_history"

    # Own Patient Management
    VIEW_OWN_PATIENTS = "view_own_patients"
    MANAGE_OWN_PATIENT_ASSOCIATIONS = "manage_own_patient_associations"
    ADD_PATIENT_ASSOCIATION = "add_patient_association"
    UPDATE_PATIENT_ASSOCIATION = "update_patient_association"
    REMOVE_PATIENT_ASSOCIATION = "remove_patient_association"

    # Medical Documentation (Own patients only)
    ADD_VISIT_NOTES = "add_visit_notes"
    EDIT_VISIT_NOTES = "edit_visit_notes"
    ADD_DIAGNOSIS = "add_diagnosis"
    EDIT_DIAGNOSIS = "edit_diagnosis"
    ADD_PRESCRIPTION = "add_prescription"
    EDIT_PRESCRIPTION = "edit_prescription"
    ADD_PRIVATE_NOTES = "add_private_notes"
    VIEW_OWN_VISIT_HISTORY = "view_own_visit_history"

    # Own Performance & Statistics
    VIEW_OWN_STATISTICS = "view_own_statistics"
    VIEW_OWN_PERFORMANCE = "view_own_performance"
    VIEW_OWN_REVENUE = "view_own_revenue"

    # Patient Communication
    SEND_PATIENT_MESSAGES = "send_patient_messages"
    MANAGE_PATIENT_NOTIFICATIONS = "manage_patient_notifications"

    # =============================================================================
    # RESTRICTED PERMISSIONS (What doctors CANNOT do)
    # =============================================================================

    # These are explicitly denied to doctors for data isolation
    VIEW_OTHER_DOCTOR_PATIENTS = "view_other_doctor_patients"
    VIEW_OTHER_DOCTOR_NOTES = "view_other_doctor_notes"
    VIEW_CROSS_CLINIC_PATIENT_DATA = "view_cross_clinic_patient_data"
    MANAGE_OTHER_QUEUES = "manage_other_queues"
    VIEW_OTHER_DOCTOR_REVENUE = "view_other_doctor_revenue"


# =============================================================================
# PERMISSION MAPPINGS FOR EACH ROLE
# =============================================================================

ADMIN_PERMISSIONS: Set[Permission] = {
    # Doctor Management
    Permission.MANAGE_DOCTORS,
    Permission.VIEW_ALL_DOCTORS,
    Permission.ADD_DOCTOR,
    Permission.EDIT_DOCTOR,
    Permission.REMOVE_DOCTOR,
    # Queue Management (All doctors)
    Permission.VIEW_ALL_QUEUES,
    Permission.MANAGE_ALL_QUEUES,
    Permission.START_ANY_QUEUE,
    Permission.PAUSE_ANY_QUEUE,
    Permission.CLOSE_ANY_QUEUE,
    # Patient Data Access (Clinic-wide)
    Permission.VIEW_ALL_PATIENT_ASSOCIATIONS,
    Permission.VIEW_ALL_VISIT_RECORDS,
    Permission.VIEW_ALL_MEDICAL_NOTES,
    Permission.VIEW_DOCTOR_NOTES,
    Permission.EXPORT_PATIENT_DATA,
    Permission.MANAGE_PATIENT_PRIVACY,
    # Financial & Subscription Management
    Permission.VIEW_SUBSCRIPTION,
    Permission.MANAGE_SUBSCRIPTION,
    Permission.MANAGE_PAYMENTS,
    Permission.VIEW_REVENUE,
    Permission.VIEW_BILLING_HISTORY,
    Permission.DOWNLOAD_REPORTS,
    Permission.MANAGE_PRICING,
    # System Administration
    Permission.CONFIGURE_WHATSAPP,
    Permission.MANAGE_SETTINGS,
    Permission.MANAGE_USERS,
    Permission.VIEW_AUDIT_LOGS,
    Permission.MANAGE_CLINIC_PROFILE,
    # Analytics & Reporting (Clinic-wide)
    Permission.VIEW_CLINIC_ANALYTICS,
    Permission.VIEW_DOCTOR_PERFORMANCE,
    Permission.GENERATE_REPORTS,
    Permission.EXPORT_ANALYTICS,
}

DOCTOR_PERMISSIONS: Set[Permission] = {
    # Own Queue Management
    Permission.VIEW_OWN_QUEUE,
    Permission.MANAGE_OWN_QUEUE,
    Permission.START_OWN_QUEUE,
    Permission.PAUSE_OWN_QUEUE,
    Permission.CLOSE_OWN_QUEUE,
    Permission.CALL_NEXT_PATIENT,
    Permission.SKIP_PATIENT,
    # Own Token Management
    Permission.MANAGE_OWN_TOKENS,
    Permission.CREATE_TOKEN,
    Permission.UPDATE_TOKEN_STATUS,
    Permission.CANCEL_TOKEN,
    Permission.VIEW_TOKEN_HISTORY,
    # Own Patient Management
    Permission.VIEW_OWN_PATIENTS,
    Permission.MANAGE_OWN_PATIENT_ASSOCIATIONS,
    Permission.ADD_PATIENT_ASSOCIATION,
    Permission.UPDATE_PATIENT_ASSOCIATION,
    Permission.REMOVE_PATIENT_ASSOCIATION,
    # Medical Documentation (Own patients only)
    Permission.ADD_VISIT_NOTES,
    Permission.EDIT_VISIT_NOTES,
    Permission.ADD_DIAGNOSIS,
    Permission.EDIT_DIAGNOSIS,
    Permission.ADD_PRESCRIPTION,
    Permission.EDIT_PRESCRIPTION,
    Permission.ADD_PRIVATE_NOTES,
    Permission.VIEW_OWN_VISIT_HISTORY,
    # Own Performance & Statistics
    Permission.VIEW_OWN_STATISTICS,
    Permission.VIEW_OWN_PERFORMANCE,
    Permission.VIEW_OWN_REVENUE,
    # Patient Communication
    Permission.SEND_PATIENT_MESSAGES,
    Permission.MANAGE_PATIENT_NOTIFICATIONS,
}

# Explicitly denied permissions for doctors (for clarity and security)
DOCTOR_DENIED_PERMISSIONS: Set[Permission] = {
    Permission.VIEW_OTHER_DOCTOR_PATIENTS,
    Permission.VIEW_OTHER_DOCTOR_NOTES,
    Permission.VIEW_CROSS_CLINIC_PATIENT_DATA,
    Permission.MANAGE_OTHER_QUEUES,
    Permission.VIEW_OTHER_DOCTOR_REVENUE,
    Permission.MANAGE_DOCTORS,
    Permission.MANAGE_SUBSCRIPTION,
    Permission.VIEW_REVENUE,
    Permission.MANAGE_SETTINGS,
    Permission.CONFIGURE_WHATSAPP,
}


# =============================================================================
# DATA ACCESS SCOPES
# =============================================================================


class DataAccessScope(str, Enum):
    """Data access scope for users."""

    CLINIC_ALL = "CLINIC_ALL"  # Admin: All clinic data
    DOCTOR_OWN = "DOCTOR_OWN"  # Doctor: Only own patients and data
    PATIENT_SELF = "PATIENT_SELF"  # Future: Patient self-access


# =============================================================================
# JWT TOKEN STRUCTURE & VALIDATION
# =============================================================================


class JWTPayload:
    """JWT token payload structure for PulseOps."""

    def __init__(self, token_data: Dict[str, Any]):
        self.user_id: str = token_data.get("user_id", "")
        self.clinic_id: str = token_data.get("clinic_id", "")
        self.whatsapp_number: str = token_data.get("whatsapp_number", "")
        self.doctor_id: Optional[str] = token_data.get("doctor_id")
        self.role: UserRole = UserRole(token_data.get("role", ""))
        self.permissions: Set[Permission] = {
            Permission(p) for p in token_data.get("permissions", [])
        }
        self.patient_access_scope: DataAccessScope = DataAccessScope(
            token_data.get("patient_access_scope", "")
        )
        self.exp: int = token_data.get("exp", 0)
        self.iat: int = token_data.get("iat", 0)
        self.iss: str = token_data.get("iss", "")

    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.now(timezone.utc).timestamp() > self.exp

    def is_admin(self) -> bool:
        """Check if user is admin."""
        return self.role == UserRole.ADMIN

    def is_doctor(self) -> bool:
        """Check if user is doctor."""
        return self.role == UserRole.DOCTOR

    def has_permission(self, permission: Permission) -> bool:
        """Check if user has specific permission."""
        return permission in self.permissions

    def has_any_permission(self, permissions: List[Permission]) -> bool:
        """Check if user has any of the specified permissions."""
        return any(p in self.permissions for p in permissions)

    def has_all_permissions(self, permissions: List[Permission]) -> bool:
        """Check if user has all specified permissions."""
        return all(p in self.permissions for p in permissions)

    def can_access_clinic_data(self, clinic_id: str) -> bool:
        """Check if user can access data for specific clinic."""
        return self.clinic_id == clinic_id

    def can_access_doctor_data(self, doctor_id: str) -> bool:
        """Check if user can access data for specific doctor."""
        if self.is_admin():
            return True  # Admin can access any doctor in their clinic
        return self.doctor_id == doctor_id  # Doctor can only access own data

    def can_access_patient_data(self, doctor_id: str, patient_id: str) -> bool:
        """Check if user can access patient data for specific doctor-patient relationship."""
        if self.is_admin():
            return True  # Admin can access all patient data in clinic
        if self.is_doctor() and self.doctor_id == doctor_id:
            return True  # Doctor can access own patient data
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JWT encoding."""
        return {
            "user_id": self.user_id,
            "clinic_id": self.clinic_id,
            "whatsapp_number": self.whatsapp_number,
            "doctor_id": self.doctor_id,
            "role": self.role.value,
            "permissions": [p.value for p in self.permissions],
            "patient_access_scope": self.patient_access_scope.value,
            "exp": self.exp,
            "iat": self.iat,
            "iss": self.iss,
        }


# =============================================================================
# PERMISSION UTILITIES
# =============================================================================


def get_permissions_for_role(role: UserRole) -> Set[Permission]:
    """
    Get all permissions for a specific role.

    Args:
        role: User role

    Returns:
        Set of permissions for the role
    """
    if role == UserRole.ADMIN:
        return ADMIN_PERMISSIONS.copy()
    elif role == UserRole.DOCTOR:
        return DOCTOR_PERMISSIONS.copy()
    else:
        return set()


def get_data_access_scope(role: UserRole) -> DataAccessScope:
    """
    Get data access scope for a role.

    Args:
        role: User role

    Returns:
        Data access scope
    """
    if role == UserRole.ADMIN:
        return DataAccessScope.CLINIC_ALL
    elif role == UserRole.DOCTOR:
        return DataAccessScope.DOCTOR_OWN
    else:
        return DataAccessScope.PATIENT_SELF


def create_jwt_payload(
    user_id: str,
    clinic_id: str,
    whatsapp_number: str,
    role: UserRole,
    doctor_id: Optional[str] = None,
    exp_timestamp: Optional[int] = None,
    iat_timestamp: Optional[int] = None,
) -> JWTPayload:
    """
    Create JWT payload for user.

    Args:
        user_id: User identifier
        clinic_id: Clinic identifier
        whatsapp_number: User's WhatsApp number
        role: User role
        doctor_id: Doctor identifier (if user is doctor)
        exp_timestamp: Expiration timestamp
        iat_timestamp: Issued at timestamp

    Returns:
        JWT payload object
    """
    now = int(datetime.now(timezone.utc).timestamp())

    payload_data = {
        "user_id": user_id,
        "clinic_id": clinic_id,
        "whatsapp_number": whatsapp_number,
        "doctor_id": doctor_id,
        "role": role.value,
        "permissions": [p.value for p in get_permissions_for_role(role)],
        "patient_access_scope": get_data_access_scope(role).value,
        "exp": exp_timestamp or (now + 3600),  # 1 hour default
        "iat": iat_timestamp or now,
        "iss": "pulseops-api",
    }

    return JWTPayload(payload_data)


def validate_permission_access(
    user_permissions: Set[Permission],
    required_permission: Permission,
    user_role: UserRole,
) -> None:
    """
    Validate if user has required permission.

    Args:
        user_permissions: User's permissions
        required_permission: Required permission
        user_role: User's role

    Raises:
        InsufficientPermissionsError: If user lacks permission
    """
    if required_permission not in user_permissions:
        raise InsufficientPermissionsError(
            required_permission=required_permission.value,
            user_role=user_role.value,
            details={
                "user_permissions": [p.value for p in user_permissions],
                "required_permission": required_permission.value,
            },
        )


def validate_data_isolation(
    jwt_payload: JWTPayload,
    resource_clinic_id: str,
    resource_doctor_id: Optional[str] = None,
    resource_patient_id: Optional[str] = None,
) -> None:
    """
    Validate data isolation boundaries.

    Args:
        jwt_payload: JWT token payload
        resource_clinic_id: Clinic ID of the resource
        resource_doctor_id: Doctor ID of the resource (if applicable)
        resource_patient_id: Patient ID of the resource (if applicable)

    Raises:
        AuthorizationError: If data isolation is violated
    """
    # Check clinic boundary
    if not jwt_payload.can_access_clinic_data(resource_clinic_id):
        raise AuthorizationError(
            error_code="CLINIC_ACCESS_DENIED",
            message="Access denied: Resource belongs to different clinic",
            details={
                "user_clinic_id": jwt_payload.clinic_id,
                "resource_clinic_id": resource_clinic_id,
            },
        )

    # Check doctor boundary (for doctor users)
    if jwt_payload.is_doctor() and resource_doctor_id:
        if not jwt_payload.can_access_doctor_data(resource_doctor_id):
            raise AuthorizationError(
                error_code="DOCTOR_ACCESS_DENIED",
                message="Access denied: Resource belongs to different doctor",
                details={
                    "user_doctor_id": jwt_payload.doctor_id,
                    "resource_doctor_id": resource_doctor_id,
                },
            )

    # Check patient data access
    if resource_patient_id and resource_doctor_id:
        if not jwt_payload.can_access_patient_data(
            resource_doctor_id, resource_patient_id
        ):
            raise AuthorizationError(
                error_code="PATIENT_ACCESS_DENIED",
                message="Access denied: Patient data not accessible",
                details={
                    "user_role": jwt_payload.role.value,
                    "user_doctor_id": jwt_payload.doctor_id,
                    "resource_doctor_id": resource_doctor_id,
                    "resource_patient_id": resource_patient_id,
                },
            )


# =============================================================================
# AUTHENTICATION & AUTHORIZATION DEPENDENCIES
# =============================================================================

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> JWTPayload:
    """
    Get current authenticated user from JWT token.

    Args:
        credentials: HTTP authorization credentials

    Returns:
        JWT payload with user information

    Raises:
        AuthenticationError: If token is invalid or expired
    """
    try:
        # This would normally import from config, but avoiding circular imports
        from src.core.config import get_auth_config

        auth_config = get_auth_config()
        secret_key = auth_config.jwt_secret_key.get_secret_value()
        algorithm = auth_config.jwt_algorithm

        payload = jwt.decode(
            credentials.credentials,
            secret_key,
            algorithms=[algorithm],
        )

        jwt_payload = JWTPayload(payload)

        if jwt_payload.is_expired():
            raise TokenExpiredError()

        return jwt_payload

    except jwt.ExpiredSignatureError:
        raise TokenExpiredError()
    except jwt.InvalidTokenError:
        raise InvalidTokenError()
    except Exception as e:
        raise InvalidTokenError(details={"error": str(e)})


def require_permission(required_permission: Permission):
    """
    Decorator to require specific permission for endpoint access.

    Args:
        required_permission: Permission required to access endpoint

    Returns:
        Decorator function
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from dependency injection
            current_user = kwargs.get("current_user")
            if not current_user:
                raise AuthenticationError(
                    error_code="MISSING_USER_CONTEXT",
                    message="User context not found",
                )

            # Validate permission
            validate_permission_access(
                user_permissions=current_user.permissions,
                required_permission=required_permission,
                user_role=current_user.role,
            )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def require_any_permission(required_permissions: List[Permission]):
    """
    Decorator to require any of the specified permissions.

    Args:
        required_permissions: List of permissions (user needs at least one)

    Returns:
        Decorator function
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            if not current_user:
                raise AuthenticationError(
                    error_code="MISSING_USER_CONTEXT",
                    message="User context not found",
                )

            if not current_user.has_any_permission(required_permissions):
                raise InsufficientPermissionsError(
                    required_permission=f"Any of: {[p.value for p in required_permissions]}",
                    user_role=current_user.role.value,
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def require_role(required_role: UserRole):
    """
    Decorator to require specific role for endpoint access.

    Args:
        required_role: Role required to access endpoint

    Returns:
        Decorator function
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            if not current_user:
                raise AuthenticationError(
                    error_code="MISSING_USER_CONTEXT",
                    message="User context not found",
                )

            if current_user.role != required_role:
                raise InsufficientPermissionsError(
                    required_permission=f"Role: {required_role.value}",
                    user_role=current_user.role.value,
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def admin_only(func):
    """Decorator to restrict access to admin users only."""
    return require_role(UserRole.ADMIN)(func)


def doctor_only(func):
    """Decorator to restrict access to doctor users only."""
    return require_role(UserRole.DOCTOR)(func)


# =============================================================================
# FASTAPI DEPENDENCY FUNCTIONS
# =============================================================================


async def get_admin_user(
    current_user: JWTPayload = Depends(get_current_user),
) -> JWTPayload:
    """Dependency to get current admin user."""
    if not current_user.is_admin():
        raise InsufficientPermissionsError(
            required_permission="Admin role",
            user_role=current_user.role.value,
        )
    return current_user


async def get_doctor_user(
    current_user: JWTPayload = Depends(get_current_user),
) -> JWTPayload:
    """Dependency to get current doctor user."""
    if not current_user.is_doctor():
        raise InsufficientPermissionsError(
            required_permission="Doctor role",
            user_role=current_user.role.value,
        )
    return current_user


async def get_user_with_permission(permission: Permission):
    """
    Create dependency to get user with specific permission.

    Args:
        permission: Required permission

    Returns:
        Dependency function
    """

    async def dependency(
        current_user: JWTPayload = Depends(get_current_user),
    ) -> JWTPayload:
        validate_permission_access(
            user_permissions=current_user.permissions,
            required_permission=permission,
            user_role=current_user.role,
        )
        return current_user

    return dependency


# =============================================================================
# PERMISSION VALIDATION HELPERS
# =============================================================================


def can_manage_doctor(user: JWTPayload, target_doctor_id: str) -> bool:
    """Check if user can manage specific doctor."""
    if user.is_admin():
        return True
    return user.is_doctor() and user.doctor_id == target_doctor_id


def can_access_queue(user: JWTPayload, queue_doctor_id: str) -> bool:
    """Check if user can access specific queue."""
    if user.is_admin():
        return True
    return user.is_doctor() and user.doctor_id == queue_doctor_id


def can_access_patient_association(
    user: JWTPayload, association_doctor_id: str
) -> bool:
    """Check if user can access patient association."""
    if user.is_admin():
        return True
    return user.is_doctor() and user.doctor_id == association_doctor_id


def can_access_visit_record(user: JWTPayload, visit_doctor_id: str) -> bool:
    """Check if user can access visit record."""
    if user.is_admin():
        return True
    return user.is_doctor() and user.doctor_id == visit_doctor_id


def can_manage_subscription(user: JWTPayload) -> bool:
    """Check if user can manage subscription."""
    return user.is_admin()


def can_view_analytics(
    user: JWTPayload, target_doctor_id: Optional[str] = None
) -> bool:
    """Check if user can view analytics."""
    if user.is_admin():
        return True
    if user.is_doctor() and target_doctor_id:
        return user.doctor_id == target_doctor_id
    return False


# =============================================================================
# HEALTHCARE PRIVACY COMPLIANCE
# =============================================================================


def ensure_patient_data_isolation(
    user: JWTPayload,
    clinic_id: str,
    doctor_id: str,
    patient_id: Optional[str] = None,
) -> None:
    """
    Ensure patient data isolation compliance.

    Args:
        user: Current user
        clinic_id: Clinic ID of the data
        doctor_id: Doctor ID of the data
        patient_id: Patient ID (if applicable)

    Raises:
        AuthorizationError: If access violates privacy rules
    """
    validate_data_isolation(
        jwt_payload=user,
        resource_clinic_id=clinic_id,
        resource_doctor_id=doctor_id,
        resource_patient_id=patient_id,
    )


def get_accessible_doctor_ids(user: JWTPayload) -> List[str]:
    """
    Get list of doctor IDs that user can access.

    Args:
        user: Current user

    Returns:
        List of accessible doctor IDs
    """
    if user.is_admin():
        # Admin can access all doctors in their clinic
        # This would typically query the database
        return ["*"]  # Placeholder for "all doctors in clinic"
    elif user.is_doctor():
        # Doctor can only access their own data
        return [user.doctor_id] if user.doctor_id else []
    else:
        return []


def filter_data_by_access_scope(
    user: JWTPayload, data: List[Dict[str, Any]], doctor_id_field: str = "doctorId"
) -> List[Dict[str, Any]]:
    """
    Filter data based on user's access scope.

    Args:
        user: Current user
        data: Data to filter
        doctor_id_field: Field name containing doctor ID

    Returns:
        Filtered data based on access scope
    """
    if user.is_admin():
        return data  # Admin can see all data in clinic

    if user.is_doctor() and user.doctor_id:
        return [item for item in data if item.get(doctor_id_field) == user.doctor_id]

    return []  # No access by default


# =============================================================================
# AUDIT LOGGING FOR PERMISSIONS
# =============================================================================


def log_permission_check(
    user: JWTPayload,
    permission: Permission,
    resource_type: str,
    resource_id: str,
    granted: bool,
) -> None:
    """
    Log permission check for audit trail.

    Args:
        user: User attempting access
        permission: Permission being checked
        resource_type: Type of resource
        resource_id: Resource identifier
        granted: Whether access was granted
    """
    # Get the audit logger
    audit_logger = logging.getLogger("pulseops.audit")

    log_data = {
        "event": "permission_check",
        "user_id": user.user_id,
        "clinic_id": user.clinic_id,
        "doctor_id": user.doctor_id,
        "role": user.role.value,
        "permission": permission.value,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "granted": granted,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Log with appropriate level based on result
    if granted:
        audit_logger.info(
            f"Permission granted: {permission.value} for {resource_type}",
            extra=log_data,
        )
    else:
        audit_logger.warning(
            f"Permission denied: {permission.value} for {resource_type}", extra=log_data
        )


def log_data_access(
    user: JWTPayload,
    action: str,
    resource_type: str,
    resource_id: str,
    success: bool = True,
    details: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Log data access events for healthcare compliance.

    Args:
        user: User accessing data
        action: Action performed
        resource_type: Type of resource
        resource_id: Resource identifier
        success: Whether access was successful
        details: Additional event details
    """
    # Get the audit logger
    audit_logger = logging.getLogger("pulseops.audit")

    log_data = {
        "event": "data_access",
        "user_id": user.user_id,
        "clinic_id": user.clinic_id,
        "doctor_id": user.doctor_id,
        "role": user.role.value,
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "success": success,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "details": details or {},
    }

    # Log with appropriate level based on result
    if success:
        audit_logger.info(f"Data access: {action} {resource_type}", extra=log_data)
    else:
        audit_logger.error(
            f"Failed data access: {action} {resource_type}", extra=log_data
        )


# =============================================================================
# PERMISSION CONSTANTS FOR QUICK ACCESS
# =============================================================================

# Common permission groups for easy reference
PATIENT_MANAGEMENT_PERMISSIONS = {
    Permission.VIEW_OWN_PATIENTS,
    Permission.MANAGE_OWN_PATIENT_ASSOCIATIONS,
    Permission.ADD_PATIENT_ASSOCIATION,
    Permission.UPDATE_PATIENT_ASSOCIATION,
}

MEDICAL_DOCUMENTATION_PERMISSIONS = {
    Permission.ADD_VISIT_NOTES,
    Permission.EDIT_VISIT_NOTES,
    Permission.ADD_DIAGNOSIS,
    Permission.EDIT_DIAGNOSIS,
    Permission.ADD_PRESCRIPTION,
    Permission.EDIT_PRESCRIPTION,
}

QUEUE_MANAGEMENT_PERMISSIONS = {
    Permission.VIEW_OWN_QUEUE,
    Permission.MANAGE_OWN_QUEUE,
    Permission.START_OWN_QUEUE,
    Permission.PAUSE_OWN_QUEUE,
    Permission.CALL_NEXT_PATIENT,
}

ADMIN_ONLY_PERMISSIONS = {
    Permission.MANAGE_DOCTORS,
    Permission.MANAGE_SUBSCRIPTION,
    Permission.VIEW_REVENUE,
    Permission.CONFIGURE_WHATSAPP,
    Permission.MANAGE_SETTINGS,
}
