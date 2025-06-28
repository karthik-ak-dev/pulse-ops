import {
  BaseModel,
  BaseEntity,
  ContactInfo,
  Address,
  SubscriptionTier,
  EntityStatus,
  ValidationError,
} from './base';

/**
 * Main clinic entity representing a healthcare organization in the PulseOps system.
 * Acts as the top-level multi-tenant boundary with complete data isolation.
 * Manages subscription billing, doctor capacity, and WhatsApp Business integration.
 */
export interface Clinic extends BaseEntity {
  clinicId: string;
  name: string;
  address: Address;
  contactInfo: ContactInfo;
  profile: ClinicProfile;
  status: EntityStatus;
  subscriptionPlan: SubscriptionTier;
  maxDoctors: number;
  currentDoctors: number;
  pricePerDoctor: number;
  totalAmount: number;
  billingCycle: BillingCycle;
  nextBillingDate: string;
  whatsappConfig: WhatsAppConfig;
  settings: ClinicSettings;
  metadata: ClinicMetadata;
}

/**
 * Extended clinic profile information including professional details,
 * specializations, and social media presence for marketing purposes.
 */
export interface ClinicProfile {
  clinicId: string;
  name: string;
  registrationNumber?: string;
  establishedYear?: number;
  specializations: string[];
  description?: string;
  website?: string;
  socialMedia?: {
    facebook?: string;
    instagram?: string;
    twitter?: string;
  };
}

/**
 * WhatsApp Business API configuration for patient communication.
 * Manages phone number ID, access tokens, and webhook settings for
 * seamless integration with WhatsApp Business platform.
 */
export interface WhatsAppConfig {
  phoneNumberId: string;
  accessToken: string;
  businessAccountId: string;
  displayPhoneNumber: string;
  isVerified: boolean;
  webhookUrl?: string;
  isActive: boolean;
  configuredAt: string;
}

/**
 * Comprehensive clinic operational settings including timezone, currency,
 * operating hours, notification preferences, feature access, and integrations.
 * Optimized for Indian healthcare market with local defaults.
 */
export interface ClinicSettings {
  timezone: string; // 'Asia/Kolkata'
  currency: string; // 'INR'
  language: string; // 'en'
  operatingHours: OperatingHours;
  notifications: NotificationSettings;
  features: FeatureSettings;
  integrations: IntegrationSettings;
}

/**
 * Weekly operating hours configuration with support for daily schedules,
 * break times, and holiday management for clinic operations.
 */
export interface OperatingHours {
  monday: DaySchedule;
  tuesday: DaySchedule;
  wednesday: DaySchedule;
  thursday: DaySchedule;
  friday: DaySchedule;
  saturday: DaySchedule;
  sunday: DaySchedule;
  holidays: Holiday[];
}

/**
 * Daily operational schedule defining opening hours, closing times,
 * and break periods for individual days of the week.
 */
export interface DaySchedule {
  isOpen: boolean;
  startTime?: string; // '09:00'
  endTime?: string; // '18:00'
  breakTime?: {
    start: string; // '13:00'
    end: string; // '14:00'
  };
}

/**
 * Holiday configuration supporting both one-time and recurring holidays
 * with descriptions for clinic calendar management.
 */
export interface Holiday {
  date: string;
  name: string;
  isRecurring: boolean;
  description?: string;
}

/**
 * Clinic-wide notification preferences controlling communication channels
 * for appointments, queue updates, payments, and emergency alerts.
 */
export interface NotificationSettings {
  enableWhatsApp: boolean;
  enableSMS: boolean;
  enableEmail: boolean;
  appointmentReminders: boolean;
  queueUpdates: boolean;
  paymentNotifications: boolean;
  emergencyAlerts: boolean;
}

/**
 * Feature access control settings based on subscription tier.
 * Manages availability of advanced features like video consultation,
 * analytics, and multi-doctor support with capacity limits.
 */
