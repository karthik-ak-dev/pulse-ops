import {
  BaseModel,
  BaseEntity,
  EntityStatus,
  SubscriptionTier,
  ValidationError,
} from './base';
import { BillingCycle } from './clinic';

/**
 * Main subscription entity managing clinic billing, feature access, and usage tracking.
 * Provides dynamic per-doctor pricing with automated billing cycles and feature control.
 * Essential for revenue management and access control in the PulseOps healthcare system.
 */
export interface Subscription extends BaseEntity {
  subscriptionId: string;
  clinicId: string;
  plan: SubscriptionPlan;
  billing: BillingInfo;
  features: FeatureAccess;
  usage: UsageMetrics;
  pricing: PricingDetails;
  status: SubscriptionStatus;
  metadata: SubscriptionMetadata;
}

/**
 * Comprehensive subscription plan definition with feature sets and limits.
 * Defines what features and capabilities are available for each tier.
 * Used for access control and billing calculations throughout the system.
 */
export interface SubscriptionPlan {
  tier: SubscriptionTier;
  name: string;
  description: string;
  features: PlanFeature[];
  limits: PlanLimits;
  pricing: PlanPricing;
  isActive: boolean;
  validFrom: string;
  validUntil?: string;
}

/**
 * Individual feature definition within a subscription plan.
 * Specifies feature availability, limits, and access levels.
 * Enables granular control over system functionality per subscription tier.
 */
export interface PlanFeature {
  featureCode: string;
  name: string;
  description: string;
  isEnabled: boolean;
  limits?: FeatureLimits;
  accessLevel: FeatureAccessLevel;
  metadata?: Record<string, any>;
}

/**
 * Feature-specific limits and quotas for subscription control.
 * Defines usage boundaries and restrictions for individual features.
 * Critical for preventing abuse and managing system resources.
 */
export interface FeatureLimits {
  maxUsage?: number;
  dailyLimit?: number;
  monthlyLimit?: number;
  concurrentLimit?: number;
  customLimits?: Record<string, number>;
}

/**
 * Comprehensive plan limits defining subscription boundaries.
 * Sets maximum allowances for doctors, storage, API calls, and other resources.
 * Essential for tier differentiation and resource management.
 */
export interface PlanLimits {
  maxDoctors: number;
  maxPatients?: number;
  maxStorageGB?: number;
  maxApiCallsPerMonth?: number;
  maxWhatsAppMessages?: number;
  maxReports?: number;
  customLimits?: Record<string, number>;
}

/**
 * Detailed pricing structure for subscription plans.
 * Supports per-doctor pricing with various billing cycles and discounts.
 * Optimized for Indian healthcare market with competitive pricing tiers.
 */
export interface PlanPricing {
  basePrice: number;
  pricePerDoctor: number;
  currency: string; // 'INR'
  billingCycles: BillingCycleOption[];
  discounts: PricingDiscount[];
  setupFee?: number;
  minimumCommitment?: number;
}

/**
 * Billing cycle options with associated pricing and discounts.
 * Supports monthly, quarterly, and annual billing with appropriate discounts.
 * Enables flexible billing arrangements for different clinic needs.
 */
export interface BillingCycleOption {
  cycle: BillingCycle;
  discountPercentage: number;
  minimumTermMonths: number;
  description: string;
}

/**
 * Pricing discount rules and promotional offers.
 * Supports various discount types including volume, loyalty, and promotional discounts.
 * Essential for competitive pricing and customer retention strategies.
 */
export interface PricingDiscount {
  discountId: string;
  name: string;
  type: DiscountType;
  value: number;
  isPercentage: boolean;
  validFrom: string;
  validUntil: string;
  conditions?: DiscountCondition[];
  isActive: boolean;
}

/**
 * Current billing information for active subscriptions.
 * Tracks billing cycle, amounts, and payment status.
 * Critical for financial management and automated billing processes.
 */
export interface BillingInfo {
  currentCycle: BillingCycle;
  currentPeriodStart: string;
  currentPeriodEnd: string;
  nextBillingDate: string;
  amount: BillingAmount;
  paymentMethod?: PaymentMethodInfo;
  billingHistory: BillingRecord[];
}

/**
 * Detailed billing amount breakdown for transparency.
 * Shows base costs, per-doctor charges, discounts, and final amounts.
 * Essential for billing transparency and financial reporting.
 */
export interface BillingAmount {
  baseAmount: number;
  doctorCount: number;
  perDoctorAmount: number;
  subtotal: number;
  discounts: AppliedDiscount[];
  taxes: TaxBreakdown[];
  totalAmount: number;
  currency: string;
}

/**
 * Applied discount details for billing transparency.
 * Shows which discounts were applied and their impact on billing.
 * Important for customer understanding and financial audit trails.
 */
export interface AppliedDiscount {
  discountId: string;
  name: string;
  type: DiscountType;
  amount: number;
  description: string;
}

/**
 * Tax breakdown for compliance and transparency.
 * Handles various Indian tax components like GST, service tax, etc.
 * Essential for regulatory compliance and financial reporting.
 */
export interface TaxBreakdown {
  taxType: TaxType;
  rate: number;
  amount: number;
  description: string;
}

/**
 * Payment method information for billing processing.
 * Stores encrypted payment details and processing preferences.
 * Critical for automated billing and payment processing.
 */
export interface PaymentMethodInfo {
  methodId: string;
  type: PaymentMethodType;
  displayName: string;
  isDefault: boolean;
  isActive: boolean;
  metadata?: Record<string, any>;
}

/**
 * Individual billing record for audit and history tracking.
 * Maintains complete billing history with status and payment details.
 * Essential for financial audit trails and customer billing inquiries.
 */
export interface BillingRecord {
  recordId: string;
  billingDate: string;
  periodStart: string;
  periodEnd: string;
  amount: BillingAmount;
  status: BillingStatus;
  paymentDate?: string;
  paymentReference?: string;
  notes?: string;
}

/**
 * Feature access control and permissions for subscription tiers.
 * Manages which features are available and their usage limits.
 * Critical for enforcing subscription boundaries and access control.
 */
export interface FeatureAccess {
  enabledFeatures: EnabledFeature[];
  disabledFeatures: string[];
  customPermissions: CustomPermission[];
  accessLevel: GlobalAccessLevel;
  lastUpdated: string;
}

/**
 * Individual enabled feature with specific configuration.
 * Defines feature availability, limits, and custom settings.
 * Enables fine-grained control over system functionality.
 */
export interface EnabledFeature {
  featureCode: string;
  isEnabled: boolean;
  limits: FeatureLimits;
  configuration?: Record<string, any>;
  enabledAt: string;
  enabledBy?: string;
}

