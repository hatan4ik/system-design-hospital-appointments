# Follow-Up Questions & Answer Sketches

This document provides a list of common follow-up questions that an interviewer might ask, along with sketches of how to answer them.

### 1. "You mentioned using a transaction to prevent double-booking. What are the potential problems with that approach, and how would you mitigate them?"

-   **Answer Sketch:**
    -   **Problem 1: Performance/Throughput:** "That's a great question. The main tradeoff with pessimistic locking is performance. Because we are serializing access to a provider's schedule, we can't process multiple bookings for the same provider in parallel. This can become a bottleneck."
    -   **Mitigation 1: Fine-Grained Locking:** "I would mitigate this by making the lock as fine-grained as possible. Instead of locking the entire provider, we could lock a specific time range or even a pre-defined slot. This reduces the window of contention."
    -   **Problem 2: Deadlocks:** "Another potential issue is deadlocks, where two transactions are waiting for each other to release locks. For example, if we are booking a multi-resource appointment and Transaction A locks the Doctor while Transaction B locks the Room, and then A tries to get the Room and B tries to get the Doctor."
    -   **Mitigation 2: Consistent Lock Ordering:** "The standard way to prevent deadlocks is to always acquire locks in a consistent order. For example, we could decide to always lock resources in alphabetical order of their type (e.g., 'doctor' then 'room')."

### 2. "How would you handle appointments that require multiple resources, like a specific doctor, a specific room, and a specific piece of equipment?"

-   **Answer Sketch:**
    -   **Option A: The Atomic Transaction (Preferred):** "The ideal way to handle this is to extend our existing transaction. We would acquire locks on all three resources (doctor, room, equipment) within the same database transaction. This guarantees that we either book all three successfully, or none at all, which is the safest approach."
    -   **Option B: Sagas (More Complex):** "If the resources were managed by different services that didn't share a database, we couldn't use a single transaction. In that case, we'd need to use a Saga pattern. We would have a series of local transactions (book doctor, then book room, then book equipment). If any step fails, we would have to run a series of compensating transactions to roll back the previous steps. This is much more complex to get right, so I would only use it if the system's architecture forced me to."

### 3. "How would you design the system to minimize patient no-shows?"

-   **Answer Sketch:**
    -   **Proactive Notifications:** "This is a great business problem to solve. I'd start with a multi-pronged notification strategy. In addition to the standard 24-hour reminder, the confirmation email/SMS would have prominent 'Confirm' and 'Cancel' links."
    -   **Automated Re-booking:** "If a patient cancels, we can automatically trigger our waitlist system to offer that slot to another patient. This maximizes provider utilization."
    -   **Analytics & Machine Learning:** "Longer-term, we could build a predictive model. We would analyze historical data to identify factors that correlate with no-shows (e.g., time of day, visit type, patient history). We could then use this model to, for example, send an extra reminder to patients who are at high risk of no-showing."

### 4. "You mentioned pre-computing availability. What happens if a doctor's schedule changes unexpectedly? How do you handle cache invalidation?"

-   **Answer Sketch:**
    -   **Event-Driven Invalidation:** "This is where an event-driven architecture really shines. When a scheduler updates a provider's schedule, the Provider Schedule Service would publish a `provider_schedule_changed` event."
    -   **Asynchronous Re-computation:** "The Availability Service would consume this event. This would trigger an asynchronous job to re-compute the availability for that specific provider and update the `appointment_slots` table. The cache for that provider would also be purged."
    -   **Stale-While-Revalidate:** "To provide a seamless user experience, we can use a 'stale-while-revalidate' caching strategy. When a user requests availability, we can serve the slightly stale data from the cache while we asynchronously re-compute the fresh data in the background. The user's next request will then get the fresh data."

### 5. "How would you handle a failure in a critical third-party integration, like the insurance verification service?"

-   **Answer Sketch:**
    -   **Circuit Breakers:** "First, the call to the external service must be wrapped in a circuit breaker. If the insurance service is down, we don't want to bring our own service down with it. The circuit breaker would open, and we'd fail fast."
    -   **Graceful Degradation:** "We need to decide how to degrade gracefully. For insurance verification, we could potentially allow the booking to proceed but flag it as 'pending_insurance_verification'. This would allow the user to complete the core task of booking their appointment."
    -   **Asynchronous Retries & DLQ:** "A record of the failed verification would be placed in a queue for asynchronous retries. We would try a few more times, and if it still fails, the message would be moved to a Dead-Letter Queue (DLQ). An operations team would then be alerted to manually investigate the issue."