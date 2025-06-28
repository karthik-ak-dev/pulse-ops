# PulseOps - Technical Implementation Guide

**Version 1.0 | Last Updated: January 2025**

---

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Data Model & Entity Hierarchy](#2-data-model--entity-hierarchy)
3. [User Access Control](#3-user-access-control)
4. [Subscription & Pricing Model](#4-subscription--pricing-model)
5. [Backend Architecture (MVC)](#5-backend-architecture-mvc)
6. [Complete API Documentation](#6-complete-api-documentation)
7. [Database Schema](#7-database-schema)
8. [Core Use Cases](#8-core-use-cases)
9. [Implementation Phases](#9-implementation-phases)
10. [Production-Ready Development Guidelines](#10-production-ready-development-guidelines)
11. [Reusable LLM Implementation Prompt](#11-reusable-llm-implementation-prompt)

---

## 1. System Architecture

### 1.1 MVP System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                    PULSEOPS MVP ARCHITECTURE                    │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   WhatsApp      │    │   API Gateway    │    │   Lambda        │    │   EventBridge   │
│   Business API  │◄──►│   (REST API)     │◄──►│   Functions     │◄──►│   (Real-time    │
│                 │    │                  │    │                 │    │    Triggers)    │
│ • OTP Messages  │    │ • Authentication │    │ • Express App   │    │ • Queue Updates │
│ • Notifications │    │ • Rate Limiting  │    │ • MVC Pattern   │    │ • Token Events  │
│ • Webhooks      │    │ • CORS           │    │ • JWT Auth      │    │ • Notifications │
│ • Payment Links │    │ • Request/Response│   │ • Role-based    │    │ • Analytics     │
└─────────────────┘    └──────────────────┘    │   Access Control│    └─────────────────┘
                                               └─────────────────┘
                                                        │
                                                        ▼
┌───────────────────────────────────────────────────────────────────────────────--------──-┐
│                              DYNAMODB MULTI-TABLE DESIGN                                 │
├─────────────────┬─────────────────┬─────────────────┬─────────────────┬────────--------─-┤
│   Clinics       │     Users       │    Doctors      │   Patients      │  Queues          │
│   Table         │     Table       │     Table       │     Table       │  Table           │
│                 │                 │                 │                 │                  │
│ • clinicId (PK) │ • clinicId (PK) │ • clinicId (PK) │ • patientId (PK)│ • doctorId (PK)  │
│ • name, address │ • userId (SK)   │ • doctorId (SK) │ • phone, name   │ • date (SK)      │
│ • subscription  │ • role, status  │ • specialization│ • demographics  │ • status         │
│ • billing       │ • permissions   │ • schedule      │ • medical info  │ • tokens         │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┴─────────---------┘
                                                        │
                                                        ▼
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┬─────────----------┤
│   Tokens        │   Associations  │   Visit Records │ Subscriptions   │  OTP              │
│   Table         │     Table       │     Table       │     Table       │ Requests          │
│                 │                 │                 │                 │  Table            │
│ • queueId (PK)  │ • doctorId (PK) │ • doctorId (PK) │ • clinicId (PK) │ • requestId (PK)  │
│ • tokenId (SK)  │ • patientId (SK)│ • visitId (SK)  │ • plan, billing │ • whatsapp, otp   │
│ • patient info  │ • relationship  │ • diagnosis     │ • limits        │ • status          │
│ • status, time  │ • preferences   │ • prescription  │ • features      │ • expiration      │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┴────────----------─┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              DATA FLOW & ISOLATION                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  CLINIC A                    CLINIC B                    CLINIC C               │
│  ┌─────────────┐            ┌─────────────┐            ┌─────────────┐          │
│  │ Admin User  │            │ Admin User  │            │ Admin User  │          │
│  │ (Full Access)│           │ (Full Access)│           │ (Full Access)│         │
│  └─────────────┘            └─────────────┘            └─────────────┘          │
│         │                           │                           │               │
│         ▼                           ▼                           ▼               │
│  ┌─────────────┐            ┌─────────────--┐            ┌─────────────-┐       │
│  │ Doctor A    │            │ Doctor X      │            │ Doctor P     │       │
│  │ (Own Patients)│          │ (Own Patients)│            |(Own Patients)│       │
│  └─────────────┘            └─────────────--┘            └─────────────-┘       │
│         │                           │                           │               │
│         ▼                           ▼                           ▼               │
│  ┌─────────────┐            ┌─────────────┐            ┌─────────────┐          │
│  │ Patients    │            │ Patients    │            │ Patients    │          │
│  │ (Isolated)  │            │ (Isolated)  │            │ (Isolated)  │          │
│  └─────────────┘            └─────────────┘            └─────────────┘          │
│                                                                                 │
│  ❌ NO CROSS-CLINIC DATA ACCESS  ❌ NO SHARED PATIENT RECORDS                    │
│  ✅ COMPLETE DATA ISOLATION      ✅ PRIVATE DOCTOR-PATIENT RELATIONSHIPS         │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              KEY FEATURES & FLOWS                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  🔐 AUTHENTICATION FLOW:                                                        │
│  WhatsApp Number → OTP Verification → JWT Token → Role-based Access             │
│                                                                                 │
│  📋 QUEUE MANAGEMENT:                                                           │
│  Doctor Login → Start Queue → Call Tokens → Pause/Resume → Close Queue          │
│                                                                                 │
│  👥 PATIENT FLOW:                                                               │
│  WhatsApp Booking → Token Creation → Payment → Visit → Medical Records          │
│                                                                                 │
│  📊 REAL-TIME UPDATES:                                                          │
│  Queue Changes → EventBridge → SSE → Live Dashboard Updates                     │
│                                                                                 │
│  💰 SUBSCRIPTION MODEL:                                                         │
│  Per-Doctor Pricing → Monthly Billing → Feature Access Control                  │
│                                                                                 │
│  🔒 PRIVACY & SECURITY:                                                         │
│  Multi-tenant Isolation → Role-based Permissions → Audit Logging                │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              TECHNICAL STACK                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Backend: Node.js 18+ | Express.js | TypeScript | JWT Authentication            │
│  Database: DynamoDB Multi-Table | Global Secondary Indexes | Local Indexes      │
│  Cloud: AWS Lambda | API Gateway | EventBridge | CloudWatch | Parameter Store   │
│  Integration: WhatsApp Business API | UPI Payment Gateway | SMS Gateway         │
│  Security: Role-based Access Control | Data Isolation | Audit Logging           │
│  Monitoring: Structured Logging | Performance Metrics | Error Tracking          │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Technology Stack

**Backend:**

- **Runtime**: Node.js 18+ with TypeScript
- **Framework**: Express.js with Zod validation
- **Database**: DynamoDB multi-table design
- **Authentication**: JWT with role-based access
- **Architecture**: MVC pattern with dependency injection

---

## 2. Data Model & Entity Hierarchy

### 2.1 Entity Relationship

```
Clinic (1)
├── Subscription (1:1)
├── Users (1:N)
│   ├── Admin Users (can see everything within clinic)
│   └── Doctor Users (restricted to own patients)
├── Doctors (1:N)
│   ├── Daily Queues (1:N)
│   │   └── Tokens (1:N)
│   └── Doctor-Patient Associations (1:N)
│       └── Visit Records (1:N)
│           ├── Diagnosis Notes
│           ├── Prescriptions
│           └── Treatment History
├── OTP Requests (1:N)
│   ├── Registration OTPs
│   ├── Login OTPs
│   └── Password Reset OTPs
└── Patients (Global, identified by phone)
    └── Cross-Clinic Associations (N:N)
```

### 2.2 Core Entities

#### Clinic

- **Purpose**: Top-level organization
- **Subscription**: Paid at clinic level
- **Users**: Admins and doctors belong to clinic
- **Isolation**: Complete data separation between clinics
- **Patient Access**: Only within clinic boundaries

#### Doctor

- **Purpose**: Individual practitioners within clinic
- **Queue**: Each doctor has separate daily queues
- **Patient Associations**: Private doctor-patient relationships
- **Isolation**: Doctor A cannot see Doctor B's patients or notes
- **Access**: Only assigned clinic admins can view doctor's patient data

#### Patient

- **Purpose**: Global patient record identified by phone number
- **Scope**: Can visit multiple doctors across multiple clinics
- **Isolation**: Patient data isolated per doctor-clinic combination
- **Privacy**: Visit records private to specific doctor and clinic admin only

#### Doctor-Patient Association

- **Purpose**: Links doctor to patient within clinic boundaries
- **Scope**: Tracks relationship history and preferences
- **Access**: Visible only to specific doctor and clinic admin
- **Data**: Patient preferences, communication history, visit summaries

#### Visit Record

- **Purpose**: Individual consultation documentation
- **Scope**: Belongs to specific doctor-patient association
- **Content**: Diagnosis, prescription, notes, treatment plan
- **Privacy**: Accessible only by treating doctor and clinic admin
- **History**: Complete visit timeline for continuity of care

#### Queue

- **Purpose**: Daily token management per doctor
- **Scope**: One queue per doctor per day
- **Status**: Active, Paused, Emergency, Closed
- **Control**: Real-time updates via EventBridge

#### Token

- **Purpose**: Individual patient booking for specific visit
- **Association**: Links to doctor-patient relationship and visit record
- **Payment**: Handled via WhatsApp Pay
- **Status**: Pending → Confirmed → Arrived → Completed
- **Privacy**: Contains only basic info, detailed notes in visit record

#### User

- **Purpose**: System user accounts for clinic staff and doctors
- **Types**: Admin users and Doctor users with different permissions
- **Authentication**: WhatsApp-based login with OTP verification
- **Scope**: Belongs to specific clinic with role-based access
- **Isolation**: Users can only access data within their assigned clinic

#### Subscription

- **Purpose**: Clinic billing and plan management
- **Tiers**: Basic, Professional, Enterprise with different doctor limits
- **Billing**: Per-doctor pricing with monthly billing cycles
- **Features**: Feature access based on subscription tier
- **Management**: Admin controls for plan upgrades/downgrades

#### OTP Request

- **Purpose**: WhatsApp OTP management for authentication
- **Types**: Registration, Login, Password Reset OTPs
- **Security**: Rate limiting and expiration controls
- **Tracking**: Audit trail for all OTP requests
- **Validation**: Verification against stored OTP codes

---

## 3. User Access Control

### 3.1 User Types & Permissions

#### Clinic Admin

```typescript
interface AdminPermissions {
  // Full clinic access
  viewAllDoctors: true;
  manageDoctors: true;
  viewAllQueues: true;

  // Patient data access (within clinic only)
  viewAllPatientAssociations: true;
  viewAllVisitRecords: true;
  viewDoctorNotes: true;
  exportPatientData: true;

  // Financial access
  viewSubscription: true;
  managePayments: true;
  viewRevenue: true;
  downloadReports: true;

  // System access
  configureWhatsApp: true;
  manageSettings: true;
}
```

#### Doctor User

```typescript
interface DoctorPermissions {
  // Limited to own queue
  viewOwnQueue: true;
  manageOwnTokens: true;
  callNextPatient: true;
  pauseOwnQueue: true;

  // Patient data access (own patients only)
  viewOwnPatients: true;
  manageOwnPatientAssociations: true;
  addVisitNotes: true;
  addDiagnosis: true;
  addPrescription: true;
  viewOwnVisitHistory: true;

  // Restricted patient access
  viewOtherDoctorPatients: false;
  viewOtherDoctorNotes: false;
  viewCrossClinicPatientData: false;

  // No financial access
  viewSubscription: false;
  managePayments: false;
  viewRevenue: false; // except own consultation count

  // No admin access
  manageDoctors: false;
  viewOtherQueues: false;
}
```

### 3.2 JWT Token Structure

```typescript
// JWT Payload
{
  "user_id": "usr_12345",
  "clinic_id": "clinic_abc123",
  "whatsapp_number": "+919876543210",
  "doctor_id": "doc_67890", // only for doctor users
  "role": "ADMIN" | "DOCTOR",
  "permissions": [
    "view_queue", "manage_payments", "view_own_patients",
    "add_visit_notes", "view_doctor_notes", ...
  ],
  "patient_access_scope": "CLINIC_ALL" | "DOCTOR_OWN", // determines patient data access
  "exp": 1640995200,
  "iat": 1640995200,
  "iss": "pulseops-api"
}
```

---

## 4. Subscription & Pricing Model

### 4.1 Clinic Subscription Tiers

#### Basic Plan

```typescript
{
  "name": "Basic",
  "price_per_doctor": 799,
  "max_doctors": 3,
  "features": [
    "Basic dashboard",
    "WhatsApp notifications",
    "Standard support"
  ]
}
```

#### Professional Plan

```typescript
{
  "name": "Professional",
  "price_per_doctor": 649,
  "max_doctors": 10,
  "features": [
    "Advanced analytics",
    "Multi-user access",
    "Priority support",
    "Custom reports"
  ]
}
```

#### Enterprise Plan

```typescript
{
  "name": "Enterprise",
  "price_per_doctor": 549,
  "max_doctors": 50,
  "features": [
    "Unlimited features",
    "Dedicated support",
    "Custom integrations",
    "White-label options"
  ]
}
```

### 4.2 Dynamic Pricing Calculation

```typescript
function calculateSubscriptionCost(numDoctors: number): number {
  if (numDoctors <= 3) {
    return numDoctors * 799; // Basic
  } else if (numDoctors <= 10) {
    return numDoctors * 649; // Professional
  } else {
    return numDoctors * 549; // Enterprise
  }
}
```

---

## 5. Backend Architecture (MVC)

### 5.1 Complete Project Structure

```
pulse-ops-backend/
├── src/
│   ├── api/                           # Routes Layer
│   │   ├── v1/
│   │   │   ├── index.ts
│   │   │   ├── auth.ts               # Authentication routes
│   │   │   ├── clinics.ts            # Clinic management routes
│   │   │   ├── doctors.ts            # Doctor management routes
│   │   │   ├── queues.ts             # Queue management routes
│   │   │   ├── tokens.ts             # Token booking routes
│   │   │   ├── patients.ts           # Patient management routes
│   │   │   ├── patient-associations.ts # Doctor-patient association routes
│   │   │   ├── visits.ts             # Visit records and notes routes
│   │   │   ├── users.ts              # User management routes
│   │   │   ├── subscriptions.ts      # Subscription routes
│   │   │   ├── analytics.ts          # Analytics routes
│   │   │   └── webhooks.ts           # WhatsApp webhooks
│   │   ├── dependencies.ts           # Route dependencies
│   │   ├── middleware.ts             # Auth & CORS middleware
│   │   └── index.ts
│   ├── controllers/                   # Controllers Layer
│   │   ├── index.ts
│   │   ├── auth-controller.ts        # Authentication logic
│   │   ├── clinic-controller.ts      # Clinic operations
│   │   ├── doctor-controller.ts      # Doctor operations
│   │   ├── queue-controller.ts       # Queue management
│   │   ├── token-controller.ts       # Token operations
│   │   ├── patient-controller.ts     # Patient operations
│   │   ├── patient-association-controller.ts # Doctor-patient associations
│   │   ├── visit-controller.ts       # Visit records and notes
│   │   ├── user-controller.ts        # User management
│   │   ├── subscription-controller.ts # Subscription logic
│   │   ├── analytics-controller.ts   # Analytics & reports
│   │   └── webhook-controller.ts     # WhatsApp webhook handling
│   ├── services/                      # Business Logic Layer
│   │   ├── index.ts
│   │   ├── auth-service.ts           # Authentication business logic
│   │   ├── clinic-service.ts         # Clinic business logic
│   │   ├── doctor-service.ts         # Doctor business logic
│   │   ├── queue-service.ts          # Queue business logic
│   │   ├── token-service.ts          # Token business logic
│   │   ├── patient-service.ts        # Patient business logic
│   │   ├── patient-association-service.ts # Doctor-patient association logic
│   │   ├── visit-service.ts          # Visit records and medical notes
│   │   ├── user-service.ts           # User business logic
│   │   ├── subscription-service.ts   # Subscription business logic
│   │   ├── whatsapp-service.ts       # WhatsApp integration
│   │   ├── payment-service.ts        # Payment processing
│   │   ├── notification-service.ts   # Notification handling
│   │   └── analytics-service.ts      # Analytics generation
│   ├── repositories/                  # Data Access Layer
│   │   ├── index.ts
│   │   ├── base-repository.ts        # Base repository pattern
│   │   ├── clinic-repository.ts      # Clinic data operations
│   │   ├── doctor-repository.ts      # Doctor data operations
│   │   ├── queue-repository.ts       # Queue data operations
│   │   ├── token-repository.ts       # Token data operations
│   │   ├── patient-repository.ts     # Patient data operations
│   │   ├── patient-association-repository.ts # Doctor-patient associations
│   │   ├── visit-repository.ts       # Visit records and notes operations
│   │   ├── user-repository.ts        # User data operations
│   │   └── subscription-repository.ts # Subscription data operations
│   ├── models/                        # Data Models
│   │   ├── index.ts
│   │   ├── base.ts                   # Base model classes
│   │   ├── clinic.ts                 # Clinic models
│   │   ├── doctor.ts                 # Doctor models
│   │   ├── queue.ts                  # Queue models
│   │   ├── token.ts                  # Token models
│   │   ├── patient.ts                # Patient models
│   │   ├── patient-association.ts    # Doctor-patient association models
│   │   ├── visit.ts                  # Visit record and medical note models
│   │   ├── user.ts                   # User models
│   │   ├── subscription.ts           # Subscription models
│   │   ├── payment.ts                # Payment models
│   │   └── notification.ts           # Notification models
│   ├── core/                          # Core Configuration
│   │   ├── index.ts
│   │   ├── config.ts                 # Application configuration
│   │   ├── security.ts               # Security utilities
│   │   ├── exceptions.ts             # Custom exceptions
│   │   ├── constants.ts              # Application constants
│   │   └── permissions.ts            # Permission definitions
│   ├── utils/                         # Comprehensive Utility Functions (57 files)
│   │   ├── README.md                 # Detailed implementation guide
│   │   ├── index.ts                  # Exports all utility functions
│   │   ├── logger/                   # Logging infrastructure (6 files)
│   │   │   ├── index.ts              # Logger exports
│   │   │   ├── winston-config.ts     # Winston configuration
│   │   │   ├── log-formatters.ts     # Log formatting utilities
│   │   │   ├── log-context.ts        # Contextual logging helpers
│   │   │   ├── audit-logger.ts       # HIPAA compliance audit logging
│   │   │   └── performance-logger.ts # Performance & metrics logging
│   │   ├── validators/               # Input validation schemas (14 files)
│   │   │   ├── index.ts              # Validation exports
│   │   │   ├── base-schemas.ts       # Common validation patterns
│   │   │   ├── auth-schemas.ts       # Authentication APIs (8 endpoints)
│   │   │   ├── clinic-schemas.ts     # Clinic management APIs (5 endpoints)
│   │   │   ├── doctor-schemas.ts     # Doctor management APIs (6 endpoints)
│   │   │   ├── patient-schemas.ts    # Patient management APIs (4 endpoints)
│   │   │   ├── patient-association-schemas.ts # Patient association APIs (5 endpoints)
│   │   │   ├── queue-schemas.ts      # Queue management APIs (8 endpoints)
│   │   │   ├── token-schemas.ts      # Token management APIs (6 endpoints)
│   │   │   ├── visit-schemas.ts      # Visit record APIs (7 endpoints)
│   │   │   ├── analytics-schemas.ts  # Analytics & reporting APIs (5 endpoints)
│   │   │   ├── whatsapp-schemas.ts   # WhatsApp integration APIs (4 endpoints)
│   │   │   ├── medical-schemas.ts    # Medical data validation (ICD codes, prescriptions)
│   │   │   └── validation-helpers.ts # Custom validation utilities
│   │   ├── formatters/               # Data formatting utilities (10 files)
│   │   │   ├── index.ts              # Formatter exports
│   │   │   ├── api-response-formatters.ts # Standard API response formatting
│   │   │   ├── phone-formatter.ts    # Phone number formatting
│   │   │   ├── date-formatter.ts     # Date & time formatting
│   │   │   ├── currency-formatter.ts # Currency & payment formatting
│   │   │   ├── medical-formatter.ts  # Medical data formatting
│   │   │   ├── analytics-formatter.ts # Analytics & report formatting
│   │   │   ├── whatsapp-formatter.ts # WhatsApp message formatting
│   │   │   ├── privacy-formatter.ts  # Data privacy & masking
│   │   │   └── queue-formatter.ts    # Queue status & token formatting
│   │   ├── helpers/                  # Common utility functions (16 files)
│   │   │   ├── index.ts              # Helper exports
│   │   │   ├── security-helpers.ts   # Encryption & security
│   │   │   ├── data-helpers.ts       # Data manipulation
│   │   │   ├── id-generators.ts      # ID generation utilities
│   │   │   ├── auth-helpers.ts       # Authentication logic helpers
│   │   │   ├── clinic-helpers.ts     # Clinic business logic
│   │   │   ├── doctor-helpers.ts     # Doctor management helpers
│   │   │   ├── patient-helpers.ts    # Patient data helpers
│   │   │   ├── queue-helpers.ts      # Queue management logic
│   │   │   ├── token-helpers.ts      # Token booking helpers
│   │   │   ├── visit-helpers.ts      # Visit record helpers
│   │   │   ├── subscription-helpers.ts # Subscription & billing logic
│   │   │   ├── analytics-helpers.ts  # Analytics calculation helpers
│   │   │   ├── whatsapp-helpers.ts   # WhatsApp integration
│   │   │   ├── payment-helpers.ts    # Payment processing helpers
│   │   │   └── notification-helpers.ts # Notification logic
│   │   └── decorators/               # Custom decorators & middleware (9 files)
│   │       ├── index.ts              # Decorator exports
│   │       ├── auth-decorators.ts    # Authentication decorators
│   │       ├── validation-decorators.ts # Request validation decorators
│   │       ├── cache-decorators.ts   # Caching decorators
│   │       ├── audit-decorators.ts   # Audit & logging decorators
│   │       ├── role-decorators.ts    # Role-based access decorators
│   │       ├── clinic-isolation-decorators.ts # Multi-tenant isolation decorators
│   │       ├── rate-limit-decorators.ts # Rate limiting decorators
│   │       └── performance-decorators.ts # Performance monitoring decorators
│   └── app.ts                         # Express application entry
├── tests/                             # Test Suite
│   ├── index.ts
│   ├── setup.ts                      # Test configuration
│   ├── controllers/                  # Controller tests
│   ├── services/                     # Service tests
│   ├── repositories/                 # Repository tests
│   ├── api/                          # API endpoint tests
│   └── utils/                        # Utility tests
├── deployment/                        # Deployment Configuration
│   ├── lambda-handler.ts             # AWS Lambda handler
│   ├── serverless.yml                # Serverless framework config
│   ├── package.json                  # Node.js dependencies
│   └── deploy.sh                     # Deployment script
├── scripts/                           # Utility Scripts
│   ├── seed-data.ts                  # Database seeding
│   ├── migrate.ts                    # Database migrations
│   └── setup-env.ts                  # Environment setup
├── package.json                       # Node.js project config
├── tsconfig.json                      # TypeScript configuration
├── eslint.config.js                   # ESLint configuration
└── README.md                         # Technical documentation
```

### 5.2 MVC Architecture Pattern

The application follows a clean MVC (Model-View-Controller) architecture pattern:

**Routes Layer**: Handle HTTP requests, authentication, and input validation  
**Controllers Layer**: Business logic coordination and permission validation  
**Services Layer**: Core business rules and cross-cutting concerns  
**Repositories Layer**: Data access abstraction and database operations  
**Models Layer**: Data structures and entity definitions

Each layer has clear responsibilities and dependencies flow downward, ensuring separation of concerns and testability.

### 5.3 Database Schema

#### 5.3.1 DynamoDB Table Design

The system uses a multi-table DynamoDB design with the following tables:

##### 1. Clinics Table

**Table Name**: `pulseops-clinics`

**Primary Key Structure:**

- **Partition Key**: `clinicId` (String)
- **Sort Key**: None (Simple primary key)

**Global Secondary Indexes (GSI):**

- **whatsappNumber-clinicId-idx**: Partition Key: `whatsappNumber`, Sort Key: `clinicId`
- **status-clinicId-idx**: Partition Key: `status`, Sort Key: `clinicId`
- **plan-clinicId-idx**: Partition Key: `plan`, Sort Key: `clinicId`

**Local Secondary Indexes (LSI):**

- **specialization-idx**: Sort Key: `specialization`
- **billingCycle-idx**: Sort Key: `billingCycle`

**Item Structure:**

```json
{
  "clinicId": "clinic_abc123",
  "name": "City Medical Center",
  "address": "123 Main St, Mumbai",
  "phone": "+919876543210",
  "whatsappNumber": "+919876543210",
  "status": "ACTIVE",
  "subscriptionPlan": "PROFESSIONAL",
  "maxDoctors": 10,
  "currentDoctors": 3,
  "pricePerDoctor": 649,
  "totalAmount": 1947,
  "billingCycle": "MONTHLY",
  "nextBillingDate": "2025-02-15",
  "createdAt": "2025-01-15T09:00:00Z",
  "updatedAt": "2025-01-15T10:30:00Z"
}
```

##### 2. Users Table

**Table Name**: `pulseops-users`

**Primary Key Structure:**

- **Partition Key**: `clinicId` (String)
- **Sort Key**: `userId` (String)

**Global Secondary Indexes (GSI):**

- **whatsappNumber-clinicId-idx**: Partition Key: `whatsappNumber`, Sort Key: `clinicId`
- **role-clinicId-idx**: Partition Key: `role`, Sort Key: `clinicId`

**Local Secondary Indexes (LSI):**

- **status-idx**: Sort Key: `status`

**Item Structure:**

```json
{
  "clinicId": "clinic_abc123",
  "userId": "usr_12345",
  "whatsappNumber": "+919876543210",
  "name": "Dr. Admin Sharma",
  "role": "ADMIN",
  "doctorId": null,
  "status": "ACTIVE",
  "permissions": ["manage_doctors", "view_analytics", "manage_subscription"],
  "passwordHash": "$2b$12$...",
  "lastLogin": "2025-01-15T08:30:00Z",
  "createdAt": "2025-01-15T09:00:00Z",
  "updatedAt": "2025-01-15T10:30:00Z"
}
```

##### 3. Doctors Table

**Table Name**: `pulseops-doctors`

**Primary Key Structure:**

- **Partition Key**: `clinicId` (String)
- **Sort Key**: `doctorId` (String)

**Global Secondary Indexes (GSI):**

- **whatsappNumber-clinicId-idx**: Partition Key: `whatsappNumber`, Sort Key: `clinicId`
- **status-clinicId-idx**: Partition Key: `status`, Sort Key: `clinicId`

**Local Secondary Indexes (LSI):**

- **specialization-idx**: Sort Key: `specialization`

**Item Structure:**

```json
{
  "clinicId": "clinic_abc123",
  "doctorId": "doc_67890",
  "userId": "usr_67890",
  "name": "Dr. Rajesh Sharma",
  "whatsappNumber": "+919876543211",
  "specialization": "General Medicine",
  "consultationFee": 500,
  "advanceAmount": 50,
  "dailyLimit": 40,
  "consultationDuration": 15,
  "startTime": "09:00",
  "endTime": "17:00",
  "lunchBreak": "13:00-14:00",
  "status": "ACTIVE",
  "createdAt": "2025-01-15T09:00:00Z",
  "updatedAt": "2025-01-15T10:30:00Z"
}
```

##### 4. Patients Table

**Table Name**: `pulseops-patients`

**Primary Key Structure:**

- **Partition Key**: `patientId` (String)
- **Sort Key**: None (Simple primary key)

**Global Secondary Indexes (GSI):**

- **patientPhone-patientId-idx**: Partition Key: `patientPhone`, Sort Key: `patientId`
- **name-patientId-idx**: Partition Key: `name`, Sort Key: `patientId`

**Local Secondary Indexes (LSI):**

- **gender-idx**: Sort Key: `gender`

**Item Structure:**

```json
{
  "patientId": "pat_12345",
  "patientPhone": "+919876543210",
  "name": "Rajesh Kumar",
  "dateOfBirth": "1980-05-15",
  "age": 44,
  "gender": "MALE",
  "address": "123 ABC Street, Mumbai",
  "emergencyContact": "+919876543211",
  "bloodGroup": "O+",
  "allergies": ["Penicillin", "Dust"],
  "chronicConditions": ["Diabetes"],
  "currentMedications": ["Metformin"],
  "createdAt": "2024-06-10T14:30:00Z",
  "updatedAt": "2025-01-15T10:15:00Z"
}
```

##### 5. Doctor-Patient Associations Table

**Table Name**: `pulseops-associations`

**Primary Key Structure:**

- **Partition Key**: `doctorId` (String)
- **Sort Key**: `patientId` (String)

**Global Secondary Indexes (GSI):**

- **patientId-doctorId-idx**: Partition Key: `patientId`, Sort Key: `doctorId`
- **clinicId-associationDate-idx**: Partition Key: `clinicId`, Sort Key: `associationDate`

**Local Secondary Indexes (LSI):**

- **associationDate-idx**: Sort Key: `associationDate`

**Item Structure:**

```json
{
  "doctorId": "doc_67890",
  "patientId": "pat_12345",
  "associationId": "assoc_12345",
  "clinicId": "clinic_abc123",
  "patientPhone": "+919876543210",
  "patientName": "Rajesh Kumar",
  "associationDate": "2025-01-10T09:00:00Z",
  "lastVisitDate": "2025-01-15T14:30:00Z",
  "totalVisits": 3,
  "preferences": {
    "preferredTime": "MORNING",
    "communicationMethod": "WHATSAPP"
  },
  "notes": "Patient prefers afternoon appointments due to work schedule",
  "status": "ACTIVE",
  "createdAt": "2025-01-10T09:00:00Z",
  "updatedAt": "2025-01-15T11:30:00Z"
}
```

##### 6. Queues Table

**Table Name**: `pulseops-queues`

**Primary Key Structure:**

- **Partition Key**: `doctorId` (String)
- **Sort Key**: `date` (String)

**Global Secondary Indexes (GSI):**

- **clinicId-date-idx**: Partition Key: `clinicId`, Sort Key: `date`
- **status-doctorId-idx**: Partition Key: `status`, Sort Key: `doctorId`

**Local Secondary Indexes (LSI):**

- **status-idx**: Sort Key: `status`

**Item Structure:**

```json
{
  "doctorId": "doc_67890",
  "date": "2025-01-15",
  "queueId": "queue_12345",
  "clinicId": "clinic_abc123",
  "status": "ACTIVE",
  "currentToken": "TKN_001",
  "totalTokens": 25,
  "completedTokens": 8,
  "pendingTokens": 12,
  "skippedTokens": 5,
  "startTime": "2025-01-15T09:00:00Z",
  "estimatedEndTime": "2025-01-15T17:00:00Z",
  "pauseReason": null,
  "pausedAt": null,
  "resumedAt": null,
  "closedAt": null,
  "createdAt": "2025-01-15T09:00:00Z",
  "updatedAt": "2025-01-15T14:30:00Z"
}
```

##### 7. Tokens Table

**Table Name**: `pulseops-tokens`

**Primary Key Structure:**

- **Partition Key**: `queueId` (String)
- **Sort Key**: `tokenId` (String)

**Global Secondary Indexes (GSI):**

- **patientId-date-idx**: Partition Key: `patientId`, Sort Key: `date`
- **doctorId-date-idx**: Partition Key: `doctorId`, Sort Key: `date`
- **status-queueId-idx**: Partition Key: `status`, Sort Key: `queueId`

**Local Secondary Indexes (LSI):**

- **status-idx**: Sort Key: `status`

**Item Structure:**

```json
{
  "queueId": "queue_12345",
  "tokenId": "TKN_001",
  "patientId": "pat_12345",
  "doctorId": "doc_67890",
  "clinicId": "clinic_abc123",
  "patientPhone": "+919876543210",
  "patientName": "Rajesh Kumar",
  "status": "CONFIRMED",
  "tokenNumber": "001",
  "date": "2025-01-15",
  "estimatedTime": "2025-01-15T14:30:00Z",
  "actualTime": null,
  "consultationType": "GENERAL",
  "paymentStatus": "PAID",
  "amount": 500,
  "visitId": "visit_12345",
  "createdAt": "2025-01-15T09:00:00Z",
  "updatedAt": "2025-01-15T14:30:00Z"
}
```

##### 8. Visit Records Table

**Table Name**: `pulseops-visits`

**Primary Key Structure:**

- **Partition Key**: `doctorId` (String)
- **Sort Key**: `visitId` (String)

**Global Secondary Indexes (GSI):**

- **patientId-visitDate-idx**: Partition Key: `patientId`, Sort Key: `visitDate`
- **clinicId-visitDate-idx**: Partition Key: `clinicId`, Sort Key: `visitDate`

**Local Secondary Indexes (LSI):**

- **visitDate-idx**: Sort Key: `visitDate`

**Item Structure:**

```json
{
  "doctorId": "doc_67890",
  "visitId": "visit_12345",
  "patientId": "pat_12345",
  "patientPhone": "+919876543210",
  "patientName": "Rajesh Kumar",
  "clinicId": "clinic_abc123",
  "visitDate": "2025-01-15",
  "tokenId": "TKN_001",
  "status": "COMPLETED",
  "chiefComplaint": "Headache and dizziness",
  "vitalSigns": {
    "bloodPressure": "140/90",
    "pulse": "72",
    "temperature": "98.6",
    "weight": "70kg"
  },
  "examination": "General examination normal, BP elevated",
  "diagnosis": "Hypertension",
  "prescription": "Amlodipine 5mg",
  "notes": "Patient responding well to treatment",
  "privateNotes": "Patient seems anxious about work stress",
  "createdAt": "2025-01-15T14:30:00Z",
  "updatedAt": "2025-01-15T15:00:00Z"
}
```

##### 9. Subscriptions Table

**Table Name**: `pulseops-subscriptions`

**Primary Key Structure:**

- **Partition Key**: `clinicId` (String)
- **Sort Key**: `subscriptionId` (String)

**Global Secondary Indexes (GSI):**

- **status-clinicId-idx**: Partition Key: `status`, Sort Key: `clinicId`
- **plan-clinicId-idx**: Partition Key: `plan`, Sort Key: `clinicId`

**Local Secondary Indexes (LSI):**

- **billingCycle-idx**: Sort Key: `billingCycle`

**Item Structure:**

```json
{
  "clinicId": "clinic_abc123",
  "subscriptionId": "sub_12345",
  "plan": "PROFESSIONAL",
  "maxDoctors": 10,
  "currentDoctors": 3,
  "pricePerDoctor": 649,
  "totalAmount": 1947,
  "billingCycle": "MONTHLY",
  "status": "ACTIVE",
  "nextBillingDate": "2025-02-15",
  "lastPaymentDate": "2025-01-15",
  "lastPaymentAmount": 1947,
  "paymentMethod": "UPI",
  "createdAt": "2025-01-15T09:00:00Z",
  "updatedAt": "2025-01-15T10:30:00Z"
}
```

##### 10. OTP Requests Table

**Table Name**: `pulseops-otp-requests`

**Primary Key Structure:**

- **Partition Key**: `requestId` (String)
- **Sort Key**: None (Simple primary key)

**Global Secondary Indexes (GSI):**

- **whatsappNumber-requestType-idx**: Partition Key: `whatsappNumber`, Sort Key: `requestType`
- **requestType-createdAt-idx**: Partition Key: `requestType`, Sort Key: `createdAt`

**Local Secondary Indexes (LSI):**

- **status-idx**: Sort Key: `status`

**Item Structure:**

```json
{
  "requestId": "otp_req_12345",
  "whatsappNumber": "+919876543210",
  "clinicId": "clinic_abc123",
  "requestType": "LOGIN",
  "otp": "123456",
  "status": "PENDING",
  "expiresAt": "2025-01-15T10:05:00Z",
  "attempts": 0,
  "maxAttempts": 3,
  "createdAt": "2025-01-15T10:00:00Z",
  "updatedAt": "2025-01-15T10:00:00Z"
}
```

#### 5.3.2 Index Usage Patterns

**Common Query Patterns:**

1. **Clinic Management:**
   - Get clinic by ID: `clinicId = "clinic_abc123"`
   - Get clinics by status: `status-createdAt-idx: status = "ACTIVE"`
   - Get clinic by WhatsApp: `whatsappNumber-clinicId-idx: whatsappNumber = "+919876543210"`

2. **User Authentication:**
   - Get user by WhatsApp: `whatsappNumber-clinicId-idx: whatsappNumber = "+919876543210"`
   - Get users by role: `role-clinicId-idx: role = "ADMIN"`
   - Get users by status: `status-idx: status = "ACTIVE"`

3. **Doctor Operations:**
   - Get doctor by ID: `clinicId = "clinic_abc123" AND doctorId = "doc_67890"`
   - Get doctors by status: `status-clinicId-idx: status = "ACTIVE"`
   - Get doctor by WhatsApp: `whatsappNumber-clinicId-idx: whatsappNumber = "+919876543211"`

4. **Patient Management:**
   - Get patient by ID: `patientId = "pat_12345"`
   - Get patient by phone: `patientPhone-patientId-idx: patientPhone = "+919876543210"`
   - Get patients by name: `name-patientId-idx: name = "Rajesh Kumar"`

5. **Doctor-Patient Associations:**
   - Get doctor's patients: `doctorId = "doc_67890"`
   - Get patient's doctors: `patientId-doctorId-idx: patientId = "pat_12345"`
   - Get clinic associations: `clinicId-associationDate-idx: clinicId = "clinic_abc123"`

6. **Queue Management:**
   - Get doctor's queue: `doctorId = "doc_67890" AND date = "2025-01-15"`
   - Get clinic queues: `clinicId-date-idx: clinicId = "clinic_abc123"`
   - Get active queues: `status-doctorId-idx: status = "ACTIVE"`

7. **Token Operations:**
   - Get queue tokens: `queueId = "queue_12345"`
   - Get patient tokens: `patientId-date-idx: patientId = "pat_12345"`
   - Get doctor tokens: `doctorId-date-idx: doctorId = "doc_67890"`

8. **Visit Records:**
   - Get doctor's visits: `doctorId = "doc_67890"`
   - Get patient visits: `patientId-visitDate-idx: patientId = "pat_12345"`
   - Get clinic visits: `clinicId-visitDate-idx: clinicId = "clinic_abc123"`

#### 5.3.3 Benefits of Simplified Design

**✅ Advantages:**

- **Direct Attribute Access**: No need to parse composite keys
- **Simple Queries**: Straightforward DynamoDB operations
- **Easy to Understand**: Clear table structure and relationships
- **Type Safety**: Direct attribute types without string parsing
- **Better Performance**: Simpler key structures for faster queries

**Example Queries:**

```python
# Simple and direct
def get_clinic(clinic_id: str):
    response = clinics_table.get_item(Key={'clinicId': clinic_id})
    return response.get('Item')

def get_users_in_clinic(clinic_id: str):
    response = users_table.query(
        KeyConditionExpression='clinicId = :clinic_id',
        ExpressionAttributeValues={':clinic_id': clinic_id}
    )
    return response['Items']

def get_doctor_by_whatsapp(whatsapp_number: str):
    response = doctors_table.query(
        IndexName='whatsappNumber-clinicId-idx',
        KeyConditionExpression='whatsappNumber = :whatsapp',
        ExpressionAttributeValues={':whatsapp': whatsapp_number}
    )
    return response['Items']
```

---

### 5.4 WhatsApp-Based Authentication Flow

**Why WhatsApp Authentication?**

- **Unified Platform**: Clinics already use WhatsApp for patient communication
- **No Email Required**: Many small clinics don't have professional emails
- **Better Security**: OTP via WhatsApp is more secure than password-only
- **User Familiarity**: Doctors and staff are already comfortable with WhatsApp
- **Cost Effective**: No additional SMS costs, uses existing WhatsApp Business

**Authentication Process:**

```
1. Clinic Registration:
   └── Admin provides clinic details + WhatsApp number
   └── OTP sent to WhatsApp for verification
   └── Password set after OTP verification
   └── Clinic activated with admin user created

2. User Login:
   └── User enters WhatsApp number + clinic ID
   └── OTP sent to WhatsApp
   └── User enters OTP + password
   └── JWT tokens issued for session

3. Doctor User Creation:
   └── Admin creates doctor user with WhatsApp number
   └── Login credentials sent via WhatsApp message
   └── Doctor can login using WhatsApp OTP flow
```

**Security Benefits:**

- **Two-Factor Authentication**: OTP + Password
- **Device Verification**: WhatsApp number linked to specific device
- **Message Encryption**: WhatsApp's end-to-end encryption
- **Audit Trail**: All OTP requests logged with timestamps
- **Rate Limiting**: Prevents OTP spam and brute force attacks

---

## 6. Complete API Documentation

### 6.1 Authentication APIs

#### POST /api/v1/auth/clinic/register

**Purpose**: Register new clinic with admin user  
**Access**: Public  
**Usage**: Initial clinic onboarding and admin account creation

**Request:**

```json
{
  "clinicName": "City Medical Center",
  "address": "123 Main St, Mumbai",
  "whatsappNumber": "+919876543210",
  "adminName": "Dr. Admin Sharma",
  "subscriptionPlan": "PROFESSIONAL"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Clinic registered successfully. OTP sent to WhatsApp.",
  "data": {
    "clinicId": "clinic_abc123",
    "registrationId": "reg_xyz789",
    "otpExpiresIn": 300
  }
}
```

**OTP Message Template:**
"Welcome to PulseOps! Your clinic registration OTP is: 123456. Valid for 5 minutes."

#### POST /api/v1/auth/clinic/verify-registration

**Purpose**: Verify clinic registration with WhatsApp OTP  
**Access**: Public  
**Usage**: Complete clinic registration after OTP verification

**Request:**

```json
{
  "registrationId": "reg_xyz789",
  "otp": "123456",
  "password": "securePassword123"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Clinic registration completed successfully",
  "data": {
    "clinic": {
      "clinicId": "clinic_abc123",
      "name": "City Medical Center",
      "status": "ACTIVE"
    },
    "adminUser": {
      "userId": "usr_12345",
      "role": "ADMIN"
    },
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

#### POST /api/v1/auth/clinic/login

**Purpose**: Initiate login process by sending WhatsApp OTP  
**Access**: Public  
**Usage**: First step of login - sends OTP to user's WhatsApp

**Request:**

```json
{
  "whatsappNumber": "+919876543210",
  "clinicId": "clinic_abc123"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Login OTP sent to WhatsApp",
  "data": {
    "loginRequestId": "login_req_456",
    "otpExpiresIn": 300,
    "maskedNumber": "+91987****210"
  }
}
```

**OTP Message Template:**
"Your PulseOps login OTP is: 123456. Valid for 5 minutes."

#### POST /api/v1/auth/clinic/verify-login

**Purpose**: Complete login process by verifying OTP and password  
**Access**: Public  
**Usage**: Second step of login - validates OTP and authenticates user

**Request:**

```json
{
  "loginRequestId": "login_req_456",
  "otp": "123456",
  "password": "securePassword123"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {
      "userId": "usr_12345",
      "whatsappNumber": "+919876543210",
      "role": "ADMIN",
      "clinicId": "clinic_abc123",
      "doctorId": null,
      "permissions": ["manage_doctors", "view_analytics", "manage_subscription"]
    },
    "clinic": {
      "clinicId": "clinic_abc123",
      "name": "City Medical Center"
    },
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

#### POST /api/v1/auth/forgot-password

**Purpose**: Initiate password reset with WhatsApp OTP  
**Access**: Public  
**Usage**: Reset password when user forgets current password

**Request:**

```json
{
  "whatsappNumber": "+919876543210",
  "clinicId": "clinic_abc123"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Password reset OTP sent to WhatsApp",
  "data": {
    "resetRequestId": "reset_req_789",
    "otpExpiresIn": 300,
    "maskedNumber": "+91987****210"
  }
}
```

**OTP Message Template:**
"Your PulseOps password reset OTP is: 123456. Valid for 5 minutes."

#### POST /api/v1/auth/reset-password

**Purpose**: Complete password reset with OTP verification  
**Access**: Public  
**Usage**: Set new password after OTP verification

**Request:**

```json
{
  "resetRequestId": "reset_req_789",
  "otp": "123456",
  "newPassword": "newSecurePassword123"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Password reset successfully",
  "data": {
    "userId": "usr_12345",
    "passwordUpdatedAt": "2025-01-15T10:30:00Z"
  }
}
```

#### POST /api/v1/auth/refresh

**Purpose**: Refresh JWT access token using refresh token  
**Access**: Authenticated users  
**Usage**: Maintain session without re-login

**Request:**

```json
{
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

#### POST /api/v1/auth/logout

**Purpose**: Invalidate current session and tokens  
**Access**: Authenticated users  
**Usage**: Secure logout process

**Request:**

```json
{
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**

```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

### 6.2 Clinic Management APIs

#### GET /api/v1/clinics/profile

**Purpose**: Get clinic information and subscription details  
**Access**: Admin only  
**Usage**: Clinic dashboard and settings display

**Response:**

```json
{
  "success": true,
  "data": {
    "clinic": {
      "clinicId": "clinic_abc123",
      "name": "City Medical Center",
      "address": "123 Main St, Mumbai",
      "phone": "+919876543210",
      "whatsappNumber": "+919876543210",
      "status": "ACTIVE",
      "createdAt": "2025-01-15T09:00:00Z"
    },
    "subscription": {
      "plan": "PROFESSIONAL",
      "maxDoctors": 10,
      "currentDoctors": 3,
      "pricePerDoctor": 649,
      "totalAmount": 1947,
      "billingCycle": "MONTHLY",
      "nextBillingDate": "2025-02-15",
      "status": "ACTIVE"
    }
  }
}
```

#### PUT /api/v1/clinics/profile

**Purpose**: Update clinic information (name, address, WhatsApp config)  
**Access**: Admin only  
**Usage**: Clinic profile management

**Request:**

```json
{
  "name": "Updated Medical Center",
  "address": "456 New Street, Mumbai",
  "phone": "+919876543211",
  "whatsappNumber": "+919876543211"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Clinic profile updated successfully",
  "data": {
    "clinicId": "clinic_abc123",
    "name": "Updated Medical Center",
    "address": "456 New Street, Mumbai",
    "phone": "+919876543211",
    "whatsappNumber": "+919876543211",
    "updatedAt": "2025-01-15T10:30:00Z"
  }
}
```

#### GET /api/v1/clinics/subscription

**Purpose**: Get current subscription plan and billing information  
**Access**: Admin only  
**Usage**: Subscription management dashboard

**Response:**

```json
{
  "success": true,
  "data": {
    "currentPlan": {
      "plan": "PROFESSIONAL",
      "maxDoctors": 10,
      "currentDoctors": 3,
      "pricePerDoctor": 649,
      "totalAmount": 1947,
      "billingCycle": "MONTHLY",
      "status": "ACTIVE"
    },
    "billing": {
      "nextBillingDate": "2025-02-15",
      "lastPaymentDate": "2025-01-15",
      "lastPaymentAmount": 1947,
      "paymentMethod": "UPI"
    },
    "usage": {
      "totalTokensThisMonth": 450,
      "totalRevenueThisMonth": 225000
    }
  }
}
```

#### POST /api/v1/clinics/subscription/upgrade

**Purpose**: Upgrade/downgrade subscription plan  
**Access**: Admin only  
**Usage**: Change subscription tier based on doctor count

**Request:**

```json
{
  "newPlan": "ENTERPRISE",
  "estimatedDoctors": 15
}
```

**Response:**

```json
{
  "success": true,
  "message": "Subscription updated successfully",
  "data": {
    "previousPlan": "PROFESSIONAL",
    "newPlan": "ENTERPRISE",
    "priceChange": {
      "oldPricePerDoctor": 649,
      "newPricePerDoctor": 549,
      "estimatedMonthlySaving": 1500
    },
    "effectiveDate": "2025-02-01",
    "nextBillingAmount": 8235
  }
}
```

#### GET /api/v1/clinics/analytics

**Purpose**: Get clinic-wide analytics and reports  
**Access**: Admin only  
**Usage**: Business intelligence and performance monitoring

**Query Parameters:**

```
?period=last_30_days&metrics=revenue,patients,tokens
```

**Response:**

```json
{
  "success": true,
  "data": {
    "summary": {
      "totalRevenue": 850000,
      "totalPatients": 1250,
      "totalTokens": 1700,
      "averageTokensPerDay": 56,
      "patientSatisfaction": 4.8
    },
    "trends": {
      "revenueGrowth": "15%",
      "patientGrowth": "22%",
      "averageWaitTime": "18 minutes"
    },
    "topDoctors": [
      {
        "doctorId": "doc_67890",
        "name": "Dr. Rajesh Sharma",
        "tokensCompleted": 420,
        "revenue": 210000,
        "avgConsultationTime": "12 minutes"
      }
    ]
  }
}
```

---

### 6.3 Doctor Management APIs

#### GET /api/v1/doctors

**Purpose**: Get all doctors in clinic with their account status  
**Access**: Admin (all doctors), Doctor (self only)  
**Usage**: Doctor listing and selection

**Response:**

```json
{
  "success": true,
  "data": {
    "doctors": [
      {
        "doctorId": "doc_67890",
        "userId": "usr_67890",
        "name": "Dr. Rajesh Sharma",
        "whatsappNumber": "+919876543211",
        "specialization": "General Medicine",
        "consultationFee": 500,
        "advanceAmount": 50,
        "dailyLimit": 40,
        "consultationDuration": 15,
        "startTime": "09:00",
        "endTime": "17:00",
        "lunchBreak": "13:00-14:00",
        "status": "ACTIVE",
        "accountStatus": "ACTIVE",
        "lastLogin": "2025-01-15T08:30:00Z",
        "createdAt": "2025-01-15T09:00:00Z"
      }
    ],
    "totalDoctors": 1
  }
}
```

#### POST /api/v1/doctors

**Purpose**: Add new doctor to clinic (creates both user account & doctor profile)  
**Access**: Admin only  
**Usage**: Onboard new practitioners with complete account setup

**Request:**

```json
{
  "name": "Dr. Priya Patel",
  "whatsappNumber": "+919876543212",
  "specialization": "Pediatrics",
  "consultationFee": 600,
  "advanceAmount": 60,
  "dailyLimit": 30,
  "consultationDuration": 20,
  "startTime": "10:00",
  "endTime": "18:00",
  "lunchBreak": "14:00-15:00",
  "initialPassword": "temporaryPassword123"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Doctor added successfully. Login credentials sent via WhatsApp.",
  "data": {
    "doctor": {
      "doctorId": "doc_12345",
      "userId": "usr_99999",
      "name": "Dr. Priya Patel",
      "whatsappNumber": "+919876543212",
      "specialization": "Pediatrics",
      "consultationFee": 600,
      "status": "ACTIVE"
    },
    "account": {
      "userId": "usr_99999",
      "role": "DOCTOR",
      "status": "ACTIVE",
      "mustChangePassword": true
    },
    "whatsappMessage": "Welcome to PulseOps! Your login details: WhatsApp: +919876543212, Temp Password: temporaryPassword123. Please change password on first login."
  }
}
```

#### GET /api/v1/doctors/{doctorId}

**Purpose**: Get doctor profile and account information  
**Access**: Admin (any doctor), Doctor (self only)  
**Usage**: Doctor profile display and account management

**Response:**

```json
{
  "success": true,
  "data": {
    "doctor": {
      "doctorId": "doc_67890",
      "name": "Dr. Rajesh Sharma",
      "specialization": "General Medicine",
      "consultationFee": 500,
      "advanceAmount": 50,
      "dailyLimit": 40,
      "consultationDuration": 15,
      "startTime": "09:00",
      "endTime": "17:00",
      "lunchBreak": "13:00-14:00",
      "status": "ACTIVE",
      "createdAt": "2025-01-15T09:00:00Z"
    },
    "account": {
      "userId": "usr_67890",
      "whatsappNumber": "+919876543211",
      "role": "DOCTOR",
      "permissions": [
        "view_own_queue",
        "manage_own_patients",
        "add_visit_notes"
      ],
      "status": "ACTIVE",
      "lastLogin": "2025-01-15T08:30:00Z",
      "mustChangePassword": false
    },
    "statistics": {
      "totalPatientsThisMonth": 45,
      "totalTokensThisMonth": 120,
      "averageRating": 4.8,
      "totalRevenue": 60000
    }
  }
}
```

#### PUT /api/v1/doctors/{doctorId}

**Purpose**: Update doctor profile and account settings  
**Access**: Admin (any doctor), Doctor (self only)  
**Usage**: Profile and schedule management

**Request:**

```json
{
  "name": "Dr. Rajesh Kumar Sharma",
  "whatsappNumber": "+919876543213",
  "specialization": "General Medicine & Diabetes",
  "consultationFee": 550,
  "advanceAmount": 55,
  "dailyLimit": 45,
  "startTime": "08:30",
  "endTime": "17:30",
  "lunchBreak": "13:30-14:30"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Doctor profile updated successfully",
  "data": {
    "doctorId": "doc_67890",
    "updatedFields": [
      "name",
      "whatsappNumber",
      "consultationFee",
      "advanceAmount",
      "dailyLimit",
      "startTime",
      "endTime",
      "lunchBreak"
    ],
    "whatsappUpdated": true,
    "notificationSent": "WhatsApp number change confirmed via SMS to new number",
    "updatedAt": "2025-01-15T10:30:00Z"
  }
}
```

#### DELETE /api/v1/doctors/{doctorId}

**Purpose**: Remove doctor from clinic (deactivates both profile & account)  
**Access**: Admin only  
**Usage**: Offboard practitioners

**Response:**

```json
{
  "success": true,
  "message": "Doctor removed from clinic successfully",
  "data": {
    "doctorId": "doc_67890",
    "userId": "usr_67890",
    "name": "Dr. Rajesh Sharma",
    "status": "INACTIVE",
    "deactivatedAt": "2025-01-15T10:30:00Z",
    "dataRetention": {
      "patientRecordsPreserved": true,
      "visitHistoryPreserved": true,
      "accessRevoked": true
    }
  }
}
```

#### GET /api/v1/doctors/{doctorId}/stats

**Purpose**: Get comprehensive doctor performance statistics  
**Access**: Admin (any doctor), Doctor (self only)  
**Usage**: Performance monitoring and reports

**Query Parameters:**

```
?period=last_30_days&include=patients,revenue,ratings
```

**Response:**

```json
{
  "success": true,
  "data": {
    "doctor": {
      "doctorId": "doc_67890",
      "name": "Dr. Rajesh Sharma"
    },
    "period": "last_30_days",
    "performance": {
      "totalTokens": 120,
      "completedTokens": 115,
      "cancelledTokens": 5,
      "noShowTokens": 8,
      "completionRate": "95.8%"
    },
    "patients": {
      "totalPatients": 45,
      "newPatients": 12,
      "returnPatients": 33,
      "averageVisitsPerPatient": 2.7
    },
    "revenue": {
      "totalRevenue": 60000,
      "advanceCollected": 6000,
      "consultationRevenue": 54000,
      "averageRevenuePerDay": 2000
    },
    "efficiency": {
      "averageConsultationTime": "12 minutes",
      "averageWaitTime": "18 minutes",
      "patientSatisfaction": 4.8,
      "punctualityScore": "92%"
    },
    "trends": {
      "patientGrowth": "+15%",
      "revenueGrowth": "+12%",
      "efficiencyImprovement": "+5%"
    }
  }
}
```

---

### 6.4 Patient Management APIs

#### GET /api/v1/patients/search

**Purpose**: Search patients by phone number or name  
**Access**: Doctor (own patients), Admin (clinic patients)  
**Usage**: Find existing patients for booking

**Query Parameters:**

```
?phone=+919988776655&name=Amit&limit=10
```

**Response:**

```json
{
  "success": true,
  "data": {
    "patients": [
      {
        "phone": "+919988776655",
        "name": "Amit Kumar",
        "age": 32,
        "gender": "MALE",
        "lastVisit": "2025-01-15",
        "totalVisits": 3,
        "isAssociatedWithDoctor": true
      }
    ],
    "totalFound": 1,
    "searchTerm": "Amit"
  }
}
```

#### POST /api/v1/patients

**Purpose**: Create new global patient record  
**Access**: Any authenticated user  
**Usage**: Register new patient during first visit

**Request:**

```json
{
  "phone": "+919988776655",
  "name": "Amit Kumar",
  "dateOfBirth": "1992-03-15",
  "gender": "MALE",
  "address": "123 ABC Street, Mumbai",
  "emergencyContact": "+919876543210",
  "bloodGroup": "O+",
  "allergies": ["Penicillin", "Dust"],
  "chronicConditions": []
}
```

**Response:**

```json
{
  "success": true,
  "message": "Patient record created successfully",
  "data": {
    "phone": "+919988776655",
    "name": "Amit Kumar",
    "age": 32,
    "gender": "MALE",
    "bloodGroup": "O+",
    "allergies": ["Penicillin", "Dust"],
    "createdAt": "2025-01-15T10:00:00Z"
  }
}
```

#### GET /api/v1/patients/{patientId}

**Purpose**: Get patient details by unique identifier  
**Access**: Doctor (own patients), Admin (clinic patients)  
**Usage**: Patient profile view

**Response:**

```json
{
  "success": true,
  "data": {
    "patient": {
      "patientId": "pat_12345",
      "patientPhone": "+919876543210",
      "name": "Rajesh Kumar",
      "dateOfBirth": "1980-05-15",
      "age": 44,
      "gender": "MALE",
      "address": "123 ABC Street, Mumbai",
      "emergencyContact": "+919876543211",
      "bloodGroup": "O+",
      "allergies": ["Penicillin", "Dust"],
      "chronicConditions": ["Diabetes"],
      "currentMedications": ["Metformin"],
      "createdAt": "2024-06-10T14:30:00Z",
      "updatedAt": "2025-01-15T10:15:00Z"
    }
  }
}
```

#### PUT /api/v1/patients/{patientId}

**Purpose**: Update patient information  
**Access**: Doctor (own patients), Admin (clinic patients)  
**Usage**: Patient profile management

**Request:**

```json
{
  "name": "Rajesh Kumar",
  "dateOfBirth": "1980-05-15",
  "gender": "MALE",
  "address": "456 XYZ Street, Mumbai",
  "emergencyContact": "+919876543211",
  "bloodGroup": "O+",
  "allergies": ["Penicillin", "Dust", "Shellfish"],
  "chronicConditions": ["Diabetes", "Hypertension"]
}
```

**Response:**

```json
{
  "success": true,
  "message": "Patient updated successfully",
  "data": {
    "patientId": "pat_12345",
    "updatedAt": "2025-01-15T11:30:00Z"
  }
}
```

---

### 6.5 Patient Association APIs

#### GET /api/v1/doctors/{doctorId}/patients

**Purpose**: Get all patients associated with doctor  
**Access**: Doctor (own patients), Admin (any doctor)  
**Usage**: Doctor's patient list

**Response:**

```json
{
  "success": true,
  "data": {
    "patients": [
      {
        "patientId": "pat_12345",
        "patientPhone": "+919876543210",
        "name": "Rajesh Kumar",
        "age": 45,
        "gender": "MALE",
        "associationDate": "2025-01-10T09:00:00Z",
        "lastVisitDate": "2025-01-15T14:30:00Z",
        "totalVisits": 3,
        "preferences": {
          "preferredTime": "MORNING",
          "communicationMethod": "WHATSAPP"
        }
      }
    ],
    "totalCount": 25
  }
}
```

#### POST /api/v1/doctors/{doctorId}/patients

**Purpose**: Associate patient with doctor  
**Access**: Doctor (self), Admin (any doctor)  
**Usage**: Link patient to doctor on first visit

**Request:**

```json
{
  "patientPhone": "+919876543210",
  "patientName": "Rajesh Kumar",
  "age": 45,
  "gender": "MALE",
  "preferences": {
    "preferredTime": "MORNING",
    "communicationMethod": "WHATSAPP"
  }
}
```

**Response:**

```json
{
  "success": true,
  "message": "Patient associated successfully",
  "data": {
    "associationId": "assoc_12345",
    "patientId": "pat_12345",
    "patientPhone": "+919876543210",
    "doctorId": "doc_67890",
    "associationDate": "2025-01-15T10:00:00Z"
  }
}
```

#### GET /api/v1/doctors/{doctorId}/patients/{patientId}

**Purpose**: Get patient details for specific doctor  
**Access**: Doctor (own association), Admin (clinic associations)  
**Usage**: Patient profile with relationship data

**Response:**

```json
{
  "success": true,
  "data": {
    "patient": {
      "patientId": "pat_12345",
      "patientPhone": "+919876543210",
      "name": "Rajesh Kumar",
      "age": 45,
      "gender": "MALE",
      "associationDate": "2025-01-10T09:00:00Z",
      "lastVisitDate": "2025-01-15T14:30:00Z",
      "totalVisits": 3,
      "preferences": {
        "preferredTime": "MORNING",
        "communicationMethod": "WHATSAPP"
      },
      "medicalHistory": {
        "allergies": ["Penicillin"],
        "chronicConditions": ["Diabetes"],
        "currentMedications": ["Metformin"]
      }
    }
  }
}
```

#### PUT /api/v1/doctors/{doctorId}/patients/{patientId}

**Purpose**: Update doctor-patient relationship data  
**Access**: Doctor (own association), Admin (clinic associations)  
**Usage**: Update patient notes and preferences

**Request:**

```json
{
  "preferences": {
    "preferredTime": "AFTERNOON",
    "communicationMethod": "WHATSAPP"
  },
  "notes": "Patient prefers afternoon appointments due to work schedule"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Patient association updated successfully",
  "data": {
    "patientId": "pat_12345",
    "updatedAt": "2025-01-15T11:30:00Z"
  }
}
```

#### DELETE /api/v1/doctors/{doctorId}/patients/{patientId}

**Purpose**: Remove patient association  
**Access**: Doctor (own association), Admin (clinic associations)  
**Usage**: End doctor-patient relationship

**Response:**

```json
{
  "success": true,
  "message": "Patient association removed successfully",
  "data": {
    "patientId": "pat_12345",
    "removedAt": "2025-01-15T12:00:00Z"
  }
}
```

---

### 6.6 Queue Management APIs

#### GET /api/v1/doctors/{doctorId}/queue/current

**Purpose**: Get current day's queue status and tokens  
**Access**: Doctor (own queue), Admin (any doctor queue)  
**Usage**: Queue dashboard display

**Response:**

```json
{
  "success": true,
  "data": {
    "queue": {
      "queueId": "queue_12345",
      "doctorId": "doc_67890",
      "date": "2025-01-15",
      "status": "ACTIVE",
      "currentToken": "TKN_001",
      "totalTokens": 25,
      "completedTokens": 8,
      "pendingTokens": 12,
      "skippedTokens": 5,
      "startTime": "2025-01-15T09:00:00Z",
      "estimatedEndTime": "2025-01-15T17:00:00Z"
    },
    "tokens": [
      {
        "tokenId": "TKN_001",
        "patientPhone": "+919876543210",
        "patientName": "Rajesh Kumar",
        "status": "CURRENT",
        "estimatedTime": "2025-01-15T14:30:00Z",
        "actualTime": null
      }
    ]
  }
}
```

#### POST /api/v1/doctors/{doctorId}/queue/start

**Purpose**: Start/activate queue for the day  
**Access**: Doctor (own queue), Admin (any doctor queue)  
**Usage**: Begin daily operations

**Request:**

```json
{
  "startTime": "2025-01-15T09:00:00Z",
  "estimatedEndTime": "2025-01-15T17:00:00Z"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Queue started successfully",
  "data": {
    "queueId": "queue_12345",
    "status": "ACTIVE",
    "startTime": "2025-01-15T09:00:00Z"
  }
}
```

#### POST /api/v1/doctors/{doctorId}/queue/call-next

**Purpose**: Call next token in queue  
**Access**: Doctor (own queue), Admin (any doctor queue)  
**Usage**: Progress through patient queue

**Response:**

```json
{
  "success": true,
  "message": "Next patient called",
  "data": {
    "currentToken": "TKN_002",
    "patientName": "Priya Sharma",
    "patientPhone": "+919876543211",
    "estimatedTime": "2025-01-15T14:45:00Z"
  }
}
```

#### POST /api/v1/doctors/{doctorId}/queue/skip

**Purpose**: Skip current token (patient not present)  
**Access**: Doctor (own queue), Admin (any doctor queue)  
**Usage**: Handle no-show patients

**Request:**

```json
{
  "reason": "PATIENT_NOT_PRESENT",
  "notes": "Patient called to reschedule"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Token skipped successfully",
  "data": {
    "skippedToken": "TKN_002",
    "nextToken": "TKN_003",
    "reason": "PATIENT_NOT_PRESENT"
  }
}
```

#### POST /api/v1/doctors/{doctorId}/queue/pause

**Purpose**: Pause queue (lunch break, emergency)  
**Access**: Doctor (own queue), Admin (any doctor queue)  
**Usage**: Temporary queue suspension

**Request:**

```json
{
  "reason": "LUNCH_BREAK",
  "estimatedResumeTime": "2025-01-15T13:30:00Z"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Queue paused successfully",
  "data": {
    "status": "PAUSED",
    "pauseReason": "LUNCH_BREAK",
    "pausedAt": "2025-01-15T12:00:00Z",
    "estimatedResumeTime": "2025-01-15T13:30:00Z"
  }
}
```

#### POST /api/v1/doctors/{doctorId}/queue/resume

**Purpose**: Resume paused queue  
**Access**: Doctor (own queue), Admin (any doctor queue)  
**Usage**: Continue after pause

**Response:**

```json
{
  "success": true,
  "message": "Queue resumed successfully",
  "data": {
    "status": "ACTIVE",
    "resumedAt": "2025-01-15T13:30:00Z",
    "currentToken": "TKN_003"
  }
}
```

#### POST /api/v1/doctors/{doctorId}/queue/close

**Purpose**: Close queue for the day  
**Access**: Doctor (own queue), Admin (any doctor queue)  
**Usage**: End daily operations

**Response:**

```json
{
  "success": true,
  "message": "Queue closed successfully",
  "data": {
    "status": "CLOSED",
    "closedAt": "2025-01-15T17:00:00Z",
    "summary": {
      "totalTokens": 25,
      "completedTokens": 20,
      "skippedTokens": 3,
      "pendingTokens": 2
    }
  }
}
```

#### GET /api/v1/doctors/{doctorId}/queue/stream

**Purpose**: Real-time queue updates via SSE  
**Access**: Doctor (own queue), Admin (any doctor queue)  
**Usage**: Live queue status monitoring

**Response (Server-Sent Events):**

```
event: queue_update
data: {
  "queueId": "queue_12345",
  "status": "ACTIVE",
  "currentToken": "TKN_004",
  "totalTokens": 25,
  "completedTokens": 10,
  "timestamp": "2025-01-15T14:30:00Z"
}
```

---

### 6.7 Token Management APIs

#### GET /api/v1/doctors/{doctorId}/tokens

**Purpose**: Get all tokens for doctor's queue  
**Access**: Doctor (own tokens), Admin (any doctor tokens)  
**Usage**: Token management interface

**Query Parameters:**

```
?date=2025-01-15&status=CONFIRMED
```

**Response:**

```json
{
  "success": true,
  "data": {
    "tokens": [
      {
        "tokenId": "TKN_001",
        "patientId": "pat_12345",
        "patientPhone": "+919876543210",
        "patientName": "Rajesh Kumar",
        "status": "CONFIRMED",
        "tokenNumber": "001",
        "estimatedTime": "2025-01-15T14:30:00Z",
        "actualTime": null,
        "paymentStatus": "PAID",
        "amount": 500,
        "createdAt": "2025-01-15T09:00:00Z"
      }
    ],
    "totalCount": 25,
    "summary": {
      "confirmed": 15,
      "completed": 8,
      "cancelled": 2
    }
  }
}
```

#### POST /api/v1/doctors/{doctorId}/tokens

**Purpose**: Create new token booking  
**Access**: Doctor (own queue), Admin (any doctor queue)  
**Usage**: Manual token booking

**Request:**

```json
{
  "patientId": "pat_12345",
  "patientPhone": "+919876543210",
  "patientName": "Rajesh Kumar",
  "preferredTime": "2025-01-15T14:30:00Z",
  "consultationType": "GENERAL",
  "amount": 500
}
```

**Response:**

```json
{
  "success": true,
  "message": "Token created successfully",
  "data": {
    "tokenId": "TKN_001",
    "patientId": "pat_12345",
    "tokenNumber": "001",
    "status": "PENDING",
    "estimatedTime": "2025-01-15T14:30:00Z",
    "paymentLink": "https://pay.pulseops.com/tkn_001"
  }
}
```

#### GET /api/v1/tokens/{tokenId}

**Purpose**: Get specific token details  
**Access**: Doctor (own tokens), Admin (clinic tokens)  
**Usage**: Token detail view

**Response:**

```json
{
  "success": true,
  "data": {
    "token": {
      "tokenId": "TKN_001",
      "patientId": "pat_12345",
      "doctorId": "doc_67890",
      "patientPhone": "+919876543210",
      "patientName": "Rajesh Kumar",
      "status": "CONFIRMED",
      "tokenNumber": "001",
      "estimatedTime": "2025-01-15T14:30:00Z",
      "actualTime": null,
      "consultationType": "GENERAL",
      "paymentStatus": "PAID",
      "amount": 500,
      "createdAt": "2025-01-15T09:00:00Z",
      "visitId": "visit_12345"
    }
  }
}
```

#### PUT /api/v1/tokens/{tokenId}

**Purpose**: Update token status and information  
**Access**: Doctor (own tokens), Admin (clinic tokens)  
**Usage**: Token status management

**Request:**

```json
{
  "status": "COMPLETED",
  "actualTime": "2025-01-15T14:45:00Z",
  "notes": "Patient consultation completed successfully"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Token updated successfully",
  "data": {
    "tokenId": "TKN_001",
    "status": "COMPLETED",
    "updatedAt": "2025-01-15T14:45:00Z"
  }
}
```

#### DELETE /api/v1/tokens/{tokenId}

**Purpose**: Cancel token booking  
**Access**: Doctor (own tokens), Admin (clinic tokens)  
**Usage**: Handle cancellations

**Request:**

```json
{
  "reason": "PATIENT_REQUEST",
  "notes": "Patient requested cancellation due to emergency"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Token cancelled successfully",
  "data": {
    "tokenId": "TKN_001",
    "status": "CANCELLED",
    "refundAmount": 500,
    "cancelledAt": "2025-01-15T13:00:00Z"
  }
}
```

#### GET /api/v1/patients/{patientId}/tokens

**Purpose**: Get patient's token history  
**Access**: Doctor (own patients), Admin (clinic patients)  
**Usage**: Patient booking history

**Response:**

```json
{
  "success": true,
  "data": {
    "patient": {
      "patientId": "pat_12345",
      "patientPhone": "+919876543210",
      "name": "Rajesh Kumar"
    },
    "tokens": [
      {
        "tokenId": "TKN_001",
        "patientId": "pat_12345",
        "doctorId": "doc_67890",
        "doctorName": "Dr. Sharma",
        "status": "COMPLETED",
        "date": "2025-01-15",
        "amount": 500,
        "consultationType": "GENERAL"
      }
    ],
    "totalCount": 15
  }
}
```

---

### 6.8 Visit Record APIs

#### GET /api/v1/doctors/{doctorId}/patients/{patientId}/visits

**Purpose**: Get patient's visit history with doctor  
**Access**: Doctor (own patients), Admin (clinic patients)  
**Usage**: Medical history review

**Response:**

```json
{
  "success": true,
  "data": {
    "patient": {
      "patientId": "pat_12345",
      "patientPhone": "+919876543210",
      "name": "Rajesh Kumar"
    },
    "visits": [
      {
        "visitId": "visit_12345",
        "date": "2025-01-15",
        "tokenId": "TKN_001",
        "status": "COMPLETED",
        "diagnosis": "Hypertension",
        "prescription": "Amlodipine 5mg",
        "notes": "Patient responding well to treatment",
        "createdAt": "2025-01-15T14:30:00Z"
      }
    ],
    "totalCount": 5
  }
}
```

#### POST /api/v1/doctors/{doctorId}/patients/{patientId}/visits

**Purpose**: Create new visit record  
**Access**: Doctor (own patients), Admin (clinic patients)  
**Usage**: Document consultation

**Request:**

```json
{
  "tokenId": "TKN_001",
  "visitDate": "2025-01-15",
  "chiefComplaint": "Headache and dizziness",
  "vitalSigns": {
    "bloodPressure": "140/90",
    "pulse": "72",
    "temperature": "98.6",
    "weight": "70kg"
  },
  "examination": "General examination normal, BP elevated"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Visit record created successfully",
  "data": {
    "visitId": "visit_12345",
    "patientId": "pat_12345",
    "doctorId": "doc_67890",
    "createdAt": "2025-01-15T14:30:00Z"
  }
}
```

#### GET /api/v1/visits/{visitId}

**Purpose**: Get specific visit details  
**Access**: Doctor (own visits), Admin (clinic visits)  
**Usage**: Visit record review

**Response:**

```json
{
  "success": true,
  "data": {
    "visit": {
      "visitId": "visit_12345",
      "patientId": "pat_12345",
      "patientPhone": "+919876543210",
      "patientName": "Rajesh Kumar",
      "doctorId": "doc_67890",
      "doctorName": "Dr. Sharma",
      "visitDate": "2025-01-15",
      "tokenId": "TKN_001",
      "status": "COMPLETED",
      "chiefComplaint": "Headache and dizziness",
      "vitalSigns": {
        "bloodPressure": "140/90",
        "pulse": "72",
        "temperature": "98.6",
        "weight": "70kg"
      },
      "examination": "General examination normal, BP elevated",
      "diagnosis": "Hypertension",
      "prescription": "Amlodipine 5mg",
      "notes": "Patient responding well to treatment",
      "privateNotes": "Patient seems anxious about work stress",
      "createdAt": "2025-01-15T14:30:00Z",
      "updatedAt": "2025-01-15T15:00:00Z"
    }
  }
}
```

#### PUT /api/v1/visits/{visitId}

**Purpose**: Update visit record and medical notes  
**Access**: Doctor (own visits), Admin (clinic visits)  
**Usage**: Edit consultation documentation

**Request:**

```json
{
  "examination": "Updated examination findings",
  "diagnosis": "Updated diagnosis",
  "prescription": "Updated prescription",
  "notes": "Updated treatment notes"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Visit record updated successfully",
  "data": {
    "visitId": "visit_12345",
    "updatedAt": "2025-01-15T16:00:00Z"
  }
}
```

#### POST /api/v1/visits/{visitId}/diagnosis

**Purpose**: Add/update diagnosis for visit  
**Access**: Doctor (own visits), Admin (clinic visits)  
**Usage**: Medical diagnosis documentation

**Request:**

```json
{
  "diagnosis": "Hypertension Stage 1",
  "icd10Code": "I10",
  "severity": "MILD",
  "notes": "Primary hypertension, no secondary causes identified"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Diagnosis updated successfully",
  "data": {
    "visitId": "visit_12345",
    "diagnosis": "Hypertension Stage 1",
    "updatedAt": "2025-01-15T15:30:00Z"
  }
}
```

#### POST /api/v1/visits/{visitId}/prescription

**Purpose**: Add/update prescription for visit  
**Access**: Doctor (own visits), Admin (clinic visits)  
**Usage**: Digital prescription management

**Request:**

```json
{
  "medications": [
    {
      "name": "Amlodipine",
      "strength": "5mg",
      "frequency": "Once daily",
      "duration": "30 days",
      "instructions": "Take in the morning"
    }
  ],
  "notes": "Monitor BP weekly, return in 30 days"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Prescription updated successfully",
  "data": {
    "visitId": "visit_12345",
    "prescriptionId": "pres_67890",
    "updatedAt": "2025-01-15T15:45:00Z"
  }
}
```

#### POST /api/v1/visits/{visitId}/notes

**Purpose**: Add private doctor notes to visit  
**Access**: Doctor (own visits), Admin (clinic visits)  
**Usage**: Confidential medical observations

**Request:**

```json
{
  "privateNotes": "Patient appears to be under significant work stress. Consider counseling referral if symptoms persist.",
  "isConfidential": true
}
```

**Response:**

```json
{
  "success": true,
  "message": "Private notes added successfully",
  "data": {
    "visitId": "visit_12345",
    "notesId": "notes_11111",
    "isConfidential": true,
    "createdAt": "2025-01-15T16:00:00Z"
  }
}
```

---

### 6.9 Analytics & Reporting APIs

#### GET /api/v1/analytics/clinic/dashboard

**Purpose**: Get clinic dashboard metrics  
**Access**: Admin only  
**Usage**: Executive dashboard

**Query Parameters:**

```
?period=last_30_days&metrics=revenue,patients,tokens
```

**Response:**

```json
{
  "success": true,
  "data": {
    "summary": {
      "totalRevenue": 850000,
      "totalPatients": 1250,
      "totalTokens": 1700,
      "averageTokensPerDay": 56,
      "patientSatisfaction": 4.8
    },
    "trends": {
      "revenueGrowth": "15%",
      "patientGrowth": "22%",
      "averageWaitTime": "18 minutes"
    },
    "topDoctors": [
      {
        "doctorId": "doc_67890",
        "name": "Dr. Rajesh Sharma",
        "tokensCompleted": 420,
        "revenue": 210000,
        "avgConsultationTime": "12 minutes"
      }
    ]
  }
}
```

#### GET /api/v1/analytics/doctors/{doctorId}/performance

**Purpose**: Get doctor performance metrics  
**Access**: Doctor (self), Admin (any doctor)  
**Usage**: Individual performance tracking

**Query Parameters:**

```
?period=last_30_days&metrics=tokens,revenue,patients
```

**Response:**

```json
{
  "success": true,
  "data": {
    "doctor": {
      "doctorId": "doc_67890",
      "name": "Dr. Rajesh Sharma"
    },
    "performance": {
      "totalTokens": 420,
      "completedTokens": 395,
      "cancelledTokens": 25,
      "totalRevenue": 210000,
      "averageConsultationTime": "12 minutes",
      "patientSatisfaction": 4.9
    },
    "trends": {
      "dailyAverage": 14,
      "weeklyGrowth": "8%",
      "monthlyGrowth": "15%"
    },
    "patientMetrics": {
      "newPatients": 45,
      "returningPatients": 375,
      "patientRetentionRate": "89%"
    }
  }
}
```

#### GET /api/v1/analytics/patients/flow

**Purpose**: Get patient flow analytics  
**Access**: Admin only  
**Usage**: Operational insights

**Query Parameters:**

```
?period=last_7_days&granularity=hourly
```

**Response:**

```json
{
  "success": true,
  "data": {
    "patientFlow": [
      {
        "hour": "09:00",
        "arrivals": 15,
        "departures": 0,
        "waiting": 15
      },
      {
        "hour": "10:00",
        "arrivals": 22,
        "departures": 12,
        "waiting": 25
      }
    ],
    "peakHours": ["10:00", "14:00", "16:00"],
    "averageWaitTime": "18 minutes",
    "bottlenecks": [
      {
        "timeSlot": "14:00-15:00",
        "waitTime": "25 minutes",
        "reason": "High patient volume"
      }
    ]
  }
}
```

#### GET /api/v1/analytics/revenue

**Purpose**: Get revenue and billing analytics  
**Access**: Admin only  
**Usage**: Financial reporting

**Query Parameters:**

```
?period=last_30_days&breakdown=by_doctor
```

**Response:**

```json
{
  "success": true,
  "data": {
    "revenue": {
      "totalRevenue": 850000,
      "totalConsultations": 1700,
      "averageConsultationFee": 500,
      "growthRate": "15%"
    },
    "breakdown": {
      "byDoctor": [
        {
          "doctorId": "doc_67890",
          "name": "Dr. Rajesh Sharma",
          "revenue": 210000,
          "consultations": 420
        }
      ],
      "byConsultationType": {
        "GENERAL": 600000,
        "SPECIALIST": 250000
      }
    },
    "trends": {
      "dailyAverage": 28333,
      "weeklyGrowth": "12%",
      "monthlyGrowth": "15%"
    }
  }
}
```

#### POST /api/v1/reports/generate

**Purpose**: Generate custom reports  
**Access**: Admin only  
**Usage**: Business intelligence reporting

**Request:**

```json
{
  "reportType": "DOCTOR_PERFORMANCE",
  "parameters": {
    "startDate": "2025-01-01",
    "endDate": "2025-01-31",
    "doctorIds": ["doc_67890", "doc_67891"],
    "metrics": ["revenue", "patients", "satisfaction"]
  },
  "format": "PDF"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Report generation started",
  "data": {
    "reportId": "report_12345",
    "status": "PROCESSING",
    "estimatedCompletion": "2025-01-15T16:30:00Z",
    "downloadUrl": null
  }
}
```

---

### 6.10 WhatsApp Integration APIs

#### POST /api/v1/webhooks/whatsapp

**Purpose**: Handle WhatsApp webhook events  
**Access**: WhatsApp service only  
**Usage**: Process incoming messages and status updates

**Request (Webhook from WhatsApp):**

```json
{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "123456789",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {
              "display_phone_number": "919876543210",
              "phone_number_id": "987654321"
            },
            "contacts": [
              {
                "profile": {
                  "name": "Rajesh Kumar"
                },
                "wa_id": "919876543210"
              }
            ],
            "messages": [
              {
                "from": "919876543210",
                "id": "wamid.123456789",
                "timestamp": "1705312800",
                "text": {
                  "body": "Hello, I need an appointment"
                },
                "type": "text"
              }
            ]
          },
          "field": "messages"
        }
      ]
    }
  ]
}
```

**Response:**

```json
{
  "success": true,
  "message": "Webhook processed successfully"
}
```

#### POST /api/v1/whatsapp/send-message

**Purpose**: Send WhatsApp message to patient  
**Access**: Doctor (own patients), Admin (clinic patients)  
**Usage**: Patient communication

**Request:**

```json
{
  "patientPhone": "+919876543210",
  "messageType": "TEMPLATE",
  "templateName": "appointment_reminder",
  "templateData": {
    "patient_name": "Rajesh Kumar",
    "doctor_name": "Dr. Sharma",
    "appointment_time": "2025-01-15 14:30",
    "token_number": "TKN_001"
  }
}
```

**Response:**

```json
{
  "success": true,
  "message": "Message sent successfully",
  "data": {
    "messageId": "wamid.123456789",
    "status": "SENT",
    "sentAt": "2025-01-15T10:00:00Z"
  }
}
```

#### GET /api/v1/whatsapp/templates

**Purpose**: Get available message templates  
**Access**: Doctor, Admin  
**Usage**: Standardized patient communication

**Response:**

```json
{
  "success": true,
  "data": {
    "templates": [
      {
        "name": "appointment_reminder",
        "language": "en",
        "category": "UTILITY",
        "components": [
          {
            "type": "HEADER",
            "text": "Appointment Reminder"
          },
          {
            "type": "BODY",
            "text": "Hello {{patient_name}}, your appointment with {{doctor_name}} is scheduled for {{appointment_time}}. Your token number is {{token_number}}. Please arrive 10 minutes early."
          }
        ]
      },
      {
        "name": "token_confirmation",
        "language": "en",
        "category": "UTILITY",
        "components": [
          {
            "type": "HEADER",
            "text": "Token Confirmed"
          },
          {
            "type": "BODY",
            "text": "Your token {{token_number}} has been confirmed for {{appointment_time}} with {{doctor_name}}. Payment of ₹{{amount}} received."
          }
        ]
      }
    ]
  }
}
```

#### POST /api/v1/whatsapp/broadcast

**Purpose**: Send broadcast message to multiple patients  
**Access**: Admin only  
**Usage**: Clinic announcements

**Request:**

```json
{
  "recipients": ["+919876543210", "+919876543211"],
  "messageType": "TEMPLATE",
  "templateName": "clinic_announcement",
  "templateData": {
    "clinic_name": "City Medical Center",
    "announcement": "Clinic will be closed on Republic Day, January 26th"
  }
}
```

**Response:**

```json
{
  "success": true,
  "message": "Broadcast initiated successfully",
  "data": {
    "broadcastId": "broadcast_12345",
    "totalRecipients": 2,
    "sentCount": 2,
    "failedCount": 0,
    "status": "COMPLETED"
  }
}
```

## 9. Core Use Cases

### 9.1 Admin User Flow

#### Clinic Setup

1. **Registration**: Admin registers clinic with subscription plan
2. **Doctor Addition**: Admin adds doctors to clinic (up to plan limit)
3. **User Creation**: Admin creates doctor user accounts
4. **WhatsApp Config**: Admin configures WhatsApp Business number

#### Daily Operations

1. **Dashboard View**: See all doctors' queues and stats
2. **Patient Overview**: View all clinic patients and their visit history
3. **Doctor Performance**: Monitor individual doctor-patient relationships
4. **Analytics**: View revenue, patient flow, doctor performance
5. **Subscription**: Manage subscription, add/remove doctors
6. **Reports**: Generate and download detailed reports with patient data

### 9.2 Doctor User Flow

#### Queue Management

1. **Login**: Doctor logs in to see only their queue
2. **Start Day**: Activate queue for current date
3. **Call Patients**: Call next, skip, or pause as needed
4. **Emergency**: Pause queue for emergencies with patient notification
5. **End Day**: Close queue and review day's summary

#### Patient Management

1. **Patient List**: View only own patients and their basic info
2. **Visit History**: See complete history with own patients
3. **Current Visit**: Document current consultation with notes
4. **Add Diagnosis**: Record diagnosis and treatment plan
5. **Write Prescription**: Create and save prescription
6. **Follow-up**: Schedule follow-up appointments
7. **Patient Notes**: Add private notes about patient care

#### Restrictions

- Cannot see other doctors' queues or patients
- Cannot access financial/subscription data
- Cannot manage clinic settings
- Cannot view other doctors' patient notes or visit records
- Cannot access patient data from other clinics
- Limited to own patient associations only

### 9.3 Patient Data Flow

#### Patient Registration & Association

1. **First Visit**: Patient books token via WhatsApp
2. **Data Creation**: Global patient record created with phone number
3. **Doctor Association**: Patient automatically associated with booked doctor
4. **Visit Record**: Initial visit record created for consultation
5. **Privacy Isolation**: Patient data isolated per doctor-clinic boundary

#### Cross-Clinic Visits

1. **Different Clinic**: Patient can visit different clinic with same phone
2. **New Association**: Separate doctor-patient association created
3. **Data Isolation**: Previous clinic data remains private
4. **Independent Records**: Each clinic maintains separate visit history
5. **No Cross-Referencing**: Doctors cannot see other clinic visits

#### Patient Data Privacy Boundaries

```
Patient Phone: +919988776655

Clinic A - Dr. Smith:
├── Association: Active since Jan 2024
├── Visits: 5 consultations
├── Notes: "Regular patient, diabetic"
└── Access: Only Dr. Smith & Clinic A Admin

Clinic B - Dr. Patel:
├── Association: Active since Mar 2024
├── Visits: 2 consultations
├── Notes: "First time patient"
└── Access: Only Dr. Patel & Clinic B Admin

❌ Dr. Smith CANNOT see Clinic B data
❌ Dr. Patel CANNOT see Clinic A data
❌ Clinic A Admin CANNOT see Clinic B data
```

### 9.4 Patient WhatsApp Flow

#### Token Booking

```
Patient: "Hi"
Bot: "Welcome to City Medical Center! Please select doctor:
1. Dr. Sharma (General Medicine)
2. Dr. Patel (Pediatrics)"

Patient: "1"
Bot: "Available slots for Dr. Sharma today:
1. 10:30 AM (Token #8)
2. 11:15 AM (Token #10)
3. 2:00 PM (Token #15)"

Patient: "1"
Bot: "Token #8 for 10:30 AM
Advance: ₹50
Total fee: ₹500
Tap to pay: [WhatsApp Pay Link]"

Payment Success:
Bot: "✅ Booking confirmed!
Token #8 - Dr. Sharma
Time: 10:30 AM (approx)
Currently serving: Token #3
Your turn in ~45 minutes

Show this message at clinic for check-in."
```

#### Real-time Updates

```
Bot: "🔔 Update: Currently serving Token #6
Your turn in ~20 minutes (Token #8)"

Bot: "⚡ Dr. Sharma called for emergency
Estimated delay: 30 minutes
Reply:
1 - Wait and receive updates
2 - Reschedule to tomorrow
3 - Cancel and get refund"
```

---

## 10. Implementation Phases

### 10.1 Phase 1: Foundation (Weeks 1-2)

#### Backend Setup

```bash
# Project initialization
mkdir backend
cd backend
npm init -y

# Dependencies
npm install express typescript ts-node @types/node @types/express
npm install jsonwebtoken bcryptjs zod aws-sdk
npm install -D nodemon @types/jsonwebtoken @types/bcryptjs

# Project structure
mkdir -p src/{api/v1,controllers,services,repositories,models,core,utils}
mkdir -p tests/{controllers,services,repositories}
mkdir -p deployment scripts
```

### 10.2 Phase 2: Core Features (Weeks 3-4)

#### Backend Implementation

1. **Authentication System**: JWT with role-based access
2. **Clinic Management**: CRUD operations with proper isolation
3. **Doctor Management**: Admin controls with permission checks
4. **Queue Operations**: Real-time queue management
5. **Patient Management**: Global patient records with phone-based identification
6. **Doctor-Patient Associations**: Private relationship tracking per doctor
7. **WhatsApp Integration**: Webhook handling and message sending

### 10.3 Phase 3: Visit Records & Medical Notes (Weeks 5-6)

#### Visit Management Features

1. **Visit Documentation**: Complete visit record creation and management
2. **Medical Notes**: Rich text editor for doctor's private notes
3. **Diagnosis System**: Structured diagnosis input and history tracking
4. **Prescription Management**: Digital prescription creation and storage
5. **Patient History**: Chronological visit timeline per doctor-patient relationship
6. **Access Control**: Strict isolation of visit data per doctor and clinic

### 10.4 Phase 4: Integration & Testing (Weeks 7-8)

#### Testing Strategy

```bash
# Jest configuration
npm install -D jest @types/jest ts-jest supertest @types/supertest

# Test categories
# 1. Unit tests: Services and repositories
# 2. Integration tests: API endpoints
# 3. E2E tests: Complete user flows
```

#### Deployment

```yaml
# serverless.yml
service: pulse-ops-api
provider:
  name: aws
  runtime: nodejs18.x
  region: ap-south-1

functions:
  api:
    handler: deployment/lambda-handler.handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
          cors: true
```

---

## 11. Production-Ready Development Guidelines

### 11.1 Code Quality Standards

**TypeScript Configuration:**

```typescript
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "tests"]
}
```

**Linting Configuration:**

```javascript
// eslint.config.js
module.exports = {
  parser: '@typescript-eslint/parser',
  extends: ['eslint:recommended', '@typescript-eslint/recommended', 'prettier'],
  rules: {
    '@typescript-eslint/no-unused-vars': 'error',
    '@typescript-eslint/explicit-function-return-type': 'warn',
    'no-console': 'warn',
    'prefer-const': 'error',
  },
};
```

### 11.2 Testing Strategy

**Unit Testing Framework:**

```typescript
// jest.config.js
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  collectCoverageFrom: ['src/**/*.ts', '!src/**/*.d.ts', '!src/tests/**/*'],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};
```

**Test Categories:**

1. **Unit Tests**: Services, repositories, utilities
2. **Integration Tests**: API endpoints with database
3. **E2E Tests**: Complete user workflows
4. **Security Tests**: Authentication and authorization

### 11.3 Error Handling & Validation

**Centralized Error Handling:**

```typescript
// Custom error classes
export class ValidationError extends Error {
  constructor(
    message: string,
    public field?: string
  ) {
    super(message);
    this.name = 'ValidationError';
  }
}

export class AuthenticationError extends Error {
  constructor(message: string = 'Authentication failed') {
    super(message);
    this.name = 'AuthenticationError';
  }
}

export class AuthorizationError extends Error {
  constructor(message: string = 'Access denied') {
    super(message);
    this.name = 'AuthorizationError';
  }
}
```

**Input Validation with Zod:**

```typescript
import { z } from 'zod';

export const CreateDoctorSchema = z.object({
  name: z.string().min(2).max(100),
  whatsappNumber: z.string().regex(/^\+91[0-9]{10}$/),
  specialization: z.string().min(2).max(50),
  consultationFee: z.number().min(0).max(10000),
  advanceAmount: z.number().min(0).max(1000),
  dailyLimit: z.number().min(1).max(100),
});
```

### 11.4 Security Best Practices

**JWT Security:**

```typescript
// Secure JWT configuration
const jwtConfig = {
  accessTokenExpiry: '15m',
  refreshTokenExpiry: '7d',
  algorithm: 'HS256',
  issuer: 'pulseops-api',
  audience: 'pulseops-client',
};
```

**Data Sanitization:**

```typescript
// Input sanitization middleware
export const sanitizeInput = (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  // Remove HTML tags and sanitize inputs
  req.body = sanitizeHtml(req.body);
  next();
};
```

### 11.5 Performance Optimization

**Database Query Optimization:**

```typescript
// Efficient DynamoDB queries
class BaseRepository {
  protected async queryWithPagination(params: any, limit = 50) {
    const result = await this.dynamodb
      .query({
        ...params,
        Limit: limit,
      })
      .promise();

    return {
      items: result.Items,
      lastEvaluatedKey: result.LastEvaluatedKey,
      hasMore: !!result.LastEvaluatedKey,
    };
  }
}
```

**Caching Strategy:**

```typescript
// Redis caching for frequently accessed data
export class CacheService {
  private redis: Redis;

  async get<T>(key: string): Promise<T | null> {
    const cached = await this.redis.get(key);
    return cached ? JSON.parse(cached) : null;
  }

  async set(key: string, value: any, ttl = 3600): Promise<void> {
    await this.redis.setex(key, ttl, JSON.stringify(value));
  }
}
```

### 11.6 Monitoring & Logging

**Structured Logging:**

```typescript
import winston from 'winston';

export const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'app.log' }),
  ],
});
```

**Performance Monitoring:**

```typescript
// API response time tracking
export const responseTimeMiddleware = (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  const start = Date.now();

  res.on('finish', () => {
    const duration = Date.now() - start;
    logger.info('API Request', {
      method: req.method,
      url: req.url,
      statusCode: res.statusCode,
      duration,
      userId: req.user?.userId,
    });
  });

  next();
};
```

### 11.7 Environment Configuration

**Configuration Management:**

```typescript
// Environment-based configuration
export const config = {
  server: {
    port: parseInt(process.env.PORT || '3000'),
    environment: process.env.NODE_ENV || 'development',
  },
  database: {
    region: process.env.AWS_REGION || 'ap-south-1',
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
  },
  jwt: {
    secret: process.env.JWT_SECRET || 'fallback-secret',
    accessTokenExpiry: process.env.JWT_ACCESS_EXPIRY || '15m',
    refreshTokenExpiry: process.env.JWT_REFRESH_EXPIRY || '7d',
  },
  whatsapp: {
    apiUrl: process.env.WHATSAPP_API_URL,
    accessToken: process.env.WHATSAPP_ACCESS_TOKEN,
    webhookSecret: process.env.WHATSAPP_WEBHOOK_SECRET,
  },
};
```

### 11.8 Deployment Best Practices

**Docker Configuration:**

```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3000

USER node

CMD ["npm", "start"]
```

**Health Checks:**

```typescript
// Health check endpoint
export const healthCheck = async (req: Request, res: Response) => {
  try {
    // Check database connectivity
    await dynamodb.describeTable({ TableName: 'pulseops-clinics' }).promise();

    res.status(200).json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      services: {
        database: 'connected',
        whatsapp: 'connected',
      },
    });
  } catch (error) {
    res.status(503).json({
      status: 'unhealthy',
      error: error.message,
    });
  }
};
```

---

## 12. Reusable LLM Implementation Prompt

Copy and paste this prompt before any code implementation request:

```
You are implementing code for the PulseOps healthcare management system. Please follow these guidelines:

PROJECT CONTEXT:
- Healthcare system with strict privacy requirements
- Multi-tenant architecture with complete data isolation between clinics
- WhatsApp-based authentication with JWT tokens
- Real-time queue management for medical consultations
- Role-based access: Admin (full clinic access) and Doctor (own patients only)
- Node.js 18+ backend with TypeScript, Express.js, DynamoDB multi-table design, AWS Lambda deployment

MANDATORY REFERENCES (FOLLOW EXACTLY):
- Project Structure: Use the exact folder structure defined in section 5.1 of the README
- API Endpoints: Follow the exact API patterns, request/response formats, and status codes from section 6
- DynamoDB Schema: Use the exact table structures, indexes, and item formats from section 5.3
- Database Queries: Follow the query patterns and index usage from section 5.3.2
- Authentication Flow: Implement the exact WhatsApp OTP flow from section 5.4
- Entity Relationships: Follow the exact data model and isolation rules from section 2

ARCHITECTURE PATTERNS:
- Follow MVC pattern: Routes → Controllers → Services → Repositories
- Use dependency injection for all services and repositories
- Implement proper class-based structure with clear separation of concerns
- Use Zod schemas for request/response validation
- Follow single responsibility principle

CODE QUALITY STANDARDS:
- Use TypeScript with strict type checking throughout
- Follow TypeScript naming: PascalCase for classes, camelCase for methods/variables
- Maximum line length: 80 characters (Prettier formatting)
- Use single quotes for strings
- Implement proper JSDoc comments with comprehensive documentation
- Use absolute imports, avoid circular dependencies

ERROR HANDLING & VALIDATION:
- Implement centralized error handling with custom exception classes
- Map errors to appropriate HTTP status codes (400, 401, 403, 404, 409, 422, 500)
- Use consistent error response format across all APIs
- Implement proper input validation with meaningful error messages
- Log all errors with appropriate severity levels

CONFIGURATION & CONSTANTS:
- NEVER hardcode values - use constants from dedicated constants modules
- All config must be environment variable based
- Use enums for status values, roles, and fixed sets
- Create domain-specific constants files (authConstants, queueConstants, etc.)
- Use AWS Parameter Store/Secrets Manager for sensitive data

DATABASE & DATA ACCESS:
- Use simplified DynamoDB schema with direct attribute names (not PK/SK patterns)
- Implement proper repository interfaces with dependency injection
- Use appropriate indexes for efficient queries
- Implement proper pagination for large datasets
- Use batch operations where possible

SECURITY & AUTHENTICATION:
- Implement proper input validation and sanitization
- Use parameterized queries to prevent injection
- Validate permissions at both API and service levels
- Implement proper CORS configuration
- Use JWT tokens with proper expiration and refresh

TESTING REQUIREMENTS:
- Implement comprehensive unit tests for all business logic
- Use Jest framework with proper mocking
- Maintain minimum 80% code coverage
- Use descriptive test names that explain scenarios
- Implement proper test fixtures and setup/teardown

LOGGING & MONITORING:
- Use structured logging with consistent format
- Include relevant context in all log messages
- Use correlation IDs for request tracing
- Implement proper log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)