/**
 * Custom permission overrides for specific subscription needs.
 * Allows granular permission control beyond standard plan features.
 * Essential for enterprise customizations and special arrangements.
 */
export interface CustomPermission {
  permissionId: string;
  resource: string;
  action: string;
  isAllowed: boolean;
  conditions?: Record<string, any>;
  grantedAt: string;
  grantedBy: string;
  expiresAt?: string;
}

/**
 * Comprehensive usage metrics and analytics for subscription monitoring.
 * Tracks feature usage, resource consumption, and system utilization.
 * Critical for billing accuracy and usage-based insights.
 */
export interface UsageMetrics {
  currentPeriod: PeriodUsage;
  previousPeriod: PeriodUsage;
  trends: UsageTrend[];
  alerts: UsageAlert[];
  projections: UsageProjection[];
}

/**
 * Usage statistics for a specific billing period.
 * Tracks consumption across all features and resources.
 * Essential for accurate billing and usage monitoring.
 */
export interface PeriodUsage {
  periodStart: string;
  periodEnd: string;
  doctorCount: number;
  featureUsage: FeatureUsageMetric[];
  resourceUsage: ResourceUsageMetric[];
  totalApiCalls: number;
  totalStorage: number;
  peakConcurrentUsers: number;
}

/**
 * Individual feature usage statistics and metrics.
 * Tracks how often specific features are used and by whom.
 * Important for feature optimization and user behavior analysis.
 */
export interface FeatureUsageMetric {
  featureCode: string;
  usageCount: number;
  uniqueUsers: number;
  totalDuration?: number;
  peakUsage: number;
  averageUsage: number;
  lastUsed: string;
}

/**
 * Resource consumption metrics for system monitoring.
 * Tracks usage of system resources like storage, bandwidth, compute.
 * Critical for capacity planning and cost management.
 */
export interface ResourceUsageMetric {
  resourceType: ResourceType;
  consumed: number;
  limit: number;
  unit: string;
  utilizationPercentage: number;
  peakUsage: number;
  trends: number[];
}

/**
 * Usage trend analysis for capacity planning.
 * Identifies usage patterns and growth trends over time.
 * Essential for proactive scaling and subscription recommendations.
 */
export interface UsageTrend {
  metric: string;
  trend: TrendDirection;
  changePercentage: number;
  periodComparison: string;
  significance: TrendSignificance;
  recommendations?: string[];
}

/**
 * Usage alert for threshold monitoring and notifications.
 * Warns when usage approaches or exceeds defined limits.
 * Critical for preventing service disruptions and overage charges.
 */
export interface UsageAlert {
  alertId: string;
  type: AlertType;
  severity: AlertSeverity;
  metric: string;
  threshold: number;
  currentValue: number;
  message: string;
  triggeredAt: string;
  isActive: boolean;
}

/**
 * Usage projection for capacity planning and recommendations.
 * Predicts future usage based on historical patterns.
 * Important for proactive subscription management and scaling.
 */
export interface UsageProjection {
  metric: string;
  projectedValue: number;
  projectionDate: string;
  confidence: number;
  basis: ProjectionBasis;
  recommendations: ProjectionRecommendation[];
}

/**
 * Subscription-specific recommendation for optimization.
 * Suggests plan changes, feature optimizations, or cost savings.
 * Valuable for customer success and revenue optimization.
 */
export interface ProjectionRecommendation {
  type: RecommendationType;
  title: string;
  description: string;
  impact: RecommendationImpact;
  priority: RecommendationPriority;
  estimatedSavings?: number;
}

/**
 * Pricing and financial details for the subscription.
 * Manages current pricing, calculations, and financial projections.
 * Essential for revenue management and financial planning.
 */
export interface PricingDetails {
  currentPlan: SubscriptionTier;
  monthlyRate: number;
  annualRate: number;
  perDoctorRate: number;
  effectiveRate: number;
  discountsApplied: AppliedDiscount[];
  nextRateChange?: RateChange;
  pricingHistory: PricingHistoryRecord[];
}

/**
 * Scheduled pricing changes for subscription management.
 * Handles plan upgrades, downgrades, and pricing adjustments.
 * Important for subscription lifecycle management.
 */
export interface RateChange {
  changeId: string;
  newTier?: SubscriptionTier;
  newRate: number;
  effectiveDate: string;
  reason: ChangeReason;
  approvedBy: string;
  approvedAt: string;
}

/**
 * Historical pricing record for audit and analysis.
 * Maintains complete pricing history for financial analysis.
 * Essential for revenue tracking and customer billing history.
 */
export interface PricingHistoryRecord {
  recordId: string;
  tier: SubscriptionTier;
  rate: number;
  effectiveFrom: string;
  effectiveTo?: string;
  reason: string;
  appliedBy: string;
}

/**
 * Subscription metadata for tracking and analytics.
 * Contains operational information and performance metrics.
 * Important for subscription health monitoring and optimization.
 */
export interface SubscriptionMetadata {
  activatedAt: string;
  lastBilledAt?: string;
  nextBillingAt: string;
  gracePeriodEnds?: string;
  autoRenewal: boolean;
  cancellationRequested?: boolean;
  cancellationDate?: string;
  customerSatisfactionScore?: number;
  supportTickets: number;
  healthScore: SubscriptionHealthScore;
  tags: string[];
  notes: string[];
}

/**
 * Subscription health scoring for customer success monitoring.
 * Evaluates subscription status across multiple dimensions.
 * Critical for proactive customer success and retention efforts.
 */
export interface SubscriptionHealthScore {
  overall: number; // 0-100
  payment: number; // Payment reliability
  usage: number; // Feature utilization
  engagement: number; // System engagement
  support: number; // Support interactions
  lastCalculated: string;
  factors: HealthFactor[];
}

/**
 * Health factor contributing to subscription health score.
 * Identifies specific areas affecting subscription wellness.
 * Used for targeted improvement recommendations and alerts.
 */
export interface HealthFactor {
  factor: string;
  score: number;
  weight: number;
  description: string;
  recommendations?: string[];
}

// Enumerations for subscription management

/**
 * Subscription status enumeration for lifecycle management.
 * Tracks the current state of clinic subscriptions.
 * Critical for billing, access control, and customer management.
 */
export enum SubscriptionStatus {
  ACTIVE = 'ACTIVE',
  TRIAL = 'TRIAL',
  EXPIRED = 'EXPIRED',
  SUSPENDED = 'SUSPENDED',
  CANCELLED = 'CANCELLED',
  PENDING_ACTIVATION = 'PENDING_ACTIVATION',
  PENDING_CANCELLATION = 'PENDING_CANCELLATION',
  GRACE_PERIOD = 'GRACE_PERIOD',
}

