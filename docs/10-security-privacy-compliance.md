# Security, Privacy, and Compliance

For a medical system, security and privacy are not just features; they are fundamental requirements. This document outlines the key principles and strategies for ensuring the system is secure and compliant with regulations like HIPAA (Health Insurance Portability and Accountability Act).

## 1. The HIPAA Mindset

The core principle of HIPAA is the concept of **Minimum Necessary Use**. This means that we should only access, use, and disclose Protected Health Information (PHI) to the minimum extent necessary to accomplish the intended purpose.

## 2. Data Protection

### 2.1. Encryption in Transit

-   **Requirement:** All communication between clients and servers, and between services, must be encrypted.
-   **Implementation:**
    -   **TLS Everywhere:** Enforce Transport Layer Security (TLS) 1.2 or higher for all API endpoints and internal service-to-service communication.
    -   **API Gateway:** The API Gateway should terminate TLS for external traffic and can re-encrypt traffic to internal services.

### 2.2. Encryption at Rest

-   **Requirement:** All data stored in databases, caches, and file stores must be encrypted.
-   **Implementation:**
    -   **Database Encryption:** Use the built-in encryption features of our database (e.g., PostgreSQL's `pgcrypto` or Transparent Data Encryption (TDE)).
    -   **Cloud Provider KMS:** Leverage a Key Management Service (KMS) from our cloud provider (e.g., AWS KMS, Google Cloud KMS) to manage encryption keys. This prevents even the cloud provider from accessing our data.

## 3. Access Control

### 3.1. Role-Based Access Control (RBAC)

-   **Requirement:** Users should only have access to the data and functionality they need to perform their jobs.
-   **Implementation:**
    -   **Roles:** Define roles with specific permissions (e.g., `PATIENT`, `SCHEDULER`, `DOCTOR`, `ADMIN`).
    -   **Permissions:** A `PATIENT` can only view their own appointments. A `SCHEDULER` can view appointments for their assigned clinic. An `ADMIN` can manage provider schedules.

### 3.2. Attribute-Based Access Control (ABAC)

-   **Requirement:** For more granular control, access can be based on attributes of the user, resource, or environment.
-   **Example:** A doctor can only access the full medical record of a patient if they have an active appointment with that patient in the next 24 hours.

## 4. Auditing and Monitoring

### 4.1. Immutable Audit Logs

-   **Requirement:** We must maintain a detailed, immutable audit trail of all actions performed in the system, especially any access to PHI.
-   **Implementation:**
    -   **Audit Service:** As described in the Core Architecture, a dedicated Audit Service consumes events from the event bus and writes them to an immutable log.
    -   **Log Content:** The audit log should capture the **who, what, when, and where** of every action (e.g., `user_id`, `action`, `timestamp`, `ip_address`).

### 4.2. PHI in Logs and Events

-   **Requirement:** PHI should be minimized in logs and events to reduce the "blast radius" of a security breach.
-   **Implementation:**
    -   **Tokenization:** Instead of logging raw PHI, log internal identifiers or "tokens." For example, log `patient_id: 'pat_123'` instead of the patient's name and date of birth.
    -   **References over Payloads:** When publishing events, it's often better to publish a reference to the data (e.g., `appointment_id`) rather than the full appointment details. Downstream services can then query for the details they need, subject to their own access controls.

## 5. Data Retention and Deletion

-   **Requirement:** We must have clear policies for data retention and deletion, in line with legal and regulatory requirements.
-   **Implementation:**
    -   **Retention Policies:** Define how long different types of data are kept (e.g., appointment data for 7 years).
    -   **Deletion Workflows:** Implement a secure and verifiable process for deleting data when a patient requests it (the "right to be forgotten") or when it reaches the end of its retention period. This can be a complex, asynchronous process.

## 6. Secure Development Lifecycle

-   **Static Analysis (SAST):** Integrate static code analysis tools into the CI/CD pipeline to scan for security vulnerabilities.
-   **Dependency Scanning:** Continuously scan third-party libraries for known vulnerabilities.
-   **Penetration Testing:** Regularly conduct penetration tests to identify and fix security weaknesses.

## Next Steps

- **[11-reliability-observability.md](./11-reliability-observability.md):** How we ensure the system is reliable and can be effectively monitored.