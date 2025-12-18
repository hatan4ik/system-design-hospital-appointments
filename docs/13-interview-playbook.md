# The Interview Playbook

This document provides a structured approach for tackling the "Design a hospital appointment system" question in a 60-minute system design interview. The key is to be proactive, drive the conversation, and demonstrate your ability to think about a problem at all levels, from the high-level requirements down to the low-level details of correctness and scalability.

## 1. The First 5 Minutes: Requirements & Assumptions (0-5 min)

**Goal:** Scope the problem and demonstrate that you are a product-minded engineer.

**Your Script:**
"This is a great question. It's a complex system, so to make sure I'm on the right track, I'd like to start by clarifying the requirements. My initial thoughts are that we'll need to support a few key user stories..."

**Key Talking Points:**
-   **User Stories:**
    -   Patients can search for doctors, view availability, and book/cancel appointments.
    -   Schedulers can manage appointments on behalf of patients.
    -   Doctors can manage their own schedules.
-   **Core Functional Requirements:** Booking, cancellation, reminders.
-   **Key Non-Functional Requirements:** Correctness (no double-booking!), reliability, and security (HIPAA).

**Questions to Ask Your Interviewer:**
-   "Is this for a single hospital or a network of clinics?"
-   "What's the expected scale? A few hundred providers, or thousands?"
-   "Are we focusing on the patient-facing booking flow, or are the internal admin tools just as important?"

## 2. The Next 5 Minutes: High-Level Design (5-10 min)

**Goal:** Sketch out the big picture and the initial data model.

**Your Script:**
"Okay, that gives me a good starting point. I'm thinking of a microservices-based architecture. At a high level, we'll have a few key services: an Appointment Service for the core booking logic, an Availability Service to handle the read-heavy task of finding open slots, and a Notification Service for sending reminders. For the data model, we'll have entities like `Patient`, `Provider`, and `Appointment`..."

**Key Talking Points:**
-   **Services:** API Gateway, Appointment Service, Availability Service, Notification Service.
-   **Data Stores:** PostgreSQL for transactional data, Redis for caching.
-   **Data Model:** Draw a simple ERD on the whiteboard with the core entities.

## 3. The Deep Dive on Correctness (10-25 min)

**Goal:** This is the make-or-break part of the interview. Prove that you understand the hardest part of the problem.

**Your Script:**
"The most critical requirement for this system is correctness. If we double-book a doctor, the system is a failure. So, I'd like to spend a good amount of time here. The main challenge is handling concurrent requests for the same slot. My preferred approach is to use pessimistic locking within a database transaction..."

**Key Talking Points:**
-   **Race Conditions:** Clearly explain the double-booking race condition.
-   **Pessimistic Locking:** Walk through the `SELECT ... FOR UPDATE` flow. Explain why this guarantees consistency.
-   **Idempotency:** Discuss the need for `Idempotency-Key` to handle client retries.
-   **Holds (Optional but good):** Mention the concept of short-lived holds in Redis to improve the user experience.

## 4. Scaling the System (25-40 min)

**Goal:** Show that you can think about how the system will evolve and handle massive load.

**Your Script:**
"Now that we have a correct system, let's talk about how to scale it. This system is very read-heavy, so my primary focus would be on scaling our read workloads. The first step is caching. For the Availability Service, we can pre-compute and cache the available slots. For the database, we can use read replicas..."

**Key Talking Points:**
-   **Read Replicas:** Explain how they work and why they are a good fit here.
-   **Caching:** Discuss caching strategies for the Availability Service.
-   **Partitioning/Sharding:** Talk about sharding the database by `location_id` or `clinic_id` as a long-term scaling strategy.
-   **Hot Spots:** Mention the "hot provider" problem and how you might handle it (e.g., with request queues).

## 5. The "ilities" (40-55 min)

**Goal:** Round out your answer by touching on other important non-functional requirements.

**Your Script:**
"Finally, I'd like to touch on a few other important aspects of the system. For **reliability**, we need to define SLOs for our key services and use patterns like circuit breakers. For **observability**, we need the three pillars: logs, metrics, and traces. And for **security**, especially with HIPAA, we need to think about encryption, access control, and auditing..."

**Key Talking Points:**
-   **Reliability:** SLOs, circuit breakers, DLQs.
-   **Observability:** Logs, metrics (especially queue lag, lock contention), and tracing (correlation IDs).
-   **Security & Compliance:** Encryption at rest and in transit, RBAC, immutable audit logs.

## 6. The Wrap-Up (55-60 min)

**Goal:** Summarize your design and discuss potential future improvements.

**Your Script:**
"So, to summarize, we've designed a microservices-based system with a focus on correctness, using database transactions to prevent double-booking. We've scaled it for read-heavy traffic using caching and read replicas, and we have a plan for sharding in the future. We've also considered reliability, observability, and security.

If I had more time, I would explore the waitlist feature in more detail, and I'd also think about how to handle multi-resource scheduling, like booking a room and a piece of equipment along with the doctor."

**Key Talking Points:**
-   Briefly summarize the key decisions in your design.
-   Identify the trade-offs you made (e.g., "I chose strong consistency for booking, which might reduce throughput, but I think that's the right trade-off for this system.").
-   Mention a few future improvements to show that you are thinking ahead.