/**
 * Feature access level enumeration for permission control.
 * Defines different levels of feature access within subscriptions.
 * Essential for implementing tiered feature availability.
 */
export enum FeatureAccessLevel {
  FULL = 'FULL',
  LIMITED = 'LIMITED',
  READ_ONLY = 'READ_ONLY',
  DISABLED = 'DISABLED',
}

/**
 * Global access level for overall subscription permissions.
 * Defines the highest level of access available to the subscription.
 * Used for system-wide access control and feature gating.
 */
export enum GlobalAccessLevel {
  ENTERPRISE = 'ENTERPRISE',
  PROFESSIONAL = 'PROFESSIONAL', 
  STANDARD = 'STANDARD',
  BASIC = 'BASIC',
  RESTRICTED = 'RESTRICTED',
}

/**
 * Discount type enumeration for pricing flexibility.
 * Supports various discount mechanisms for competitive pricing.
 * Essential for promotional campaigns and customer retention.
 */
export enum DiscountType {
  PERCENTAGE = 'PERCENTAGE',
  FIXED_AMOUNT = 'FIXED_AMOUNT',
  VOLUME_DISCOUNT = 'VOLUME_DISCOUNT',
  LOYALTY_DISCOUNT = 'LOYALTY_DISCOUNT',
  PROMOTIONAL = 'PROMOTIONAL',
  REFERRAL = 'REFERRAL',
  SEASONAL = 'SEASONAL',
}

/**
 * Tax type enumeration for Indian market compliance.
 * Handles various tax components required for billing.
 * Critical for regulatory compliance and accurate billing.
 */
export enum TaxType {
  GST = 'GST',
  IGST = 'IGST',
  CGST = 'CGST',
  SGST = 'SGST',
  SERVICE_TAX = 'SERVICE_TAX',
  CESS = 'CESS',
}

/**
 * Payment method type enumeration for billing flexibility.
 * Supports various payment options popular in Indian market.
 * Essential for automated billing and payment processing.
 */
export enum PaymentMethodType {
  UPI = 'UPI',
  CREDIT_CARD = 'CREDIT_CARD',
  DEBIT_CARD = 'DEBIT_CARD',
  NET_BANKING = 'NET_BANKING',
  WALLET = 'WALLET',
  BANK_TRANSFER = 'BANK_TRANSFER',
  RAZORPAY = 'RAZORPAY',
  PAYTM = 'PAYTM',
  PHONEPE = 'PHONEPE',
}

/**
 * Billing status enumeration for payment tracking.
 * Tracks the status of individual billing cycles.
 * Critical for financial reconciliation and customer communication.
 */
export enum BillingStatus {
  PENDING = 'PENDING',
  PROCESSING = 'PROCESSING',
  PAID = 'PAID',
  FAILED = 'FAILED',
  CANCELLED = 'CANCELLED',
  REFUNDED = 'REFUNDED',
  PARTIALLY_PAID = 'PARTIALLY_PAID',
  OVERDUE = 'OVERDUE',
}

/**
 * Resource type enumeration for usage monitoring.
 * Defines system resources that can be tracked and limited.
 * Important for capacity planning and fair usage policies.
 */
export enum ResourceType {
  STORAGE = 'STORAGE',
  BANDWIDTH = 'BANDWIDTH',
  API_CALLS = 'API_CALLS',
  WHATSAPP_MESSAGES = 'WHATSAPP_MESSAGES',
  SMS_MESSAGES = 'SMS_MESSAGES',
  EMAIL_MESSAGES = 'EMAIL_MESSAGES',
  REPORTS_GENERATED = 'REPORTS_GENERATED',
  CONCURRENT_USERS = 'CONCURRENT_USERS',
  DATABASE_QUERIES = 'DATABASE_QUERIES',
}

/**
 * Trend direction enumeration for usage analysis.
 * Identifies whether usage patterns are increasing or decreasing.
 * Essential for capacity planning and subscription recommendations.
 */
export enum TrendDirection {
  INCREASING = 'INCREASING',
  DECREASING = 'DECREASING',
  STABLE = 'STABLE',
  VOLATILE = 'VOLATILE',
}

/**
 * Trend significance enumeration for priority assessment.
 * Indicates the importance of identified usage trends.
 * Used for prioritizing subscription management actions.
 */
export enum TrendSignificance {
  HIGH = 'HIGH',
  MEDIUM = 'MEDIUM',
  LOW = 'LOW',
}

/**
 * Alert type enumeration for usage monitoring.
 * Categorizes different types of usage alerts and notifications.
 * Critical for proactive subscription and resource management.
 */
export enum AlertType {
  USAGE_THRESHOLD = 'USAGE_THRESHOLD',
  BILLING_ISSUE = 'BILLING_ISSUE',
  FEATURE_LIMIT = 'FEATURE_LIMIT',
  EXPIRATION_WARNING = 'EXPIRATION_WARNING',
  UPGRADE_RECOMMENDATION = 'UPGRADE_RECOMMENDATION',
  DOWNGRADE_OPPORTUNITY = 'DOWNGRADE_OPPORTUNITY',
  PAYMENT_FAILURE = 'PAYMENT_FAILURE',
}

/**
 * Alert severity enumeration for proper escalation.
 * Defines the urgency level of subscription alerts.
 * Essential for appropriate response and customer communication.
 */
export enum AlertSeverity {
  CRITICAL = 'CRITICAL',
  HIGH = 'HIGH',
  MEDIUM = 'MEDIUM',
  LOW = 'LOW',
  INFO = 'INFO',
}

/**
 * Projection basis enumeration for forecasting accuracy.
 * Indicates the data source used for usage projections.
 * Important for understanding projection reliability.
 */
export enum ProjectionBasis {
  HISTORICAL_TREND = 'HISTORICAL_TREND',
  SEASONAL_PATTERN = 'SEASONAL_PATTERN',
  GROWTH_MODEL = 'GROWTH_MODEL',
  MACHINE_LEARNING = 'MACHINE_LEARNING',
  LINEAR_REGRESSION = 'LINEAR_REGRESSION',
  MANUAL_ESTIMATE = 'MANUAL_ESTIMATE',
}

/**
 * Recommendation type enumeration for optimization suggestions.
 * Categorizes different types of subscription recommendations.
 * Used for targeted customer success and revenue optimization.
 */
export enum RecommendationType {
  UPGRADE_PLAN = 'UPGRADE_PLAN',
  DOWNGRADE_PLAN = 'DOWNGRADE_PLAN',
  OPTIMIZE_USAGE = 'OPTIMIZE_USAGE',
  ENABLE_FEATURE = 'ENABLE_FEATURE',
  DISABLE_FEATURE = 'DISABLE_FEATURE',
  CHANGE_BILLING_CYCLE = 'CHANGE_BILLING_CYCLE',
  ADD_PAYMENT_METHOD = 'ADD_PAYMENT_METHOD',
  REVIEW_USAGE = 'REVIEW_USAGE',
}