export interface FeatureSettings {
  enableOnlineBooking: boolean;
  enablePaymentCollection: boolean;
  enableVideoConsultation: boolean;
  enablePrescriptionManagement: boolean;
  enableAnalytics: boolean;
  enableReports: boolean;
  enableMultiDoctor: boolean;
  maxDoctorsAllowed: number;
}

/**
 * Third-party integration configurations for payment gateways,
 * SMS providers, email services, and analytics platforms.
 * Supports multiple Indian and international service providers.
 */
export interface IntegrationSettings {
  paymentGateway: PaymentGatewayConfig;
  smsProvider: SMSProviderConfig;
  emailProvider: EmailProviderConfig;
  analyticsProvider: AnalyticsProviderConfig;
}

/**
 * Payment gateway configuration supporting major Indian payment providers
 * like Razorpay, Paytm, and PhonePe with API credentials and webhook setup.
 */
export interface PaymentGatewayConfig {
  provider: 'RAZORPAY' | 'PAYTM' | 'PHONEPE';
  isEnabled: boolean;
  merchantId?: string;
  apiKey?: string;
  webhookSecret?: string;
  configuredAt?: string;
}

/**
 * SMS provider configuration for appointment reminders and notifications
 * supporting popular Indian SMS services with sender ID management.
 */
export interface SMSProviderConfig {
  provider: 'TWILIO' | 'MSG91' | 'TEXTLOCAL';
  isEnabled: boolean;
  apiKey?: string;
  senderId?: string;
  configuredAt?: string;
}

/**
 * Email service provider configuration for clinic communications
 * with support for major email platforms and from-address management.
 */
export interface EmailProviderConfig {
  provider: 'SENDGRID' | 'SES' | 'MAILGUN';
  isEnabled: boolean;
  apiKey?: string;
  fromEmail?: string;
  configuredAt?: string;
}

/**
 * Analytics platform integration for tracking clinic performance,
 * patient engagement, and business metrics with popular analytics services.
 */
export interface AnalyticsProviderConfig {
  provider: 'GOOGLE_ANALYTICS' | 'MIXPANEL' | 'AMPLITUDE';
  isEnabled: boolean;
  trackingId?: string;
  configuredAt?: string;
}

/**
 * Clinic performance metrics and operational statistics including
 * patient counts, revenue tracking, ratings, and compliance status.
 * Includes healthcare-specific data retention policies.
 */
export interface ClinicMetadata {
  totalPatients: number;
  totalVisits: number;
  totalRevenue: number;
  averageRating: number;
  lastActivityAt: string;
  dataRetentionDays: number;
  complianceFlags: ComplianceFlags;
}

/**
 * Healthcare compliance and regulatory status flags for HIPAA,
 * PCIDSS, SOC2 standards with policy URLs and audit tracking
 * for healthcare industry requirements.
 */
export interface ComplianceFlags {
  isHIPAACompliant: boolean;
  isPCIDSSCompliant: boolean;
  isSOC2Compliant: boolean;
  dataRetentionPolicy: string;
  privacyPolicyUrl?: string;
  termsOfServiceUrl?: string;
  lastAuditDate?: string;
}

/**
 * Subscription billing cycle options with support for monthly,
 * quarterly, and annual billing with appropriate discounts.
 */
export enum BillingCycle {
  MONTHLY = 'MONTHLY',
  QUARTERLY = 'QUARTERLY',
  ANNUALLY = 'ANNUALLY',
}

/**
 * Factory class for creating default clinic settings optimized
 * for Indian healthcare market with sensible defaults for timezone,
 * currency, operating hours, and feature availability.
 */
export class ClinicDefaultSettings {
  static createDefaultSettings(): ClinicSettings {
    return {
      timezone: 'Asia/Kolkata',
      currency: 'INR',
      language: 'en',
      operatingHours: this.createDefaultOperatingHours(),
      notifications: this.createDefaultNotificationSettings(),
      features: this.createDefaultFeatureSettings(),
      integrations: this.createDefaultIntegrationSettings(),
    };
  }

