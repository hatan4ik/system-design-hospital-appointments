# Capacity Estimation

A critical step in system design is to perform a "back-of-the-envelope" capacity estimation. This helps to inform architectural decisions, technology choices, and cost projections.

## 1. Assumptions

Let's assume we are designing a system for a mid-sized healthcare network.

-   **Providers:** 3,000 healthcare providers (doctors, specialists, etc.).
-   **Daily Appointments:** An average of 50,000 appointments per day.
-   **Peak Traffic:** Traffic is not evenly distributed. We'll assume a 10x peak during business hours.
-   **Working Hours:** 8 hours per day (e.g., 9 AM to 5 PM).

## 2. Traffic Estimation (QPS)

### 2.1. Appointment Booking (Writes)

-   **Average QPS:** 50,000 appointments / (8 hours * 3600 s/hour) ≈ 1.7 QPS.
-   **Peak QPS:** 1.7 QPS * 10 = 17 QPS.
-   **Conclusion:** This is a relatively low write volume. However, these are critical, transactional operations that must be handled with strong consistency.

### 2.2. Availability Search (Reads)

-   **Assumption:** We'll assume a 20:1 read-to-write ratio. For every appointment booked, a user might check availability 20 times.
-   **Average QPS:** 1.7 QPS (writes) * 20 = 34 QPS.
-   **Peak QPS:** 34 QPS * 10 = 340 QPS.
-   **Further Consideration:** In a real-world scenario, this could be much higher, especially if the UI aggressively pre-fetches availability. It's not uncommon for this to be in the range of **1,000-5,000 QPS** during peak times.
-   **Conclusion:** The availability service must be optimized for high read throughput. Caching and pre-computation will be essential.

### 2.3. Notifications

-   **Volume:** For each appointment, we send at least two notifications (a confirmation and a reminder).
-   **Total Notifications:** 50,000 appointments/day * 2 = 100,000 notifications/day.
-   **Conclusion:** This is a significant volume of outbound messages. The notification system should be asynchronous and decoupled from the core booking flow.

## 3. Storage Estimation

### 3.1. Appointments

-   **Appointments per Year:** 50,000 appointments/day * 365 days/year ≈ 18.25 million appointments/year.
-   **Data per Appointment:** Let's assume each appointment record is about 2 KB (including patient info, provider info, timestamps, etc.).
-   **Annual Storage:** 18.25 million * 2 KB ≈ 36.5 GB/year.
-   **Conclusion:** The storage requirement for appointment data itself is not enormous. A standard PostgreSQL database can handle this for many years.

### 3.2. Audit Events

-   **Assumption:** For compliance, we need to log every significant action (view, create, update, delete). We'll assume an average of 10 audit events per appointment.
-   **Events per Year:** 18.25 million appointments * 10 events/appointment = 182.5 million events/year.
-   **Data per Event:** Let's assume each event is 1 KB.
-   **Annual Storage:** 182.5 million * 1 KB ≈ 182.5 GB/year.
-   **Conclusion:** The audit log will be significantly larger than the appointment data. This reinforces the need for a separate, scalable event store or logging system.

## 4. High-Level System Implications

-   **Read-Heavy Workload:** The system is heavily skewed towards reads, especially for the availability service. This points towards a design with aggressive caching (e.g., Redis) and potentially pre-computing availability slots.
-   **Correctness over Speed (for writes):** The booking process is not high-QPS, but it is critical. The architecture must prioritize correctness and consistency, which justifies the use of a transactional database like PostgreSQL.
-   **Asynchronous Communication:** The high volume of notifications and audit events suggests an event-driven architecture with a message bus (e.g., Kafka) to decouple these concerns from the synchronous booking flow.

## Next Steps

- **[03-domain-model.md](./03-domain-model.md):** A look at the core entities and their relationships in the system.