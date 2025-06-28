"""
Security utilities for the PulseOps healthcare management system.

This module provides comprehensive security features including:
- JWT token generation and validation
- Password hashing and verification
- OTP generation and validation
- Data encryption and decryption
- Audit logging for security events
- Healthcare privacy compliance utilities
- Rate limiting and security checks
"""

# flake8: noqa: E501

import hashlib
import hmac
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Union
from functools import wraps
import re
import logging
from contextlib import contextmanager

import bcrypt
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from fastapi import status

from .config import get_auth_config, get_security_config, get_logging_config
from .exceptions import (
    InvalidTokenError,
    TokenExpiredError,
    InvalidCredentialsError,
    OTPExpiredError,
    OTPInvalidError,
    OTPMaxAttemptsError,
    SecurityError,
    RateLimitExceededError,
)
from .permissions import UserRole, Permission, JWTPayload


# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Get configuration
auth_config = get_auth_config()
security_config = get_security_config()
logging_config = get_logging_config()

# Security logger
security_logger = logging.getLogger("pulseops.security")


# =============================================================================
# PASSWORD SECURITY
# =============================================================================


class PasswordSecurity:
    """Password security utilities for PulseOps."""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            str: Hashed password

        Raises:
            ValueError: If password doesn't meet requirements
        """
        # Validate password strength
        PasswordSecurity.validate_password_strength(password)

        # Hash password
        hashed = pwd_context.hash(password)

        # Log password creation (without actual password)
        security_logger.info(
            "Password hashed successfully",
            extra={
                "event_type": "password_hash",
                "password_length": len(password),
                "hash_algorithm": "bcrypt",
            },
        )

        return hashed

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against hash.

        Args:
            plain_password: Plain text password
            hashed_password: Hashed password

        Returns:
            bool: True if password matches
        """
        try:
            is_valid = pwd_context.verify(plain_password, hashed_password)

            # Log verification attempt
            security_logger.info(
                "Password verification attempt",
                extra={
                    "event_type": "password_verify",
                    "success": is_valid,
                },
            )

            return is_valid
        except Exception as e:
            security_logger.error(
                "Password verification failed",
                extra={
                    "event_type": "password_verify_error",
                    "error": str(e),
                },
            )
            return False

    @staticmethod
    def validate_password_strength(password: str) -> None:
        """
        Validate password meets security requirements.

        Args:
            password: Password to validate

        Raises:
            ValueError: If password doesn't meet requirements
        """
        if len(password) < auth_config.password_min_length:
            raise ValueError(
                f"Password must be at least {auth_config.password_min_length} characters long"
            )

        if auth_config.password_require_uppercase and not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter")

        if auth_config.password_require_numbers and not re.search(r"\d", password):
            raise ValueError("Password must contain at least one number")

        if auth_config.password_require_special_chars and not re.search(
            r"[!@#$%^&*(),.?\":{}|<>]", password
        ):
            raise ValueError("Password must contain at least one special character")

        # Check for common weak passwords
        weak_passwords = [
            "password",
            "123456",
            "password123",
            "admin",
            "qwerty",
            "letmein",
            "welcome",
            "monkey",
            "dragon",
            "master",
        ]
        if password.lower() in weak_passwords:
            raise ValueError("Password is too common and weak")

    @staticmethod
    def generate_secure_password(length: int = 12) -> str:
        """
        Generate a secure random password.

        Args:
            length: Password length (minimum 8)

        Returns:
            str: Secure random password
        """
        if length < 8:
            length = 8

        # Character sets
        uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        lowercase = "abcdefghijklmnopqrstuvwxyz"
        numbers = "0123456789"
        special = '!@#$%^&*(),.?":{}|<>'

        # Ensure at least one character from each set
        password = [
            secrets.choice(uppercase),
            secrets.choice(lowercase),
            secrets.choice(numbers),
            secrets.choice(special),
        ]

        # Fill remaining length
        all_chars = uppercase + lowercase + numbers + special
        for _ in range(length - 4):
            password.append(secrets.choice(all_chars))

        # Shuffle the password
        secrets.SystemRandom().shuffle(password)

        return "".join(password)