  static createDefaultOperatingHours(): OperatingHours {
    const defaultSchedule: DaySchedule = {
      isOpen: true,
      startTime: '09:00',
      endTime: '18:00',
      breakTime: {
        start: '13:00',
        end: '14:00',
      },
    };

    const sundaySchedule: DaySchedule = {
      isOpen: false,
    };

    return {
      monday: { ...defaultSchedule },
      tuesday: { ...defaultSchedule },
      wednesday: { ...defaultSchedule },
      thursday: { ...defaultSchedule },
      friday: { ...defaultSchedule },
      saturday: { ...defaultSchedule },
      sunday: { ...sundaySchedule },
      holidays: [],
    };
  }

  static createDefaultNotificationSettings(): NotificationSettings {
    return {
      enableWhatsApp: true,
      enableSMS: false,
      enableEmail: false,
      appointmentReminders: true,
      queueUpdates: true,
      paymentNotifications: true,
      emergencyAlerts: true,
    };
  }

  static createDefaultFeatureSettings(): FeatureSettings {
    return {
      enableOnlineBooking: true,
      enablePaymentCollection: true,
      enableVideoConsultation: false,
      enablePrescriptionManagement: true,
      enableAnalytics: true,
      enableReports: true,
      enableMultiDoctor: true,
      maxDoctorsAllowed: 5,
    };
  }

  static createDefaultIntegrationSettings(): IntegrationSettings {
    return {
      paymentGateway: {
        provider: 'RAZORPAY',
        isEnabled: false,
      },
      smsProvider: {
        provider: 'MSG91',
        isEnabled: false,
      },
      emailProvider: {
        provider: 'SENDGRID',
        isEnabled: false,
      },
      analyticsProvider: {
        provider: 'GOOGLE_ANALYTICS',
        isEnabled: false,
      },
    };
  }

  static createDefaultMetadata(): ClinicMetadata {
    return {
      totalPatients: 0,
      totalVisits: 0,
      totalRevenue: 0,
      averageRating: 0,
      lastActivityAt: new Date().toISOString(),
      dataRetentionDays: 2555, // 7 years default for healthcare
      complianceFlags: {
        isHIPAACompliant: false,
        isPCIDSSCompliant: false,
        isSOC2Compliant: false,
        dataRetentionPolicy: 'STANDARD',
      },
    };
  }
}

// Clinic model class
export class ClinicModel extends BaseModel implements Clinic {
  public clinicId: string;
  public name: string;
  public address: Address;
  public contactInfo: ContactInfo;
  public profile: ClinicProfile;
  public status: EntityStatus;
  public subscriptionPlan: SubscriptionTier;
  public maxDoctors: number;
  public currentDoctors: number;
  public pricePerDoctor: number;
  public totalAmount: number;
  public billingCycle: BillingCycle;
  public nextBillingDate: string;
  public whatsappConfig: WhatsAppConfig;
  public settings: ClinicSettings;
  public metadata: ClinicMetadata;

  constructor(data: Partial<Clinic>) {
    super();
    
    // Set defaults
    this.clinicId = data.clinicId || this.generateClinicId();
    this.name = data.name || '';
    this.address = data.address || this.createDefaultAddress();
    this.contactInfo = data.contactInfo || this.createDefaultContactInfo();
    this.profile = data.profile || this.createDefaultProfile();
    this.status = data.status || EntityStatus.ACTIVE;
    this.subscriptionPlan = data.subscriptionPlan || SubscriptionTier.BASIC;
    this.maxDoctors = data.maxDoctors || 5;
    this.currentDoctors = data.currentDoctors || 0;
    this.pricePerDoctor = data.pricePerDoctor || this.getPricePerDoctor();
    this.totalAmount = data.totalAmount || this.calculateSubscriptionAmount();
    this.billingCycle = data.billingCycle || BillingCycle.MONTHLY;
    this.nextBillingDate = data.nextBillingDate || this.calculateNextBillingDate();
    this.whatsappConfig = data.whatsappConfig || this.createDefaultWhatsAppConfig();
    this.settings = data.settings || ClinicDefaultSettings.createDefaultSettings();
    this.metadata = data.metadata || ClinicDefaultSettings.createDefaultMetadata();

    // Override with provided data
    Object.assign(this, data);
  }

