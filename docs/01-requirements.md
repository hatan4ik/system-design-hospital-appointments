# Requirements

This document outlines the functional and non-functional requirements for the Hospital Appointment & Scheduling System. These requirements are defined in a way that is typical for a FAANG/MANGA-level system design interview.

## 1. User Stories & Functional Requirements

### 1.1. Patient (MVP)

-   **As a patient, I want to search for providers** based on specialty (e.g., Cardiology), location, and the type of visit I need, so that I can find a suitable doctor.
-   **As a patient, I want to view the available appointment slots** for a specific provider or an entire clinic, so that I can choose a time that works for me.
-   **As a patient, I want to book an appointment**, providing my personal information and the reason for my visit, so that I can secure a time slot.
-   **As a patient, I want to receive a confirmation notification** (e.g., email, SMS) immediately after booking my appointment, so that I have a record of it.
-   **As a patient, I want to receive a reminder notification** 24-48 hours before my appointment, so that I don't forget it.
-   **As a patient, I want to be able to cancel or reschedule my appointment**, so that I can manage my schedule.

### 1.2. Hospital Staff (Scheduler)

-   **As a scheduler, I want to perform all the same actions as a patient** on their behalf, so that I can assist patients who call in or are in the hospital.
-   **As a scheduler, I want to manage provider schedules**, including adding, removing, and modifying their availability (e.g., for vacations or emergencies), so that the system is always up-to-date.
-   **As a scheduler, I want to override booking rules** in exceptional cases (e.g., double-booking an emergency patient with a doctor's approval), so that I can handle real-world exceptions.

### 1.3. Differentiators & Future Features

-   **Waitlists:** If a provider is fully booked, a patient can join a waitlist and be automatically notified if a slot opens up.
-   **Multi-Resource Appointments:** Some appointments may require multiple resources (e.g., a specific room, a piece of equipment, and a technician). The system should be able to coordinate the scheduling of all required resources.
-   **Recurring Appointments:** The system should support booking recurring appointments (e.g., for physical therapy).

## 2. Non-Functional Requirements

-   **Correctness & Consistency:**
    -   The system must guarantee **strong consistency** for all booking-related operations. Double-booking is the primary failure mode to avoid.
    -   The system must be the single source of truth for all appointments.

-   **Performance & Latency:**
    -   **Availability Reads:** Reading provider availability should be very fast (e.g., <100ms p99 latency), as this is a high-volume, read-heavy operation.
    -   **Booking Writes:** Writing an appointment can be slower (e.g., <500ms p99 latency), but must be reliable.

-   **Reliability & Availability:**
    -   The system should be highly available (e.g., 99.99% uptime), especially for the patient-facing booking and availability services.
    -   In the event of a partial system failure, the system should degrade gracefully (e.g., reads of availability might still be possible even if new bookings are temporarily disabled).

-   **Security & Privacy:**
    -   The system must be compliant with **HIPAA** in the US and GDPR in Europe. All Protected Health Information (PHI) and Personally Identifiable Information (PII) must be encrypted at rest and in transit.
    -   The system must have a robust audit trail of all actions performed, especially those related to PHI.

-   **Scalability:**
    -   The system should be able to scale to support a large number of hospitals, providers, and patients.
    -   The architecture should be able to handle spiky traffic patterns (e.g., when a new set of appointments becomes available).

-   **Observability:**
    -   The system must be fully observable, with detailed logging, metrics, and tracing.
    -   It should be possible to trace a single booking request from the initial API call through all the microservices and data stores.

-   **Extensibility:**
    -   The architecture should be designed to be extensible, allowing for the addition of new features, integrations, and even new "tenants" (e.g., hospital chains).

## 3. Clarifying Questions to Ask in an Interview

-   **What are the primary channels?** Is this for a patient-facing mobile app, a web portal, or an internal tool for call center staff?
-   **What are the different types of appointments and their durations?** Are there standard buffers required between appointments?
-   **Do appointments ever require multiple resources?** (e.g., a specific room, a piece of equipment, and a technician).
-   **What is the expected load?** What is the peak QPS for reads (availability) and writes (bookings)? How many providers and patients will the system support?
-   **What are the regulatory constraints?** Is this for a specific region with laws like HIPAA or GDPR?

## Next Steps

- **[02-capacity-estimation.md](./02-capacity-estimation.md):** A quantitative analysis of the system's capacity requirements.