PERFORMANCE & SCALABILITY:
- Use async/await for I/O operations
- Optimize database queries and indexes
- Design for horizontal scaling

PRIVACY & DATA ISOLATION:
- Maintain strict data isolation between clinics
- Doctor can only access own patients and visit records
- Admin can access all clinic data but not other clinics
- Implement proper access control at all levels
- Log all data access for audit trails

API DESIGN:
- Follow RESTful conventions
- Use consistent request/response formats
- Implement proper pagination and filtering
- Use appropriate HTTP methods and status codes
- Include comprehensive request/response examples

FILE ORGANIZATION:
- Follow established project structure strictly
- Group related functionality in appropriate modules
- Use index.ts files to expose clean public APIs
- Implement proper namespacing to avoid conflicts

TYPESCRIPT SPECIFICS:
- Use strict TypeScript configuration
- Define comprehensive interfaces for all data structures
- Use union types for status values and enums
- Implement proper type guards for runtime type checking
- Use generic types where appropriate for reusability

EXPRESS.JS PATTERNS:
- Use middleware for cross-cutting concerns
- Implement proper error handling middleware
- Use route-specific middleware for validation
- Follow Express.js best practices for security

IMPLEMENTATION CHECKLIST:
□ Follow established patterns and conventions
□ Implement proper error handling and validation
□ Use centralized configuration and constants
□ Maintain data isolation and privacy boundaries
□ Follow API documentation format for consistency
□ Implement proper logging and monitoring
□ Ensure all code is production-ready with proper testing
□ Use TypeScript types and proper documentation
□ Follow security best practices
□ Optimize for performance and scalability

Please implement the requested changes following these guidelines. Do not provide complete code - focus on the specific implementation requested while maintaining consistency with the existing architecture.
```

**Usage**: Copy this prompt and add your specific request at the end, such as:

- "Create a new controller for X with methods Y and Z"
- "Implement the service layer for feature X"
- "Add repository methods for entity X"
- "Create API endpoints for functionality X"

This technical implementation provides a complete foundation for building the PulseOps system with proper patient tracking, hierarchy, access controls, and scalable architecture using Node.js, Express.js, and TypeScript.