  /**
   * Validates all clinic data according to business rules and healthcare requirements.
   * Performs comprehensive validation including Indian phone number and pincode formats.
   * @returns Array of validation errors with specific error codes and field references
   */
  public validate(): ValidationError[] {
    const errors: ValidationError[] = [];

    // Name validation
    if (!this.name || this.name.length < 2) {
      errors.push({
        field: 'name',
        message: 'Clinic name must be at least 2 characters',
        code: 'INVALID_NAME',
        value: this.name,
      });
    }

    if (this.name && this.name.length > 100) {
      errors.push({
        field: 'name',
        message: 'Clinic name cannot exceed 100 characters',
        code: 'NAME_TOO_LONG',
        value: this.name,
      });
    }

    // Contact information validation
    if (!this.contactInfo?.phone) {
      errors.push({
        field: 'contactInfo.phone',
        message: 'Phone number is required',
        code: 'MISSING_PHONE',
      });
    } else if (!this.isValidIndianPhone(this.contactInfo.phone)) {
      errors.push({
        field: 'contactInfo.phone',
        message: 'Valid Indian phone number required (+91XXXXXXXXXX)',
        code: 'INVALID_PHONE',
        value: this.contactInfo.phone,
      });
    }

    // Address validation
    if (!this.address?.street) {
      errors.push({
        field: 'address.street',
        message: 'Street address is required',
        code: 'MISSING_ADDRESS',
      });
    }

    if (!this.address?.city) {
      errors.push({
        field: 'address.city',
        message: 'City is required',
        code: 'MISSING_CITY',
      });
    }

    if (!this.address?.state) {
      errors.push({
        field: 'address.state',
        message: 'State is required',
        code: 'MISSING_STATE',
      });
    }

    if (!this.address?.pincode) {
      errors.push({
        field: 'address.pincode',
        message: 'Pincode is required',
        code: 'MISSING_PINCODE',
      });
    } else if (!this.isValidIndianPincode(this.address.pincode)) {
      errors.push({
        field: 'address.pincode',
        message: 'Valid 6-digit Indian pincode required',
        code: 'INVALID_PINCODE',
        value: this.address.pincode,
      });
    }

    // Subscription validation
    if (this.currentDoctors < 0) {
      errors.push({
        field: 'currentDoctors',
        message: 'Current doctors count cannot be negative',
        code: 'INVALID_DOCTOR_COUNT',
        value: this.currentDoctors,
      });
    }

    if (this.maxDoctors < 1) {
      errors.push({
        field: 'maxDoctors',
        message: 'Max doctors must be at least 1',
        code: 'INVALID_MAX_DOCTORS',
        value: this.maxDoctors,
      });
    }

    if (this.currentDoctors > this.maxDoctors) {
      errors.push({
        field: 'currentDoctors',
        message: 'Current doctors cannot exceed maximum allowed',
        code: 'EXCEEDS_MAX_DOCTORS',
        value: this.currentDoctors,
      });
    }

    // WhatsApp configuration validation
    if (this.whatsappConfig?.isActive) {
      if (!this.whatsappConfig.phoneNumberId) {
        errors.push({
          field: 'whatsappConfig.phoneNumberId',
          message: 'WhatsApp Phone Number ID is required when active',
          code: 'MISSING_WHATSAPP_PHONE_ID',
        });
      }

      if (!this.whatsappConfig.accessToken) {
        errors.push({
          field: 'whatsappConfig.accessToken',
          message: 'WhatsApp Access Token is required when active',
          code: 'MISSING_WHATSAPP_TOKEN',
        });
      }

      if (!this.whatsappConfig.businessAccountId) {
        errors.push({
          field: 'whatsappConfig.businessAccountId',
          message: 'WhatsApp Business Account ID is required when active',
          code: 'MISSING_WHATSAPP_BUSINESS_ID',
        });
      }
    }

    return errors;
  }