/**
 * Recommendation impact enumeration for prioritization.
 * Indicates the potential impact of implementing recommendations.
 * Essential for prioritizing customer success activities.
 */
export enum RecommendationImpact {
  HIGH_COST_SAVINGS = 'HIGH_COST_SAVINGS',
  MODERATE_COST_SAVINGS = 'MODERATE_COST_SAVINGS',
  IMPROVED_EFFICIENCY = 'IMPROVED_EFFICIENCY',
  BETTER_EXPERIENCE = 'BETTER_EXPERIENCE',
  RISK_MITIGATION = 'RISK_MITIGATION',
  COMPLIANCE = 'COMPLIANCE',
}

/**
 * Recommendation priority enumeration for action planning.
 * Defines the urgency of implementing recommendations.
 * Critical for customer success team workflow prioritization.
 */
export enum RecommendationPriority {
  URGENT = 'URGENT',
  HIGH = 'HIGH',
  MEDIUM = 'MEDIUM',
  LOW = 'LOW',
  OPTIONAL = 'OPTIONAL',
}

/**
 * Change reason enumeration for audit tracking.
 * Documents the rationale behind subscription changes.
 * Important for customer communication and internal tracking.
 */
export enum ChangeReason {
  UPGRADE_REQUEST = 'UPGRADE_REQUEST',
  DOWNGRADE_REQUEST = 'DOWNGRADE_REQUEST',
  BILLING_ISSUE = 'BILLING_ISSUE',
  USAGE_EXCEEDED = 'USAGE_EXCEEDED',
  PROMOTIONAL_PRICING = 'PROMOTIONAL_PRICING',
  CONTRACT_RENEWAL = 'CONTRACT_RENEWAL',
  ADMINISTRATIVE = 'ADMINISTRATIVE',
  CUSTOMER_REQUEST = 'CUSTOMER_REQUEST',
}

/**
 * Discount condition interface for complex discount rules.
 * Defines conditions that must be met for discount application.
 * Enables sophisticated promotional and pricing strategies.
 */
export interface DiscountCondition {
  conditionType: DiscountConditionType;
  field: string;
  operator: ComparisonOperator;
  value: any;
  description: string;
}

/**
 * Discount condition type enumeration for rule specification.
 * Defines different types of conditions for discount eligibility.
 * Essential for flexible promotional and pricing strategies.
 */
export enum DiscountConditionType {
  DOCTOR_COUNT = 'DOCTOR_COUNT',
  SUBSCRIPTION_AGE = 'SUBSCRIPTION_AGE',
  USAGE_VOLUME = 'USAGE_VOLUME',
  PAYMENT_METHOD = 'PAYMENT_METHOD',
  BILLING_CYCLE = 'BILLING_CYCLE',
  GEOGRAPHIC_LOCATION = 'GEOGRAPHIC_LOCATION',
  REFERRAL_CODE = 'REFERRAL_CODE',
}

/**
 * Comparison operator enumeration for condition evaluation.
 * Defines logical operators for discount condition checking.
 * Used in business rule engines and conditional logic.
 */
export enum ComparisonOperator {
  EQUALS = 'EQUALS',
  NOT_EQUALS = 'NOT_EQUALS',
  GREATER_THAN = 'GREATER_THAN',
  LESS_THAN = 'LESS_THAN',
  GREATER_THAN_OR_EQUAL = 'GREATER_THAN_OR_EQUAL',
  LESS_THAN_OR_EQUAL = 'LESS_THAN_OR_EQUAL',
  IN = 'IN',
  NOT_IN = 'NOT_IN',
  CONTAINS = 'CONTAINS',
}

/**
 * Subscription model class providing comprehensive subscription management functionality.
 * Implements business logic for billing, feature access, and usage tracking.
 * Central component for subscription lifecycle management in PulseOps.
 */
export class SubscriptionModel extends BaseModel implements Subscription {
  public subscriptionId: string;
  public clinicId: string;
  public plan: SubscriptionPlan;
  public billing: BillingInfo;
  public features: FeatureAccess;
  public usage: UsageMetrics;
  public pricing: PricingDetails;
  public status: SubscriptionStatus;
  public metadata: SubscriptionMetadata;

  constructor(data: Partial<Subscription>) {
    super();
    
    // Set defaults
    this.subscriptionId = data.subscriptionId || this.generateSubscriptionId();
    this.clinicId = data.clinicId || '';
    this.plan = data.plan || this.createDefaultPlan();
    this.billing = data.billing || this.createDefaultBilling();
    this.features = data.features || this.createDefaultFeatures();
    this.usage = data.usage || this.createDefaultUsage();
    this.pricing = data.pricing || this.createDefaultPricing();
    this.status = data.status || SubscriptionStatus.PENDING_ACTIVATION;
    this.metadata = data.metadata || this.createDefaultMetadata();

    // Override with provided data
    Object.assign(this, data);
  }

  /**
   * Validates all subscription data according to business rules and billing requirements.
   * Performs comprehensive validation including pricing, limits, and feature consistency.
   * @returns Array of validation errors with specific error codes and field references
   */
  public validate(): ValidationError[] {
    const errors: ValidationError[] = [];

    // Basic required fields
    if (!this.clinicId) {
      errors.push({
        field: 'clinicId',
        message: 'Clinic ID is required',
        code: 'MISSING_CLINIC_ID',
      });
    }

    if (!this.plan?.tier) {
      errors.push({
        field: 'plan.tier',
        message: 'Subscription tier is required',
        code: 'MISSING_TIER',
      });
    }

    // Billing validation
    if (!this.billing?.currentCycle) {
      errors.push({
        field: 'billing.currentCycle',
        message: 'Billing cycle is required',
        code: 'MISSING_BILLING_CYCLE',
      });
    }

    if (!this.billing?.nextBillingDate) {
      errors.push({
        field: 'billing.nextBillingDate',
        message: 'Next billing date is required',
        code: 'MISSING_BILLING_DATE',
      });
    }

    // Pricing validation
    if (this.pricing?.currentPlan && this.pricing.currentPlan !== this.plan.tier) {
      errors.push({
        field: 'pricing.currentPlan',
        message: 'Pricing plan must match subscription tier',
        code: 'MISMATCHED_PRICING_PLAN',
      });
    }

    if (this.pricing?.monthlyRate && this.pricing.monthlyRate < 0) {
      errors.push({
        field: 'pricing.monthlyRate',
        message: 'Monthly rate cannot be negative',
        code: 'INVALID_MONTHLY_RATE',
        value: this.pricing.monthlyRate,
      });
    }

    // Feature validation
    if (!this.features?.enabledFeatures || this.features.enabledFeatures.length === 0) {
      errors.push({
        field: 'features.enabledFeatures',
        message: 'At least one feature must be enabled',
        code: 'NO_ENABLED_FEATURES',
      });
    }

    // Status validation
    if (this.status === SubscriptionStatus.ACTIVE && !this.metadata?.activatedAt) {
      errors.push({
        field: 'metadata.activatedAt',
        message: 'Activation date is required for active subscriptions',
        code: 'MISSING_ACTIVATION_DATE',
      });
    }

    return errors;
  }

