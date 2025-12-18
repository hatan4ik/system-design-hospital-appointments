# "Golden Answer" Interview Outline

This document provides a more detailed, scripted outline for delivering a FAANG/MANGA-caliber answer in a system design interview.

### 1. Requirements & Assumptions (The "Discovery" Phase)

-   **Your Opening:** "This is a great, classic system design problem. To start, I'd like to clarify the scope. My assumption is we're designing a patient-facing system for a mid-sized hospital network to allow patients to find doctors and book appointments. Is that correct?"
-   **Core User Stories:**
    -   Patient: Search providers, view availability, book/cancel appointments.
    -   Scheduler: Manage appointments on behalf of patients.
-   **Key Constraints to State Aloud:**
    -   "The most critical requirement is **correctness**. We absolutely cannot double-book a provider."
    -   "Read availability will be a very frequent operation, so we need to make that fast."
    -   "Since this is medical data, we must have a **HIPAA mindset** from the start."

### 2. Core APIs (The "Contract")

-   **Your Lead-in:** "Before we dive into the implementation, let's define the API contract. I'm thinking of a standard REST API."
-   **Key Endpoints to Whiteboard:**
    -   `GET /providers?specialty=...`: To find a doctor.
    -   `GET /availability?provider_id=...`: To see open slots.
    -   `POST /appointments`: To book a slot.
-   **Critical Detail to Mention:**
    -   "The `POST /appointments` endpoint **must be idempotent**. The client will send an `Idempotency-Key` header to prevent accidental duplicate bookings on retries."

### 3. Data Model (The "Blueprint")

-   **Your Lead-in:** "This API will be backed by a relational database like PostgreSQL because we need strong consistency for our booking transactions."
-   **Core Tables to Whiteboard:**
    -   `patients`, `providers`, `appointments`
    -   `provider_schedules`: The source of truth for a doctor's working hours.
-   **Key Index to Mention:**
    -   "We'll need a compound index on `(provider_id, start_time)` in the `appointments` table to quickly find a provider's bookings."

### 4. Correctness (The "Make-or-Break" Deep Dive)

-   **Your Lead-in:** "Now let's tackle the hardest part: ensuring no double-bookings, even under high concurrency. My approach is to use database-level locking."
-   **The Core Logic to Explain:**
    1.  "Begin a `TRANSACTION`."
    2.  "Acquire a lock on the provider's schedule for the target time slot using `SELECT ... FOR UPDATE`. This blocks other concurrent transactions for the same provider."
    3.  "Re-verify that the slot is still available."
    4.  "Insert the new appointment."
    5.  "`COMMIT` the transaction, which releases the lock."
-   **Why this is a good answer:** It shows you can go deep on the most critical part of the problem and that you have a robust solution.

### 5. Availability & Caching (The "Performance" Story)

-   **Your Lead-in:** "The booking process is now correct, but querying for availability could be slow if we calculate it from scratch every time. We need to make reads fast."
-   **Two-Pronged Strategy:**
    -   **Pre-computation:** "I would have a background job that pre-computes available slots for each provider and stores them in a separate `appointment_slots` table. The API then becomes a simple, fast read from this table."
    -   **Caching:** "The results from the `appointment_slots` table will be heavily cached in Redis for millisecond-level read latency."

### 6. Asynchronous Workflows (The "Decoupling" Story)

-   **Your Lead-in:** "Once an appointment is booked, we need to send confirmations and reminders. We don't want the user to wait for this, so we'll do it asynchronously."
-   **Event-Driven Architecture:**
    -   "The Appointment Service will publish an `appointment_booked` event to a message bus like Kafka."
    -   "A `NotificationService` will consume this event and send the email/SMS."
    -   "A `WaitlistService` can consume `appointment_cancelled` events to find and offer newly open slots."

### 7. Security & Auditing (The "Trust & Safety" Story)

-   **Your Lead-in:** "Given the sensitivity of this data, we need to build a secure and compliant system."
-   **Key Pillars:**
    -   **Encryption:** "TLS everywhere for data in transit, and encryption at rest for our databases, managed by a KMS."
    -   **Access Control:** "Strict Role-Based Access Control (RBAC) for different user types."
    -   **Auditing:** "An immutable audit trail that logs every single access to patient data."

### 8. Scalability & Partitioning (The "Future-Proofing" Story)

-   **Your Lead-in:** "As our hospital network grows, we'll need to scale our database. My plan would be to partition, or shard, the database."
-   **The Strategy:**
    -   "We can shard by `location_id`. This is a natural partition key because most queries are isolated to a single clinic or hospital."
    -   "We'd introduce a routing layer in our application that directs queries to the correct shard based on the `location_id`."

### 9. Tradeoffs & Wrap-Up

-   **Summarize:** "So, to quickly summarize, we've built a correct, scalable, and secure appointment booking system using a microservices architecture, a relational database with transactional locking, and an event-driven approach for asynchronous tasks."
-   **State a Tradeoff:** "One key tradeoff I made was choosing strong consistency for bookings over raw performance. For a medical system, I believe this is the correct choice."
-   **Next Steps:** "If I had more time, I'd love to discuss how to handle multi-resource scheduling or how we could apply machine learning to predict no-shows."