  /**
   * Calculates the total subscription amount based on current doctor count and billing cycle.
   * Applies discounts for quarterly (5%) and annual (15%) billing cycles.
   * @returns Total subscription amount in INR for the current billing period
   */
  public calculateSubscriptionAmount(): number {
    const pricePerDoctor = this.getPricePerDoctor();
    const amount = this.currentDoctors * pricePerDoctor;
    
    // Apply billing cycle multiplier
    switch (this.billingCycle) {
      case BillingCycle.QUARTERLY:
        return amount * 3 * 0.95; // 5% discount for quarterly
      case BillingCycle.ANNUALLY:
        return amount * 12 * 0.85; // 15% discount for annual
      default:
        return amount;
    }
  }

  /**
   * Gets the monthly price per doctor based on the current subscription tier.
   * Pricing optimized for Indian healthcare market with tier-based discounts.
   * @returns Monthly price per doctor in INR (Basic: ₹799, Professional: ₹649, Enterprise: ₹549)
   */
  public getPricePerDoctor(): number {
    switch (this.subscriptionPlan) {
      case SubscriptionTier.BASIC:
        return 799;
      case SubscriptionTier.PROFESSIONAL:
        return 649;
      case SubscriptionTier.ENTERPRISE:
        return 549;
      default:
        return 799;
    }
  }

  /**
   * Checks if a new doctor can be added to the clinic.
   * Validates against maximum doctor limit and clinic active status.
   * @returns True if doctor can be added, false otherwise
   */
  public canAddDoctor(): boolean {
    return this.currentDoctors < this.maxDoctors && this.status === EntityStatus.ACTIVE;
  }

  /**
   * Adds a new doctor to the clinic and recalculates subscription amount.
   * Updates the current doctor count and total billing amount automatically.
   * @returns True if doctor was successfully added, false if limit reached or clinic inactive
   */
  public addDoctor(): boolean {
    if (!this.canAddDoctor()) {
      return false;
    }

    this.currentDoctors += 1;
    this.totalAmount = this.calculateSubscriptionAmount();
    this.touch();
    return true;
  }

  /**
   * Removes a doctor from the clinic and recalculates subscription amount.
   * Updates the current doctor count and total billing amount automatically.
   * @returns True if doctor was successfully removed, false if no doctors to remove
   */
  public removeDoctor(): boolean {
    if (this.currentDoctors <= 0) {
      return false;
    }

    this.currentDoctors -= 1;
    this.totalAmount = this.calculateSubscriptionAmount();
    this.touch();
    return true;
  }

  /**
   * Updates the clinic's subscription plan and recalculates all pricing.
   * Automatically adjusts price per doctor, total amount, and maximum doctor limits.
   * @param newPlan The new subscription tier to apply
   */
  public updateSubscriptionPlan(newPlan: SubscriptionTier): void {
    this.subscriptionPlan = newPlan;
    this.pricePerDoctor = this.getPricePerDoctor();
    this.totalAmount = this.calculateSubscriptionAmount();
    this.maxDoctors = this.getMaxDoctorsForPlan(newPlan);
    this.touch();
  }

  /**
   * Checks if WhatsApp Business API is properly configured and active.
   * Validates presence of required credentials for WhatsApp integration.
   * @returns True if WhatsApp is fully configured and active, false otherwise
   */
  public isWhatsAppConfigured(): boolean {
    return !!(
      this.whatsappConfig?.isActive &&
      this.whatsappConfig?.phoneNumberId &&
      this.whatsappConfig?.accessToken &&
      this.whatsappConfig?.businessAccountId
    );
  }