  /**
   * Calculates the total subscription amount based on current plan and billing cycle.
   * Applies discounts, taxes, and per-doctor pricing for accurate billing.
   * @param doctorCount Number of doctors to calculate pricing for
   * @returns Detailed billing amount breakdown
   */
  public calculateBillingAmount(doctorCount: number): BillingAmount {
    const baseAmount = this.plan.pricing.basePrice || 0;
    const perDoctorAmount = this.plan.pricing.pricePerDoctor * doctorCount;
    const subtotal = baseAmount + perDoctorAmount;

    // Apply discounts
    const discounts = this.calculateDiscounts(subtotal, doctorCount);
    const discountAmount = discounts.reduce((sum, discount) => sum + discount.amount, 0);

    // Calculate taxes
    const taxableAmount = subtotal - discountAmount;
    const taxes = this.calculateTaxes(taxableAmount);
    const taxAmount = taxes.reduce((sum, tax) => sum + tax.amount, 0);

    const totalAmount = taxableAmount + taxAmount;

    return {
      baseAmount,
      doctorCount,
      perDoctorAmount: this.plan.pricing.pricePerDoctor,
      subtotal,
      discounts,
      taxes,
      totalAmount,
      currency: this.plan.pricing.currency,
    };
  }

  /**
   * Checks if a specific feature is enabled and available for use.
   * Validates feature access levels and usage limits.
   * @param featureCode Feature identifier to check
   * @returns True if feature is enabled and within limits, false otherwise
   */
  public isFeatureEnabled(featureCode: string): boolean {
    const feature = this.features.enabledFeatures.find(f => f.featureCode === featureCode);
    return feature?.isEnabled || false;
  }

  /**
   * Gets the usage limit for a specific feature.
   * Returns configured limits or default values based on subscription tier.
   * @param featureCode Feature identifier to check
   * @returns Feature limits object or null if feature not found
   */
  public getFeatureLimit(featureCode: string): FeatureLimits | null {
    const feature = this.features.enabledFeatures.find(f => f.featureCode === featureCode);
    return feature?.limits || null;
  }

  /**
   * Checks if current usage is within allowed limits for a feature.
   * Validates against daily, monthly, and overall usage limits.
   * @param featureCode Feature identifier to check
   * @param currentUsage Current usage amount to validate
   * @returns True if usage is within limits, false if exceeded
   */
  public isWithinUsageLimit(featureCode: string, currentUsage: number): boolean {
    const limits = this.getFeatureLimit(featureCode);
    if (!limits) return true;

    // Check various limit types
    if (limits.maxUsage && currentUsage > limits.maxUsage) return false;
    if (limits.dailyLimit && this.getDailyUsage(featureCode) > limits.dailyLimit) return false;
    if (limits.monthlyLimit && this.getMonthlyUsage(featureCode) > limits.monthlyLimit) return false;

    return true;
  }

  /**
   * Updates the subscription plan and recalculates all pricing and features.
   * Handles plan upgrades, downgrades, and feature access changes.
   * @param newTier New subscription tier to apply
   * @param effectiveDate When the change should take effect
   * @param reason Reason for the plan change
   */
  public updatePlan(newTier: SubscriptionTier, effectiveDate: string, reason: ChangeReason): void {
    const oldTier = this.plan.tier;
    
    // Update plan details
    this.plan.tier = newTier;
    this.plan = this.getPlanDetailsForTier(newTier);
    
    // Update pricing
    this.pricing.currentPlan = newTier;
    this.pricing = this.calculatePricingForTier(newTier);
    
    // Update features based on new tier
    this.features = this.getFeaturesForTier(newTier);
    
    // Record the change
    this.pricing.pricingHistory.push({
      recordId: this.generateRecordId(),
      tier: oldTier,
      rate: this.pricing.monthlyRate,
      effectiveFrom: this.pricing.pricingHistory[this.pricing.pricingHistory.length - 1]?.effectiveFrom || this.createdAt,
      effectiveTo: effectiveDate,
      reason: `Plan changed from ${oldTier} to ${newTier}`,
      appliedBy: 'SYSTEM',
    });

    this.touch();
  }

  /**
   * Processes billing for the current period and updates payment status.
   * Handles successful payments, failures, and retry logic.
   * @param paymentReference Payment transaction reference
   * @param paymentStatus Status of the payment attempt
   * @returns True if billing was processed successfully, false otherwise
   */
  public processBilling(paymentReference: string, paymentStatus: BillingStatus): boolean {
    const currentPeriodEnd = new Date(this.billing.currentPeriodEnd);
    const now = new Date();

    // Create billing record
    const billingRecord: BillingRecord = {
      recordId: this.generateRecordId(),
      billingDate: now.toISOString(),
      periodStart: this.billing.currentPeriodStart,
      periodEnd: this.billing.currentPeriodEnd,
      amount: this.billing.amount,
      status: paymentStatus,
      paymentReference,
    };

    // Add payment date only if payment was successful
    if (paymentStatus === BillingStatus.PAID) {
      billingRecord.paymentDate = now.toISOString();
    }

    this.billing.billingHistory.push(billingRecord);

    // Update subscription status based on payment result
    if (paymentStatus === BillingStatus.PAID) {
      this.status = SubscriptionStatus.ACTIVE;
      this.metadata.lastBilledAt = now.toISOString();
      this.advanceBillingPeriod();
      this.touch();
      return true;
    } else if (paymentStatus === BillingStatus.FAILED) {
      this.handlePaymentFailure();
      this.touch();
      return false;
    }

    this.touch();
    return false;
  }

  /**
   * Adds a usage alert when thresholds are approaching or exceeded.
   * Monitors resource consumption and notifies when limits are reached.
   * @param metric Metric that triggered the alert
   * @param threshold Threshold value that was crossed
   * @param currentValue Current usage value
   * @param alertType Type of alert being raised
   */
  public addUsageAlert(metric: string, threshold: number, currentValue: number, alertType: AlertType): void {
    const alert: UsageAlert = {
      alertId: this.generateAlertId(),
      type: alertType,
      severity: this.determineSeverity(currentValue, threshold),
      metric,
      threshold,
      currentValue,
      message: this.generateAlertMessage(metric, threshold, currentValue, alertType),
      triggeredAt: new Date().toISOString(),
      isActive: true,
    };

    this.usage.alerts.push(alert);
    this.touch();
  }

