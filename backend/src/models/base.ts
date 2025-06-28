/**
 * Base entity interface providing common timestamp fields for all PulseOps entities.
 * Ensures consistent audit trail with creation and modification tracking.
 * Used as foundation for all healthcare data models.
 */
export interface BaseEntity {
  createdAt: string;
  updatedAt: string;
}

/**
 * Enhanced entity interface with user tracking for healthcare compliance.
 * Extends BaseEntity with audit fields for HIPAA compliance and data accountability.
 * Tracks who created/modified records and supports optimistic locking with versioning.
 */
export interface AuditableEntity extends BaseEntity {
  createdBy?: string;
  updatedBy?: string;
  version?: number;
}

/**
 * DynamoDB-specific entity structure with partition and sort key definitions.
 * Provides database abstraction layer for AWS DynamoDB operations.
 * Includes entity type for consistent data organization and querying.
 */
export interface DynamoDBEntity {
  partitionKey: string;
  sortKey?: string;
  entityType: string;
}

/**
 * Generic entity metadata for tracking and system management.
 * Provides consistent identification, typing, and status tracking
 * across all PulseOps healthcare entities.
 */
export interface EntityMetadata {
  id: string;
  type: EntityType;
  status: EntityStatus;
  isActive: boolean;
}

/**
 * Common entity status enumeration for lifecycle management.
 * Provides standardized status tracking across all healthcare entities.
 * Supports soft deletion and suspension for data retention compliance.
 */
export enum EntityStatus {
  ACTIVE = 'ACTIVE',
  INACTIVE = 'INACTIVE',
  PENDING = 'PENDING',
  SUSPENDED = 'SUSPENDED',
  DELETED = 'DELETED',
}

/**
 * Comprehensive entity type enumeration for the PulseOps healthcare system.
 * Defines all core healthcare entities with multi-tenant clinic organization.
 * Used for database partitioning, access control, and business logic routing.
 */
export enum EntityType {
  CLINIC = 'CLINIC',
  DOCTOR = 'DOCTOR',
  PATIENT = 'PATIENT',
  USER = 'USER',
  QUEUE = 'QUEUE',
  TOKEN = 'TOKEN',
  VISIT = 'VISIT',
  ASSOCIATION = 'ASSOCIATION',
  SUBSCRIPTION = 'SUBSCRIPTION',
  PAYMENT = 'PAYMENT',
  NOTIFICATION = 'NOTIFICATION',
}

/**
 * User role enumeration for healthcare system access control.
 * Defines role-based permissions within clinic boundaries.
 * Admin: Full clinic access, Doctor: Patient-specific access only.
 */
export enum UserRole {
  ADMIN = 'ADMIN',
  DOCTOR = 'DOCTOR',
}

/**
 * Subscription tier enumeration for clinic billing and feature access.
 * Provides tiered pricing with different doctor limits and feature sets.
 * Optimized for Indian healthcare market with per-doctor pricing model.
 */
export enum SubscriptionTier {
  BASIC = 'BASIC',
  PROFESSIONAL = 'PROFESSIONAL',
  ENTERPRISE = 'ENTERPRISE',
}

/**
 * Standard contact information structure for healthcare entities.
 * Optimized for Indian market with WhatsApp as primary communication channel.
 * Supports multiple phone numbers for enhanced patient reachability.
 */
export interface ContactInfo {
  phone: string;
  whatsappNumber: string;
  email?: string;
  alternatePhone?: string;
}

/**
 * Enhanced Indian phone number structure with verification and WhatsApp support.
 * Ensures compliance with Indian mobile number format (+91XXXXXXXXXX).
 * Tracks WhatsApp availability for patient communication automation.
 */
export interface IndianPhoneNumber {
  number: string; // +919876543210 format
  isWhatsAppEnabled: boolean;
  isVerified: boolean;
  verifiedAt?: string;
}

/**
 * Comprehensive address structure optimized for Indian geographical context.
 * Includes pincode validation and landmark support for precise location.
 * Essential for clinic location services and patient visit coordination.
 */
export interface Address {
  street: string;
  city: string;
  state: string;
  pincode: string;
  country: string; // Default: 'India'
  landmark?: string;
}

/**
 * Geographical location interface combining coordinates with address.
 * Supports location-based services like clinic finder and navigation.
 * Optional GPS coordinates for enhanced mapping and distance calculations.
 */
export interface Location {
  latitude?: number;
  longitude?: number;
  address: Address;
}

/**
 * Pagination metadata for efficient data retrieval and display.
 * Supports both offset-based and cursor-based pagination strategies.
 * Essential for handling large datasets like patient lists and visit history.
 */
export interface PaginationMeta {
  limit: number;
  offset?: number;
  lastEvaluatedKey?: string;
  hasMore: boolean;
  totalCount?: number;
}

/**
 * Standardized API response wrapper for consistent client communication.
 * Provides success/error status, data payload, and request correlation.
 * Includes timestamp for debugging and audit trail purposes.
 */
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  correlationId?: string;
  timestamp: string;
}

/**
 * Validation error structure for detailed field-level error reporting.
 * Provides specific error codes and field references for client handling.
 * Essential for healthcare data validation and compliance requirements.
 */
export interface ValidationError {
  field: string;
  message: string;
  code: string;
  value?: any;
}

/**
 * Base validation interface for consistent data validation across entities.
 * Ensures all healthcare models implement proper validation logic.
 * Critical for maintaining data integrity and regulatory compliance.
 */
export interface Validatable {
  validate(): ValidationError[];
  isValid(): boolean;
}

/**
 * Abstract base model class providing common functionality for all PulseOps entities.
 * Implements BaseEntity and Validatable interfaces for consistent behavior.
 * Provides automatic timestamp management and validation framework.
 * All healthcare models should extend this class for standardized functionality.
 */
export abstract class BaseModel implements BaseEntity, Validatable {
  public createdAt: string;
  public updatedAt: string;

  /**
   * Creates a new BaseModel instance with automatic timestamp initialization.
   * Sets both createdAt and updatedAt to current ISO timestamp.
   * Provides foundation for all healthcare entity models.
   */
  constructor() {
    const now = new Date().toISOString();
    this.createdAt = now;
    this.updatedAt = now;
  }

  /**
   * Abstract validation method that must be implemented by all concrete models.
   * Should perform comprehensive validation including business rules and format checking.
   * Critical for healthcare data integrity and regulatory compliance.
   * @returns Array of validation errors with specific field references and error codes
   */
  abstract validate(): ValidationError[];

  /**
   * Convenience method to check if the entity passes all validation rules.
   * Simplifies validation checking by returning boolean instead of error array.
   * @returns True if entity is valid (no validation errors), false otherwise
   */
  public isValid(): boolean {
    return this.validate().length === 0;
  }

  /**
   * Updates the entity's modification timestamp to current time.
   * Should be called whenever entity data is modified for audit trail.
   * Essential for tracking changes in healthcare records for compliance.
   */
  public touch(): void {
    this.updatedAt = new Date().toISOString();
  }
}
