# Correctness & Concurrency

This is arguably the most critical aspect of the system design. A failure to ensure correctness—specifically, preventing double-booking—would render the entire system untrustworthy. This document explores the challenges of concurrency and the strategies to address them.

## 1. The Core Problem: Race Conditions

The classic race condition in this system is two users trying to book the same appointment slot at the same time.

```
User A checks availability -> Slot 10:00 AM is open
User B checks availability -> Slot 10:00 AM is open

User A sends booking request for 10:00 AM
User B sends booking request for 10:00 AM

System processes User A's request -> Books slot
System processes User B's request -> Also books slot (ERROR: double-booking)
```

To prevent this, we need a mechanism to ensure that the check for availability and the booking of the slot are an **atomic operation**.

## 2. Strategy 1: Pessimistic Locking (Database Transactions)

The most robust way to ensure correctness is to use the features of our relational database (PostgreSQL). This approach is often called "pessimistic locking" because we assume that conflicts are likely and we lock resources to prevent them.

### 2.1. The Process

1.  **Begin Transaction:** Start a database transaction.
2.  **Acquire Lock:** Acquire a lock on the resource that represents the slot being booked. This could be a row in a `slots` table, or a lock on the `provider` for a given time range. A common approach is to use `SELECT ... FOR UPDATE`.
3.  **Check Availability:** Within the transaction, re-check if the slot is still available.
4.  **Create Appointment:** If the slot is available, create the appointment record.
5.  **Commit Transaction:** Commit the transaction. This releases the lock.

If another request comes in for the same slot while the transaction is in progress, it will be blocked at step 2, waiting for the first transaction to complete.

### 2.2. Example (Simplified SQL)

```sql
BEGIN;

-- Acquire a lock on the provider's schedule for the specific time.
-- This will block if another transaction has a lock on this row.
SELECT * FROM provider_schedules
WHERE provider_id = 'prov_123'
AND '2024-10-28T10:00:00Z' >= start_time
AND '2024-10-28T10:30:00Z' <= end_time
FOR UPDATE;

-- Re-check for conflicting appointments within the transaction
SELECT COUNT(*) FROM appointments
WHERE provider_id = 'prov_123'
AND status != 'CANCELLED'
AND (start_time, end_time) OVERLAPS ('2024-10-28T10:00:00Z', '2024-10-28T10:30:00Z');

-- If the count is 0, we can proceed
INSERT INTO appointments (provider_id, patient_id, start_time, end_time, status)
VALUES ('prov_123', 'pat_456', '2024-10-28T10:00:00Z', '2024-10-28T10:30:00Z', 'CONFIRMED');

COMMIT;
```

### 2.3. Tradeoffs

-   **Pros:** Guarantees strong consistency. The database handles the complexity of locking.
-   **Cons:** Can reduce throughput, as transactions are serialized. Long-running transactions can be problematic. The locking strategy needs to be chosen carefully to avoid deadlocks.

## 3. Strategy 2: Optimistic Locking (Check-and-Set)

An alternative approach is "optimistic locking," where we assume that conflicts are rare.

### 3.1. The Process

1.  When a client reads data, they also get a "version" number (e.g., an `updated_at` timestamp or a version counter).
2.  When the client writes data back, they include the version number.
3.  The system checks if the version number has changed. If it has, the transaction is aborted, and the client is asked to retry.

This is less common for the core booking flow because we want to guarantee the booking if possible, but it can be useful for other parts of the system (e.g., updating a patient's contact information).

## 4. Short-Lived "Holds" (A Hybrid Approach)

A common pattern is to use a hybrid approach that provides a better user experience.

1.  **Create a Hold:** When a user selects a slot, the system creates a short-lived "hold" on that slot in a fast, in-memory store like Redis. The hold has a short TTL (e.g., 5 minutes).
2.  **Pass Hold ID to Client:** The client receives a `hold_id`.
3.  **Confirm Booking:** The user then proceeds to a confirmation screen. When they confirm, they send the `hold_id` to the booking service.
4.  **Atomic Booking:** The booking service then uses the `hold_id` to perform the atomic booking in the database, as described in Strategy 1.

### 4.1. Benefits

-   **Good UX:** Prevents another user from "sniping" the slot while the first user is entering their information.
-   **Reduces DB Load:** The database is only hit for the final, confirmed booking, not for every click on a time slot.

## 5. Idempotency

Network clients will inevitably retry requests. If a client retries a booking request, we must not create a second appointment.

-   **Mechanism:** The client should generate a unique `Idempotency-Key` (e.g., a UUID) and send it in the header of every `POST` request.
-   **Server-Side:** The server should store the `Idempotency-Key` of recently processed requests. If a request comes in with a key that has already been processed, the server can simply return the original response without re-processing the request.

## Next Steps

- **[07-data-model-postgres.md](./07-data-model-postgres.md):** The detailed data model that supports these concurrency control mechanisms.