  /**
   * Gets the operating schedule for a specific day of the week.
   * Returns schedule information including opening hours and break times.
   * @param day Day of the week (e.g., 'monday', 'tuesday', etc.)
   * @returns DaySchedule object or null if invalid day provided
   */
  public getOperatingStatus(day: string): DaySchedule | null {
    const dayKey = day.toLowerCase() as keyof Omit<OperatingHours, 'holidays'>;
    const validDays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
    
    if (!validDays.includes(dayKey)) {
      return null;
    }
    
    return this.settings?.operatingHours?.[dayKey] || null;
  }

  /**
   * Checks if the clinic is open on a specific day of the week.
   * Convenience method to quickly determine operational status.
   * @param day Day of the week to check
   * @returns True if clinic is open on the specified day, false otherwise
   */
  public isOperatingOn(day: string): boolean {
    const schedule = this.getOperatingStatus(day);
    return schedule?.isOpen || false;
  }

  /**
   * Gets a list of currently active features based on clinic settings.
   * Returns feature codes for enabled functionality like online booking, payments, etc.
   * @returns Array of active feature codes (e.g., ['ONLINE_BOOKING', 'PAYMENT_COLLECTION'])
   */
  public getActiveFeatures(): string[] {
    if (!this.settings?.features) return [];

    const features: string[] = [];
    const featureMap = {
      enableOnlineBooking: 'ONLINE_BOOKING',
      enablePaymentCollection: 'PAYMENT_COLLECTION',
      enableVideoConsultation: 'VIDEO_CONSULTATION',
      enablePrescriptionManagement: 'PRESCRIPTION_MANAGEMENT',
      enableAnalytics: 'ANALYTICS',
      enableReports: 'REPORTS',
      enableMultiDoctor: 'MULTI_DOCTOR',
    };

    Object.entries(featureMap).forEach(([key, feature]) => {
      if (this.settings.features[key as keyof FeatureSettings]) {
        features.push(feature);
      }
    });

    return features;
  }

  /**
   * Updates clinic metadata with new statistics and performance metrics.
   * Automatically updates lastActivityAt timestamp and touches the entity.
   * @param updates Partial metadata updates to apply
   */
  public updateMetadata(updates: Partial<ClinicMetadata>): void {
    this.metadata = { ...this.metadata, ...updates };
    this.metadata.lastActivityAt = new Date().toISOString();
    this.touch();
  }

  /**
   * Generates a unique clinic ID using timestamp and random string.
   * Creates a clinic-prefixed identifier for database and reference purposes.
   * @private
   * @returns Unique clinic identifier in format 'clinic_{timestamp}_{random}'
   */
  private generateClinicId(): string {
    const timestamp = Date.now().toString(36);
    const random = Math.random().toString(36).substr(2, 5);
    return `clinic_${timestamp}_${random}`;
  }

  /**
   * Creates default Indian address structure with empty fields.
   * Sets country to 'India' by default for localization.
   * @private
   * @returns Default address object with Indian country setting
   */
  private createDefaultAddress(): Address {
    return {
      street: '',
      city: '',
      state: '',
      pincode: '',
      country: 'India',
    };
  }

  /**
   * Creates default contact information structure.
   * Initializes phone and WhatsApp number fields as empty strings.
   * @private
   * @returns Default contact information object
   */
  private createDefaultContactInfo(): ContactInfo {
    return {
      phone: '',
      whatsappNumber: '',
    };
  }

  /**
   * Creates default clinic profile with basic information.
   * Links profile to clinic ID and initializes empty specializations array.
   * @private
   * @returns Default clinic profile object
   */
  private createDefaultProfile(): ClinicProfile {
    return {
      clinicId: this.clinicId,
      name: this.name || '',
      specializations: [],
    };
  }