# =============================================================================
# JWT TOKEN SECURITY
# =============================================================================


class JWTSecurity:
    """JWT token security utilities for PulseOps."""

    @staticmethod
    def create_access_token(
        user_id: str,
        clinic_id: str,
        whatsapp_number: str,
        role: UserRole,
        doctor_id: Optional[str] = None,
        permissions: Optional[List[str]] = None,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """
        Create JWT access token.

        Args:
            user_id: User identifier
            clinic_id: Clinic identifier
            whatsapp_number: User's WhatsApp number
            role: User role
            doctor_id: Doctor ID (if user is doctor)
            permissions: List of permissions
            expires_delta: Token expiration time

        Returns:
            str: JWT access token
        """
        if expires_delta is None:
            expires_delta = timedelta(
                minutes=auth_config.jwt_access_token_expire_minutes
            )

        now = datetime.now(timezone.utc)
        expire = now + expires_delta

        # Create token payload
        payload = {
            "sub": user_id,
            "user_id": user_id,
            "clinic_id": clinic_id,
            "whatsapp_number": whatsapp_number,
            "role": role.value,
            "doctor_id": doctor_id,
            "permissions": permissions or [],
            "token_type": "access",
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
            "jti": str(uuid.uuid4()),  # JWT ID for tracking
            "iss": "pulseops-api",
        }

        # Create token
        token = jwt.encode(
            payload,
            auth_config.jwt_secret_key.get_secret_value(),
            algorithm=auth_config.jwt_algorithm,
        )

        # Log token creation
        security_logger.info(
            "Access token created",
            extra={
                "event_type": "token_create",
                "user_id": user_id,
                "clinic_id": clinic_id,
                "role": role.value,
                "expires_at": expire.isoformat(),
                "jti": payload["jti"],
            },
        )

        return token

    @staticmethod
    def create_refresh_token(
        user_id: str,
        clinic_id: str,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """
        Create JWT refresh token.

        Args:
            user_id: User identifier
            clinic_id: Clinic identifier
            expires_delta: Token expiration time

        Returns:
            str: JWT refresh token
        """
        if expires_delta is None:
            expires_delta = timedelta(days=auth_config.jwt_refresh_token_expire_days)

        now = datetime.now(timezone.utc)
        expire = now + expires_delta

        # Create token payload
        payload = {
            "sub": user_id,
            "user_id": user_id,
            "clinic_id": clinic_id,
            "token_type": "refresh",
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
            "jti": str(uuid.uuid4()),
            "iss": "pulseops-api",
        }

        # Create token
        token = jwt.encode(
            payload,
            auth_config.jwt_secret_key.get_secret_value(),
            algorithm=auth_config.jwt_algorithm,
        )

        # Log token creation
        security_logger.info(
            "Refresh token created",
            extra={
                "event_type": "refresh_token_create",
                "user_id": user_id,
                "clinic_id": clinic_id,
                "expires_at": expire.isoformat(),
                "jti": payload["jti"],
            },
        )

        return token

    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """
        Decode and validate JWT token.

        Args:
            token: JWT token string

        Returns:
            Dict[str, Any]: Token payload

        Raises:
            InvalidTokenError: If token is invalid
            TokenExpiredError: If token has expired
        """
        try:
            # Check if token is revoked first (using class instance)
            jwt_instance = JWTSecurity()
            if jwt_instance.is_token_revoked(token):
                raise InvalidTokenError("Token has been revoked")

            payload = jwt.decode(
                token,
                auth_config.jwt_secret_key.get_secret_value(),
                algorithms=[auth_config.jwt_algorithm],
                options={"verify_exp": True, "verify_iat": True},
            )

            # Validate token structure
            required_fields = [
                "user_id",
                "clinic_id",
                "role",
                "token_type",
                "exp",
                "iat",
            ]
            for field in required_fields:
                if field not in payload:
                    raise InvalidTokenError(details={"missing_field": field})

            # Log successful token decode
            security_logger.info(
                "Token decoded successfully",
                extra={
                    "event_type": "token_decode",
                    "user_id": payload.get("user_id"),
                    "clinic_id": payload.get("clinic_id"),
                    "token_type": payload.get("token_type"),
                    "jti": payload.get("jti"),
                },
            )

            return payload

        except jwt.ExpiredSignatureError:
            security_logger.warning(
                "Token expired",
                extra={
                    "event_type": "token_expired",
                    "token": token[:20] + "...",  # Log partial token for debugging
                },
            )
            raise TokenExpiredError()

        except JWTError as e:
            security_logger.error(
                "Invalid token",
                extra={
                    "event_type": "token_invalid",
                    "error": str(e),
                    "token": token[:20] + "...",
                },
            )
            raise InvalidTokenError(details={"jwt_error": str(e)})

    @staticmethod
    def refresh_access_token(refresh_token: str) -> str:
        """
        Create new access token from refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            str: New access token

        Raises:
            InvalidTokenError: If refresh token is invalid
            TokenExpiredError: If refresh token has expired
        """
        # Decode refresh token
        payload = JWTSecurity.decode_token(refresh_token)

        # Validate token type
        if payload.get("token_type") != "refresh":
            raise InvalidTokenError(
                details={
                    "expected_type": "refresh",
                    "actual_type": payload.get("token_type"),
                }
            )

        # Create new access token (would need user data from database)
        # This is a simplified version - in practice, you'd fetch user data
        return JWTSecurity.create_access_token(
            user_id=payload["user_id"],
            clinic_id=payload["clinic_id"],
            whatsapp_number="",  # Would fetch from database
            role=UserRole(payload["role"]),
        )

    @staticmethod
    def invalidate_token(token: str) -> None:
        """
        Invalidate a JWT token (add to blacklist).

        Args:
            token: Token to invalidate
        """
        try:
            # Get unverified claims to avoid circular dependency
            unverified_payload = jwt.get_unverified_claims(token)
            jti = unverified_payload.get("jti")

            # Log token invalidation
            security_logger.info(
                "Token invalidated",
                extra={
                    "event_type": "token_invalidate",
                    "user_id": unverified_payload.get("user_id"),
                    "jti": jti,
                },
            )

            # Revoke the token by adding to blacklist
            jwt_instance = JWTSecurity()
            jwt_instance.revoke_token(token)

        except Exception as e:
            security_logger.error(
                "Token invalidation failed",
                extra={
                    "event_type": "token_invalidate_error",
                    "error": str(e),
                },
            )

    def revoke_token(self, token: str) -> None:
        """
        Revoke JWT token by adding to blacklist.

        Args:
            token: JWT token to revoke
        """
        try:
            # Decode token to get JTI (if available) and expiration
            unverified_payload = jwt.get_unverified_claims(token)
            jti = unverified_payload.get("jti", self._generate_jti())
            exp = unverified_payload.get("exp")

            if exp:
                exp_datetime = datetime.fromtimestamp(exp, tz=timezone.utc)
            else:
                # Default expiration if not in token
                exp_datetime = datetime.now(timezone.utc) + timedelta(
                    minutes=auth_config.jwt_access_token_expire_minutes
                )

            # Store in blacklist with expiration
            # In production, use Redis or database for token blacklist
            if not hasattr(self, "_token_blacklist"):
                self._token_blacklist = {}

            self._token_blacklist[jti] = {
                "revoked_at": datetime.now(timezone.utc).isoformat(),
                "expires_at": exp_datetime.isoformat(),
                "token_hash": hashlib.sha256(token.encode()).hexdigest()[:16],
            }

            security_logger.info(
                "Token revoked successfully",
                extra={
                    "event_type": "token_revocation",
                    "jti": jti,
                    "expires_at": exp_datetime.isoformat(),
                },
            )

        except Exception as e:
            security_logger.error(
                "Token revocation failed",
                extra={
                    "event_type": "token_revocation_error",
                    "error": str(e),
                },
            )
            raise SecurityError(f"Token revocation failed: {str(e)}")

    def is_token_revoked(self, token: str) -> bool:
        """
        Check if token is in blacklist.

        Args:
            token: JWT token to check

        Returns:
            bool: True if token is revoked
        """
        try:
            # Get JTI from token
            unverified_payload = jwt.get_unverified_claims(token)
            jti = unverified_payload.get("jti")

            if not jti:
                return False

            # Check blacklist (in production, check Redis/database)
            if not hasattr(self, "_token_blacklist"):
                return False

            blacklist_entry = self._token_blacklist.get(jti)
            if not blacklist_entry:
                return False

            # Check if blacklist entry has expired
            expires_at = datetime.fromisoformat(
                blacklist_entry["expires_at"].replace("Z", "+00:00")
            )
            if datetime.now(timezone.utc) > expires_at:
                # Clean up expired entry
                del self._token_blacklist[jti]
                return False

            return True

        except Exception as e:
            security_logger.warning(
                "Token blacklist check failed",
                extra={
                    "event_type": "blacklist_check_error",
                    "error": str(e),
                },
            )
            # Default to not revoked if check fails
            return False

    def cleanup_expired_tokens(self) -> None:
        """Clean up expired tokens from blacklist."""
        if not hasattr(self, "_token_blacklist"):
            return

        current_time = datetime.now(timezone.utc)
        expired_tokens = []

        for jti, entry in self._token_blacklist.items():
            expires_at = datetime.fromisoformat(
                entry["expires_at"].replace("Z", "+00:00")
            )
            if current_time > expires_at:
                expired_tokens.append(jti)

        for jti in expired_tokens:
            del self._token_blacklist[jti]

        if expired_tokens:
            security_logger.info(
                f"Cleaned up {len(expired_tokens)} expired tokens from blacklist"
            )


# =============================================================================
# OTP SECURITY
# =============================================================================


class OTPSecurity:
    """OTP generation and validation utilities for PulseOps."""

    @staticmethod
    def generate_otp(length: int = None) -> str:
        """
        Generate secure numeric OTP.

        Args:
            length: OTP length (default from config)

        Returns:
            str: Numeric OTP
        """
        if length is None:
            length = auth_config.otp_length

        # Generate cryptographically secure random OTP
        otp = "".join([str(secrets.randbelow(10)) for _ in range(length)])

        # Log OTP generation (without actual OTP)
        security_logger.info(
            "OTP generated",
            extra={
                "event_type": "otp_generate",
                "otp_length": length,
            },
        )

        return otp

    @staticmethod
    def create_otp_hash(otp: str, request_id: str) -> str:
        """
        Create secure hash of OTP for storage.

        Args:
            otp: Plain OTP
            request_id: OTP request identifier

        Returns:
            str: Hashed OTP
        """
        # Create hash using OTP + request_id + secret
        secret = auth_config.jwt_secret_key.get_secret_value()
        combined = f"{otp}:{request_id}:{secret}"

        return hashlib.sha256(combined.encode()).hexdigest()

    @staticmethod
    def verify_otp(otp: str, stored_hash: str, request_id: str) -> bool:
        """
        Verify OTP against stored hash.

        Args:
            otp: Provided OTP
            stored_hash: Stored OTP hash
            request_id: OTP request identifier

        Returns:
            bool: True if OTP is valid
        """
        expected_hash = OTPSecurity.create_otp_hash(otp, request_id)
        is_valid = hmac.compare_digest(expected_hash, stored_hash)

        # Log verification attempt
        security_logger.info(
            "OTP verification attempt",
            extra={
                "event_type": "otp_verify",
                "request_id": request_id,
                "success": is_valid,
            },
        )

        return is_valid

    @staticmethod
    def is_otp_expired(created_at: datetime) -> bool:
        """
        Check if OTP has expired.

        Args:
            created_at: OTP creation timestamp

        Returns:
            bool: True if expired
        """
        expiry_time = created_at + timedelta(minutes=auth_config.otp_expire_minutes)
        is_expired = datetime.now(timezone.utc) > expiry_time

        if is_expired:
            security_logger.info(
                "OTP expired",
                extra={
                    "event_type": "otp_expired",
                    "created_at": created_at.isoformat(),
                    "expired_at": expiry_time.isoformat(),
                },
            )

        return is_expired


# =============================================================================
# DATA ENCRYPTION
# =============================================================================


class DataEncryption:
    """Data encryption utilities for healthcare privacy compliance."""

    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize encryption with key.

        Args:
            encryption_key: Base64 encoded encryption key
        """
        if encryption_key:
            self.key = encryption_key.encode()
        else:
            # Generate key from JWT secret (in production, use dedicated encryption key)
            secret = auth_config.jwt_secret_key.get_secret_value().encode()
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b"pulseops_salt",  # In production, use random salt per clinic
                iterations=100000,
            )
            self.key = base64.urlsafe_b64encode(kdf.derive(secret))

        self.cipher = Fernet(self.key)

    def encrypt_sensitive_data(self, data: str) -> str:
        """
        Encrypt sensitive healthcare data.

        Args:
            data: Plain text data

        Returns:
            str: Encrypted data (base64 encoded)
        """
        if not security_config.data_encryption_enabled:
            return data

        try:
            encrypted_data = self.cipher.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            security_logger.error(
                "Data encryption failed",
                extra={
                    "event_type": "encryption_error",
                    "error": str(e),
                },
            )
            raise SecurityError(f"Data encryption failed: {str(e)}")

    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """
        Decrypt sensitive healthcare data.

        Args:
            encrypted_data: Encrypted data (base64 encoded)

        Returns:
            str: Decrypted plain text data
        """
        if not security_config.data_encryption_enabled:
            return encrypted_data

        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.cipher.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            security_logger.error(
                "Data decryption failed",
                extra={
                    "event_type": "decryption_error",
                    "error": str(e),
                },
            )
            raise SecurityError(f"Data decryption failed: {str(e)}")

    def mask_pii_data(self, data: str, mask_char: str = "*") -> str:
        """
        Mask personally identifiable information.

        Args:
            data: Data to mask
            mask_char: Character to use for masking

        Returns:
            str: Masked data
        """
        if not security_config.pii_masking_enabled:
            return data

        if not data or len(data) < 4:
            return mask_char * len(data)

        # Keep first and last character, mask middle
        return data[0] + mask_char * (len(data) - 2) + data[-1]

    def mask_phone_number(self, phone: str) -> str:
        """
        Mask phone number for logging.

        Args:
            phone: Phone number

        Returns:
            str: Masked phone number
        """
        if len(phone) <= 6:
            return "*" * len(phone)

        # Show country code and last 3 digits
        return phone[:3] + "*" * (len(phone) - 6) + phone[-3:]


# =============================================================================
# AUDIT LOGGING
# =============================================================================


class AuditLogger:
    """Security audit logging for healthcare compliance."""

    def __init__(self):
        self.logger = logging.getLogger("pulseops.audit")

    def log_authentication_event(
        self,
        event_type: str,
        user_id: Optional[str] = None,
        clinic_id: Optional[str] = None,
        whatsapp_number: Optional[str] = None,
        success: bool = True,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log authentication events.

        Args:
            event_type: Type of authentication event
            user_id: User identifier
            clinic_id: Clinic identifier
            whatsapp_number: User's WhatsApp number
            success: Whether the event was successful
            ip_address: Client IP address
            user_agent: Client user agent
            details: Additional event details
        """
        # Mask sensitive data
        encryption = DataEncryption()
        masked_whatsapp = (
            encryption.mask_phone_number(whatsapp_number) if whatsapp_number else None
        )

        audit_data = {
            "event_category": "authentication",
            "event_type": event_type,
            "user_id": user_id,
            "clinic_id": clinic_id,
            "whatsapp_number": masked_whatsapp,
            "success": success,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": details or {},
        }

        if success:
            self.logger.info(f"Authentication event: {event_type}", extra=audit_data)
        else:
            self.logger.warning(
                f"Failed authentication event: {event_type}", extra=audit_data
            )

    def log_data_access_event(
        self,
        event_type: str,
        user_id: str,
        clinic_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        success: bool = True,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log data access events for healthcare compliance.

        Args:
            event_type: Type of data access event
            user_id: User accessing data
            clinic_id: Clinic context
            resource_type: Type of resource accessed
            resource_id: Resource identifier
            action: Action performed
            success: Whether access was successful
            ip_address: Client IP address
            details: Additional event details
        """
        audit_data = {
            "event_category": "data_access",
            "event_type": event_type,
            "user_id": user_id,
            "clinic_id": clinic_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "action": action,
            "success": success,
            "ip_address": ip_address,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": details or {},
        }

        if success:
            self.logger.info(f"Data access: {action} {resource_type}", extra=audit_data)
        else:
            self.logger.warning(
                f"Failed data access: {action} {resource_type}", extra=audit_data
            )

    def log_permission_event(
        self,
        event_type: str,
        user_id: str,
        clinic_id: str,
        permission: str,
        resource_type: str,
        resource_id: str,
        granted: bool,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log permission check events.

        Args:
            event_type: Type of permission event
            user_id: User requesting permission
            clinic_id: Clinic context
            permission: Permission being checked
            resource_type: Type of resource
            resource_id: Resource identifier
            granted: Whether permission was granted
            ip_address: Client IP address
            details: Additional event details
        """
        audit_data = {
            "event_category": "permission",
            "event_type": event_type,
            "user_id": user_id,
            "clinic_id": clinic_id,
            "permission": permission,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "granted": granted,
            "ip_address": ip_address,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": details or {},
        }

        if granted:
            self.logger.info(f"Permission granted: {permission}", extra=audit_data)
        else:
            self.logger.warning(f"Permission denied: {permission}", extra=audit_data)


# =============================================================================
# RATE LIMITING
# =============================================================================


class RateLimiter:
    """Rate limiting for security and API protection."""

    def __init__(self):
        # In production, this would use Redis or database
        self._requests = {}
        self._otp_requests = {}

    def check_rate_limit(
        self,
        identifier: str,
        limit: int,
        window_seconds: int,
        request_type: str = "api",
    ) -> bool:
        """
        Check if request is within rate limit.

        Args:
            identifier: Unique identifier (IP, user ID, etc.)
            limit: Maximum requests allowed
            window_seconds: Time window in seconds
            request_type: Type of request for logging

        Returns:
            bool: True if within limit

        Raises:
            RateLimitExceededError: If rate limit exceeded
        """
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(seconds=window_seconds)

        # Get request history for identifier
        if identifier not in self._requests:
            self._requests[identifier] = []

        # Clean old requests
        self._requests[identifier] = [
            req_time
            for req_time in self._requests[identifier]
            if req_time > window_start
        ]

        # Check if within limit
        if len(self._requests[identifier]) >= limit:
            security_logger.warning(
                "Rate limit exceeded",
                extra={
                    "event_type": "rate_limit_exceeded",
                    "identifier": identifier,
                    "request_type": request_type,
                    "limit": limit,
                    "window_seconds": window_seconds,
                    "current_count": len(self._requests[identifier]),
                },
            )
            raise RateLimitExceededError(
                identifier=identifier,
                limit=limit,
                window_seconds=window_seconds,
            )

        # Add current request
        self._requests[identifier].append(now)
        return True

    def check_otp_rate_limit(self, whatsapp_number: str) -> bool:
        """
        Check OTP request rate limit.

        Args:
            whatsapp_number: WhatsApp number

        Returns:
            bool: True if within limit

        Raises:
            RateLimitExceededError: If rate limit exceeded
        """
        return self.check_rate_limit(
            identifier=f"otp:{whatsapp_number}",
            limit=auth_config.otp_rate_limit_per_hour,
            window_seconds=3600,  # 1 hour
            request_type="otp",
        )


# =============================================================================
# SECURITY DECORATORS
# =============================================================================


def audit_data_access(resource_type: str, action: str):
    """
    Decorator to audit data access events.

    Args:
        resource_type: Type of resource being accessed
        action: Action being performed
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user context (would be passed as parameter)
            user_context = kwargs.get("current_user")
            resource_id = kwargs.get("resource_id", "unknown")

            audit_logger = AuditLogger()

            try:
                # Execute function
                result = await func(*args, **kwargs)

                # Log successful access
                if user_context:
                    audit_logger.log_data_access_event(
                        event_type="data_access_success",
                        user_id=user_context.user_id,
                        clinic_id=user_context.clinic_id,
                        resource_type=resource_type,
                        resource_id=str(resource_id),
                        action=action,
                        success=True,
                    )

                return result

            except Exception as e:
                # Log failed access
                if user_context:
                    audit_logger.log_data_access_event(
                        event_type="data_access_failure",
                        user_id=user_context.user_id,
                        clinic_id=user_context.clinic_id,
                        resource_type=resource_type,
                        resource_id=str(resource_id),
                        action=action,
                        success=False,
                        details={"error": str(e)},
                    )

                raise

        return wrapper

    return decorator


def rate_limited(limit: int, window_seconds: int, identifier_func=None):
    """
    Decorator to apply rate limiting.

    Args:
        limit: Maximum requests allowed
        window_seconds: Time window in seconds
        identifier_func: Function to extract identifier from request
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            rate_limiter = RateLimiter()

            # Extract identifier
            if identifier_func:
                identifier = identifier_func(*args, **kwargs)
            else:
                # Default to user ID if available
                user_context = kwargs.get("current_user")
                identifier = user_context.user_id if user_context else "anonymous"

            # Check rate limit
            rate_limiter.check_rate_limit(
                identifier=identifier,
                limit=limit,
                window_seconds=window_seconds,
            )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def generate_correlation_id() -> str:
    """
    Generate unique correlation ID for request tracking.

    Returns:
        str: Correlation ID
    """
    return str(uuid.uuid4())


def sanitize_input(input_str: str, max_length: int = 1000) -> str:
    """
    Sanitize user input for healthcare data security.

    Args:
        input_str: Input string to sanitize
        max_length: Maximum allowed length

    Returns:
        str: Sanitized input
    """
    if not input_str:
        return ""

    # Truncate to max length
    sanitized = input_str[:max_length]

    # Remove potentially dangerous characters for XSS prevention
    sanitized = re.sub(r"[<>]", "", sanitized)

    # Remove control characters but keep normal punctuation
    sanitized = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", sanitized)

    # Remove excessive whitespace
    sanitized = re.sub(r"\s+", " ", sanitized)

    return sanitized.strip()


def validate_whatsapp_number(phone: str) -> bool:
    """
    Validate WhatsApp phone number format.

    Args:
        phone: Phone number to validate

    Returns:
        bool: True if valid format
    """
    # Indian phone number pattern: +91 followed by 10 digits
    pattern = r"^\+91[6-9]\d{9}$"
    return bool(re.match(pattern, phone))


def validate_dynamodb_key(key_value: str, max_length: int = 255) -> bool:
    """
    Validate DynamoDB key values for security and compliance.

    Args:
        key_value: DynamoDB key value to validate
        max_length: Maximum allowed length

    Returns:
        bool: True if valid

    Raises:
        ValueError: If key value is invalid
    """
    if not key_value:
        raise ValueError("Key value cannot be empty")

    if len(key_value) > max_length:
        raise ValueError(f"Key value too long (max {max_length} characters)")

    # DynamoDB keys should not contain certain characters
    invalid_chars = ["\x00", "\x01", "\x02", "\x03", "\x04", "\x05", "\x06", "\x07"]
    if any(char in key_value for char in invalid_chars):
        raise ValueError("Key value contains invalid control characters")

    return True


def sanitize_healthcare_data(data: str, field_type: str = "general") -> str:
    """
    Sanitize healthcare data based on field type.

    Args:
        data: Data to sanitize
        field_type: Type of healthcare field (name, diagnosis, prescription, etc.)

    Returns:
        str: Sanitized data
    """
    if not data:
        return ""

    # Basic sanitization
    sanitized = sanitize_input(data)

    # Field-specific sanitization
    if field_type == "name":
        # Allow only letters, spaces, hyphens, apostrophes
        sanitized = re.sub(r"[^a-zA-Z\s\-\']", "", sanitized)
        # Limit to reasonable name length
        sanitized = sanitized[:100]

    elif field_type == "diagnosis":
        # Allow medical terminology but remove HTML/script tags
        sanitized = re.sub(r"<[^>]*>", "", sanitized)
        sanitized = sanitized[:500]

    elif field_type == "prescription":
        # Allow alphanumeric, spaces, common medical symbols
        sanitized = re.sub(r"[^a-zA-Z0-9\s\-\.,\(\)\/mg]", "", sanitized)
        sanitized = sanitized[:1000]

    elif field_type == "notes":
        # Private medical notes - allow more characters but still secure
        sanitized = re.sub(
            r"<script[^>]*>.*?</script>", "", sanitized, flags=re.IGNORECASE
        )
        sanitized = sanitized[:2000]

    return sanitized.strip()


@contextmanager
def security_context(
    user_id: str,
    clinic_id: str,
    action: str,
    resource_type: str,
    resource_id: str,
):
    """
    Context manager for security operations with automatic audit logging.

    Args:
        user_id: User performing action
        clinic_id: Clinic context
        action: Action being performed
        resource_type: Type of resource
        resource_id: Resource identifier
    """
    audit_logger = AuditLogger()
    correlation_id = generate_correlation_id()

    # Log operation start
    audit_logger.log_data_access_event(
        event_type="operation_start",
        user_id=user_id,
        clinic_id=clinic_id,
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
        success=True,
        details={"correlation_id": correlation_id},
    )

    try:
        yield correlation_id

        # Log successful completion
        audit_logger.log_data_access_event(
            event_type="operation_success",
            user_id=user_id,
            clinic_id=clinic_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            success=True,
            details={"correlation_id": correlation_id},
        )

    except Exception as e:
        # Log operation failure
        audit_logger.log_data_access_event(
            event_type="operation_failure",
            user_id=user_id,
            clinic_id=clinic_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            success=False,
            details={
                "correlation_id": correlation_id,
                "error": str(e),
                "error_type": type(e).__name__,
            },
        )
        raise


# =============================================================================
# GLOBAL INSTANCES
# =============================================================================

# Global instances for easy access
password_security = PasswordSecurity()
jwt_security = JWTSecurity()
otp_security = OTPSecurity()
data_encryption = DataEncryption()
audit_logger = AuditLogger()
rate_limiter = RateLimiter()