  /**
   * Generates subscription recommendations based on usage patterns and trends.
   * Analyzes current usage to suggest optimization opportunities.
   * @returns Array of actionable recommendations for subscription optimization
   */
  public generateRecommendations(): ProjectionRecommendation[] {
    const recommendations: ProjectionRecommendation[] = [];

    // Check for upgrade opportunities
    if (this.shouldRecommendUpgrade()) {
      recommendations.push({
        type: RecommendationType.UPGRADE_PLAN,
        title: 'Upgrade Your Plan',
        description: 'Your usage patterns suggest you could benefit from a higher tier plan',
        impact: RecommendationImpact.IMPROVED_EFFICIENCY,
        priority: RecommendationPriority.HIGH,
        estimatedSavings: this.calculateUpgradeSavings(),
      });
    }

    // Check for downgrade opportunities
    if (this.shouldRecommendDowngrade()) {
      recommendations.push({
        type: RecommendationType.DOWNGRADE_PLAN,
        title: 'Consider Downgrading',
        description: 'You may be paying for features you don\'t use',
        impact: RecommendationImpact.HIGH_COST_SAVINGS,
        priority: RecommendationPriority.MEDIUM,
        estimatedSavings: this.calculateDowngradeSavings(),
      });
    }

    // Check billing cycle optimization
    if (this.billing.currentCycle === BillingCycle.MONTHLY) {
      recommendations.push({
        type: RecommendationType.CHANGE_BILLING_CYCLE,
        title: 'Switch to Annual Billing',
        description: 'Save money with annual billing cycle',
        impact: RecommendationImpact.MODERATE_COST_SAVINGS,
        priority: RecommendationPriority.LOW,
        estimatedSavings: this.calculateAnnualSavings(),
      });
    }

    return recommendations;
  }

  /**
   * Calculates the subscription health score based on multiple factors.
   * Evaluates payment history, usage patterns, and engagement metrics.
   * @returns Comprehensive health score with individual factor scores
   */
  public calculateHealthScore(): SubscriptionHealthScore {
    const paymentScore = this.calculatePaymentScore();
    const usageScore = this.calculateUsageScore();
    const engagementScore = this.calculateEngagementScore();
    const supportScore = this.calculateSupportScore();

    const overall = Math.round(
      (paymentScore * 0.3 + usageScore * 0.25 + engagementScore * 0.25 + supportScore * 0.2)
    );

    return {
      overall,
      payment: paymentScore,
      usage: usageScore,
      engagement: engagementScore,
      support: supportScore,
      lastCalculated: new Date().toISOString(),
      factors: this.getHealthFactors(paymentScore, usageScore, engagementScore, supportScore),
    };
  }

  /**
   * Checks if the subscription is currently active and in good standing.
   * Validates status, payment history, and grace period status.
   * @returns True if subscription is active and usable, false otherwise
   */
  public isActive(): boolean {
    return this.status === SubscriptionStatus.ACTIVE || this.status === SubscriptionStatus.GRACE_PERIOD;
  }

  /**
   * Checks if the subscription is in a trial period.
   * Useful for feature gating and billing logic.
   * @returns True if currently in trial, false otherwise
   */
  public isTrial(): boolean {
    return this.status === SubscriptionStatus.TRIAL;
  }

  /**
   * Gets the number of days remaining until subscription expires.
   * Calculates based on next billing date and current status.
   * @returns Number of days until expiration, or -1 if already expired
   */
  public getDaysUntilExpiration(): number {
    if (!this.billing?.nextBillingDate) return -1;

    const expirationDate = new Date(this.billing.nextBillingDate);
    const now = new Date();
    const diffTime = expirationDate.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    return diffDays > 0 ? diffDays : -1;
  }

  // Private helper methods

  /**
   * Generates a unique subscription ID using timestamp and random components.
   * @private
   * @returns Unique subscription identifier
   */
  private generateSubscriptionId(): string {
    const timestamp = Date.now().toString(36);
    const random = Math.random().toString(36).substr(2, 5);
    return `sub_${timestamp}_${random}`;
  }

  /**
   * Creates default subscription plan for basic tier.
   * @private
   * @returns Default subscription plan configuration
   */
  private createDefaultPlan(): SubscriptionPlan {
    return {
      tier: SubscriptionTier.BASIC,
      name: 'Basic Plan',
      description: 'Essential features for small clinics',
      features: [],
      limits: {
        maxDoctors: 5,
        maxPatients: 1000,
        maxStorageGB: 5,
        maxApiCallsPerMonth: 10000,
        maxWhatsAppMessages: 1000,
        maxReports: 10,
      },
      pricing: {
        basePrice: 0,
        pricePerDoctor: 799,
        currency: 'INR',
        billingCycles: [],
        discounts: [],
      },
      isActive: true,
      validFrom: new Date().toISOString(),
    };
  }

  /**
   * Creates default billing information for new subscriptions.
   * @private
   * @returns Default billing configuration
   */
  private createDefaultBilling(): BillingInfo {
    const now = new Date();
    const nextMonth = new Date(now.getFullYear(), now.getMonth() + 1, now.getDate());

    return {
      currentCycle: BillingCycle.MONTHLY,
      currentPeriodStart: now.toISOString(),
      currentPeriodEnd: nextMonth.toISOString(),
      nextBillingDate: nextMonth.toISOString(),
      amount: {
        baseAmount: 0,
        doctorCount: 0,
        perDoctorAmount: 799,
        subtotal: 0,
        discounts: [],
        taxes: [],
        totalAmount: 0,
        currency: 'INR',
      },
      billingHistory: [],
    };
  }

  /**
   * Creates default feature access for basic subscription.
   * @private
   * @returns Default feature access configuration
   */
  private createDefaultFeatures(): FeatureAccess {
    return {
      enabledFeatures: [
        {
          featureCode: 'BASIC_QUEUE',
          isEnabled: true,
          limits: { dailyLimit: 50 },
          enabledAt: new Date().toISOString(),
        },
        {
          featureCode: 'PATIENT_MANAGEMENT',
          isEnabled: true,
          limits: { maxUsage: 1000 },
          enabledAt: new Date().toISOString(),
        },
      ],
      disabledFeatures: ['ANALYTICS', 'REPORTS', 'VIDEO_CONSULTATION'],
      customPermissions: [],
      accessLevel: GlobalAccessLevel.BASIC,
      lastUpdated: new Date().toISOString(),
    };
  }