  /**
   * Creates default WhatsApp Business configuration in inactive state.
   * Initializes all required fields as empty with current timestamp.
   * @private
   * @returns Default WhatsApp configuration object
   */
  private createDefaultWhatsAppConfig(): WhatsAppConfig {
    return {
      phoneNumberId: '',
      accessToken: '',
      businessAccountId: '',
      displayPhoneNumber: '',
      isVerified: false,
      isActive: false,
      configuredAt: new Date().toISOString(),
    };
  }

  /**
   * Calculates the next billing date based on current billing cycle.
   * Adds appropriate months/years to current date for next billing period.
   * @private
   * @returns ISO string of next billing date
   */
  private calculateNextBillingDate(): string {
    const now = new Date();
    const nextBilling = new Date(now);

    switch (this.billingCycle) {
      case BillingCycle.MONTHLY:
        nextBilling.setMonth(now.getMonth() + 1);
        break;
      case BillingCycle.QUARTERLY:
        nextBilling.setMonth(now.getMonth() + 3);
        break;
      case BillingCycle.ANNUALLY:
        nextBilling.setFullYear(now.getFullYear() + 1);
        break;
    }

    return nextBilling.toISOString();
  }

  /**
   * Gets the maximum number of doctors allowed for a subscription tier.
   * Returns tier-specific limits: Basic (5), Professional (20), Enterprise (100).
   * @private
   * @param plan Subscription tier to check
   * @returns Maximum number of doctors allowed for the plan
   */
  private getMaxDoctorsForPlan(plan: SubscriptionTier): number {
    switch (plan) {
      case SubscriptionTier.BASIC:
        return 5;
      case SubscriptionTier.PROFESSIONAL:
        return 20;
      case SubscriptionTier.ENTERPRISE:
        return 100;
      default:
        return 5;
    }
  }

  /**
   * Validates Indian phone number format (+91 followed by 10 digits starting with 6-9).
   * Ensures compliance with Indian mobile number standards.
   * @private
   * @param phone Phone number to validate
   * @returns True if valid Indian phone number, false otherwise
   */
  private isValidIndianPhone(phone: string): boolean {
    const indianPhoneRegex = /^\+91[6-9]\d{9}$/;
    return indianPhoneRegex.test(phone);
  }

  /**
   * Validates Indian pincode format (6 digits, first digit 1-9).
   * Ensures compliance with Indian postal code standards.
   * @private
   * @param pincode Pincode to validate
   * @returns True if valid Indian pincode, false otherwise
   */
  private isValidIndianPincode(pincode: string): boolean {
    const pincodeRegex = /^[1-9][0-9]{5}$/;
    return pincodeRegex.test(pincode);
  }

  /**
   * Factory method to create a fully configured clinic with complete information.
   * Creates an active clinic with provided details and optional subscription plan.
   * @static
   * @param data Object containing name, contact info, address, and optional subscription plan
   * @returns New ClinicModel instance with ACTIVE status and complete configuration
   */
  static create(data: {
    name: string;
    contactInfo: ContactInfo;
    address: Address;
    subscriptionPlan?: SubscriptionTier;
  }): ClinicModel {
    return new ClinicModel({
      name: data.name,
      contactInfo: data.contactInfo,
      address: data.address,
      subscriptionPlan: data.subscriptionPlan || SubscriptionTier.BASIC,
      status: EntityStatus.ACTIVE,
    });
  }

  /**
   * Factory method to create a basic clinic with minimal information for quick setup.
   * Creates a clinic in PENDING status with just name and phone number for onboarding.
   * @static
   * @param name Clinic name
   * @param phone Indian phone number (+91XXXXXXXXXX format)
   * @returns New ClinicModel instance with PENDING status for completion during onboarding
   */
  static createBasic(name: string, phone: string): ClinicModel {
    return new ClinicModel({
      name,
      contactInfo: {
        phone,
        whatsappNumber: phone,
      },
      address: {
        street: '',
        city: '',
        state: '',
        pincode: '',
        country: 'India',
      },
      subscriptionPlan: SubscriptionTier.BASIC,
      status: EntityStatus.PENDING,
    });
  }
}