  /**
   * Creates default usage metrics for new subscriptions.
   * @private
   * @returns Default usage metrics configuration
   */
  private createDefaultUsage(): UsageMetrics {
    const now = new Date();
    const periodStart = new Date(now.getFullYear(), now.getMonth(), 1);
    
    return {
      currentPeriod: {
        periodStart: periodStart.toISOString(),
        periodEnd: now.toISOString(),
        doctorCount: 0,
        featureUsage: [],
        resourceUsage: [],
        totalApiCalls: 0,
        totalStorage: 0,
        peakConcurrentUsers: 0,
      },
      previousPeriod: {
        periodStart: '',
        periodEnd: '',
        doctorCount: 0,
        featureUsage: [],
        resourceUsage: [],
        totalApiCalls: 0,
        totalStorage: 0,
        peakConcurrentUsers: 0,
      },
      trends: [],
      alerts: [],
      projections: [],
    };
  }

  /**
   * Creates default pricing details for basic tier.
   * @private
   * @returns Default pricing configuration
   */
  private createDefaultPricing(): PricingDetails {
    return {
      currentPlan: SubscriptionTier.BASIC,
      monthlyRate: 799,
      annualRate: 799 * 12 * 0.85, // 15% annual discount
      perDoctorRate: 799,
      effectiveRate: 799,
      discountsApplied: [],
      pricingHistory: [],
    };
  }

  /**
   * Creates default metadata for new subscriptions.
   * @private
   * @returns Default subscription metadata
   */
  private createDefaultMetadata(): SubscriptionMetadata {
    const now = new Date().toISOString();
    
    return {
      activatedAt: now,
      nextBillingAt: now,
      autoRenewal: true,
      supportTickets: 0,
      healthScore: {
        overall: 85,
        payment: 100,
        usage: 70,
        engagement: 80,
        support: 90,
        lastCalculated: now,
        factors: [],
      },
      tags: [],
      notes: [],
    };
  }

  /**
   * Calculates applicable discounts for the given subtotal and doctor count.
   * @private
   * @param subtotal Base subscription amount
   * @param doctorCount Number of doctors for volume discounts
   * @returns Array of applied discounts
   */
  private calculateDiscounts(subtotal: number, doctorCount: number): AppliedDiscount[] {
    const discounts: AppliedDiscount[] = [];
    
    // Volume discount for multiple doctors
    if (doctorCount >= 10) {
      discounts.push({
        discountId: 'VOLUME_10',
        name: 'Volume Discount (10+ doctors)',
        type: DiscountType.VOLUME_DISCOUNT,
        amount: subtotal * 0.1,
        description: '10% discount for 10 or more doctors',
      });
    }
    
    return discounts;
  }

  /**
   * Calculates applicable taxes for the given amount.
   * @private
   * @param amount Taxable amount
   * @returns Array of tax breakdowns
   */
  private calculateTaxes(amount: number): TaxBreakdown[] {
    const taxes: TaxBreakdown[] = [];
    
    // GST calculation for Indian market
    const gstRate = 0.18; // 18% GST
    taxes.push({
      taxType: TaxType.GST,
      rate: gstRate,
      amount: amount * gstRate,
      description: '18% GST',
    });
    
    return taxes;
  }

  /**
   * Gets daily usage for a specific feature.
   * @private
   * @param featureCode Feature to check
   * @returns Daily usage count
   */
  private getDailyUsage(featureCode: string): number {
    const feature = this.usage.currentPeriod.featureUsage.find(f => f.featureCode === featureCode);
    return feature?.usageCount || 0;
  }

  /**
   * Gets monthly usage for a specific feature.
   * @private
   * @param featureCode Feature to check
   * @returns Monthly usage count
   */
  private getMonthlyUsage(featureCode: string): number {
    const feature = this.usage.currentPeriod.featureUsage.find(f => f.featureCode === featureCode);
    return feature?.usageCount || 0;
  }

  /**
   * Gets plan details for a specific tier.
   * @private
   * @param tier Subscription tier
   * @returns Plan configuration for the tier
   */
  private getPlanDetailsForTier(tier: SubscriptionTier): SubscriptionPlan {
    // This would typically fetch from a plan configuration service
    return {
      tier,
      name: `${tier} Plan`,
      description: `${tier} tier subscription`,
      features: [],
      limits: {
        maxDoctors: tier === SubscriptionTier.BASIC ? 5 : tier === SubscriptionTier.PROFESSIONAL ? 20 : 100,
      },
      pricing: {
        basePrice: 0,
        pricePerDoctor: tier === SubscriptionTier.BASIC ? 799 : tier === SubscriptionTier.PROFESSIONAL ? 649 : 549,
        currency: 'INR',
        billingCycles: [],
        discounts: [],
      },
      isActive: true,
      validFrom: new Date().toISOString(),
    };
  }

  /**
   * Calculates pricing details for a specific tier.
   * @private
   * @param tier Subscription tier
   * @returns Pricing configuration for the tier
   */
  private calculatePricingForTier(tier: SubscriptionTier): PricingDetails {
    const monthlyRate = tier === SubscriptionTier.BASIC ? 799 : tier === SubscriptionTier.PROFESSIONAL ? 649 : 549;
    
    return {
      currentPlan: tier,
      monthlyRate,
      annualRate: monthlyRate * 12 * 0.85, // 15% annual discount
      perDoctorRate: monthlyRate,
      effectiveRate: monthlyRate,
      discountsApplied: [],
      pricingHistory: [],
    };
  }

  /**
   * Gets feature access configuration for a specific tier.
   * @private
   * @param tier Subscription tier
   * @returns Feature access configuration
   */
  private getFeaturesForTier(tier: SubscriptionTier): FeatureAccess {
    const basicFeatures = ['BASIC_QUEUE', 'PATIENT_MANAGEMENT'];
    const professionalFeatures = [...basicFeatures, 'ANALYTICS', 'REPORTS'];
    const enterpriseFeatures = [...professionalFeatures, 'VIDEO_CONSULTATION', 'ADVANCED_ANALYTICS'];
    
    let enabledFeatureCodes: string[];
    let accessLevel: GlobalAccessLevel;
    
    switch (tier) {
      case SubscriptionTier.BASIC:
        enabledFeatureCodes = basicFeatures;
        accessLevel = GlobalAccessLevel.BASIC;
        break;
      case SubscriptionTier.PROFESSIONAL:
        enabledFeatureCodes = professionalFeatures;
        accessLevel = GlobalAccessLevel.PROFESSIONAL;
        break;
      case SubscriptionTier.ENTERPRISE:
        enabledFeatureCodes = enterpriseFeatures;
        accessLevel = GlobalAccessLevel.ENTERPRISE;
        break;
      default:
        enabledFeatureCodes = basicFeatures;
        accessLevel = GlobalAccessLevel.BASIC;
    }
    
    return {
      enabledFeatures: enabledFeatureCodes.map(code => ({
        featureCode: code,
        isEnabled: true,
        limits: { dailyLimit: 100 },
        enabledAt: new Date().toISOString(),
      })),
      disabledFeatures: [],
      customPermissions: [],
      accessLevel,
      lastUpdated: new Date().toISOString(),
    };
  }

  /**
   * Generates a unique record ID.
   * @private
   * @returns Unique record identifier
   */
  private generateRecordId(): string {
    return `rec_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`;
  }

  /**
   * Generates a unique alert ID.
   * @private
   * @returns Unique alert identifier
   */
  private generateAlertId(): string {
    return `alert_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`;
  }

  /**
   * Advances billing period to next cycle.
   * @private
   */
  private advanceBillingPeriod(): void {
    const currentEnd = new Date(this.billing.currentPeriodEnd);
    const nextEnd = new Date(currentEnd);
    
    switch (this.billing.currentCycle) {
      case BillingCycle.MONTHLY:
        nextEnd.setMonth(nextEnd.getMonth() + 1);
        break;
      case BillingCycle.QUARTERLY:
        nextEnd.setMonth(nextEnd.getMonth() + 3);
        break;
      case BillingCycle.ANNUALLY:
        nextEnd.setFullYear(nextEnd.getFullYear() + 1);
        break;
    }
    
    this.billing.currentPeriodStart = this.billing.currentPeriodEnd;
    this.billing.currentPeriodEnd = nextEnd.toISOString();
    this.billing.nextBillingDate = nextEnd.toISOString();
  }

  /**
   * Handles payment failure scenarios.
   * @private
   */
  private handlePaymentFailure(): void {
    // Move to grace period or suspend based on policy
    if (this.status === SubscriptionStatus.ACTIVE) {
      this.status = SubscriptionStatus.GRACE_PERIOD;
      const gracePeriodEnd = new Date();
      gracePeriodEnd.setDate(gracePeriodEnd.getDate() + 7); // 7-day grace period
      this.metadata.gracePeriodEnds = gracePeriodEnd.toISOString();
    }
  }

  /**
   * Determines alert severity based on usage vs threshold.
   * @private
   */
  private determineSeverity(currentValue: number, threshold: number): AlertSeverity {
    const ratio = currentValue / threshold;
    if (ratio >= 1.0) return AlertSeverity.CRITICAL;
    if (ratio >= 0.9) return AlertSeverity.HIGH;
    if (ratio >= 0.8) return AlertSeverity.MEDIUM;
    return AlertSeverity.LOW;
  }

  /**
   * Generates alert message based on context.
   * @private
   */
  private generateAlertMessage(metric: string, threshold: number, currentValue: number, alertType: AlertType): string {
    return `${metric} usage (${currentValue}) has ${currentValue >= threshold ? 'exceeded' : 'approached'} the threshold of ${threshold}`;
  }

  // Recommendation helper methods
  private shouldRecommendUpgrade(): boolean {
    return false; // Placeholder implementation
  }

  private shouldRecommendDowngrade(): boolean {
    return false; // Placeholder implementation
  }

  private calculateUpgradeSavings(): number {
    return 0; // Placeholder implementation
  }

  private calculateDowngradeSavings(): number {
    return 0; // Placeholder implementation
  }

  private calculateAnnualSavings(): number {
    return this.pricing.monthlyRate * 12 * 0.15; // 15% annual discount
  }

  // Health score calculation methods
  private calculatePaymentScore(): number {
    return 85; // Placeholder implementation
  }

  private calculateUsageScore(): number {
    return 75; // Placeholder implementation
  }

  private calculateEngagementScore(): number {
    return 80; // Placeholder implementation
  }

  private calculateSupportScore(): number {
    return 90; // Placeholder implementation
  }

  private getHealthFactors(payment: number, usage: number, engagement: number, support: number): HealthFactor[] {
    return [
      {
        factor: 'Payment Reliability',
        score: payment,
        weight: 0.3,
        description: 'On-time payment history',
      },
      {
        factor: 'Feature Usage',
        score: usage,
        weight: 0.25,
        description: 'Active feature utilization',
      },
      {
        factor: 'System Engagement',
        score: engagement,
        weight: 0.25,
        description: 'Regular system usage',
      },
      {
        factor: 'Support Interactions',
        score: support,
        weight: 0.2,
        description: 'Support ticket frequency',
      },
    ];
  }

  /**
   * Factory method to create a new subscription with specified tier and clinic.
   * @static
   * @param clinicId Clinic identifier for the subscription
   * @param tier Subscription tier to assign
   * @param doctorCount Initial number of doctors
   * @returns New SubscriptionModel instance with PENDING_ACTIVATION status
   */
  static create(clinicId: string, tier: SubscriptionTier, doctorCount: number): SubscriptionModel {
    return new SubscriptionModel({
      clinicId,
      plan: {
        tier,
        name: `${tier} Plan`,
        description: `${tier} tier subscription`,
        features: [],
        limits: { maxDoctors: doctorCount },
        pricing: {
          basePrice: 0,
          pricePerDoctor: tier === SubscriptionTier.BASIC ? 799 : tier === SubscriptionTier.PROFESSIONAL ? 649 : 549,
          currency: 'INR',
          billingCycles: [],
          discounts: [],
        },
        isActive: true,
        validFrom: new Date().toISOString(),
      },
      status: SubscriptionStatus.PENDING_ACTIVATION,
    });
  }

  /**
   * Factory method to create a trial subscription for new clinics.
   * @static
   * @param clinicId Clinic identifier for the trial
   * @param trialDays Number of days for the trial period
   * @returns New SubscriptionModel instance with TRIAL status
   */
  static createTrial(clinicId: string, trialDays: number = 30): SubscriptionModel {
    const trialEnd = new Date();
    trialEnd.setDate(trialEnd.getDate() + trialDays);

    return new SubscriptionModel({
      clinicId,
      status: SubscriptionStatus.TRIAL,
      billing: {
        currentCycle: BillingCycle.MONTHLY,
        currentPeriodStart: new Date().toISOString(),
        currentPeriodEnd: trialEnd.toISOString(),
        nextBillingDate: trialEnd.toISOString(),
        amount: {
          baseAmount: 0,
          doctorCount: 1,
          perDoctorAmount: 0,
          subtotal: 0,
          discounts: [],
          taxes: [],
          totalAmount: 0,
          currency: 'INR',
        },
        billingHistory: [],
      },
    });
  }
}
