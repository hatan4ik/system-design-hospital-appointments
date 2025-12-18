# Reliability & Observability

Reliability and observability are not "add-on" features; they must be designed into the system from the beginning. This document outlines the key strategies for ensuring our system is reliable, and that we have the tools to understand its behavior in production.

## 1. Defining Reliability: SLOs and SLIs

First, we must define what "reliable" means for our system. We do this by defining Service Level Objectives (SLOs) based on Service Level Indicators (SLIs).

-   **SLI (Service Level Indicator):** A quantitative measure of some aspect of the service (e.g., latency, error rate).
-   **SLO (Service Level Objective):** A target value or range for an SLI, agreed upon by the stakeholders.

### Example SLOs

-   **Booking Success Rate:**
    -   **SLI:** The percentage of `POST /appointments` requests that return a successful (2xx) response.
    -   **SLO:** 99.9% of booking requests will be successful.

-   **Availability Latency:**
    -   **SLI:** The 95th percentile (p95) latency of `GET /availability` requests.
    -   **SLO:** p95 latency for availability requests will be less than 150ms.

-   **Reminder Timeliness:**
    -   **SLI:** The percentage of appointment reminders that are delivered within 2 minutes of their scheduled time.
    -   **SLO:** 99% of reminders will be delivered on time.

## 2. Reliability Patterns

We can use several architectural patterns to improve the reliability of our system.

### 2.1. Circuit Breakers

-   **Problem:** The system integrates with external third-party services (e.g., insurance providers, EHR systems). If one of these services is slow or unavailable, it could cause cascading failures in our system.
-   **Solution:** A circuit breaker is a component that monitors for failures in calls to a remote service. If the failure rate exceeds a threshold, the circuit breaker "opens" and immediately fails any further calls to that service, preventing our system from waiting on a failing dependency.

### 2.2. Dead-Letter Queues (DLQs)

-   **Problem:** Our asynchronous services (e.g., Notification Service) consume events from a message bus. What happens if an event is malformed or cannot be processed?
-   **Solution:** After a few failed processing attempts, the message is moved to a Dead-Letter Queue (DLQ). This prevents a single bad message from blocking the entire queue. Engineers can then inspect the DLQ to diagnose the problem.

### 2.3. Redundancy and Failover

-   **Problem:** A single instance of a service or database could fail.
-   **Solution:** Run multiple instances of each service behind a load balancer. For the database, use a primary/replica setup with automatic failover.

## 3. The Three Pillars of Observability

Observability is about being able to ask arbitrary questions about your system's behavior without having to ship new code. It is typically broken down into three pillars:

### 3.1. Logs

-   **Purpose:** Detailed, timestamped records of events that occurred in the system.
-   **Implementation:**
    -   **Structured Logging:** All logs should be in a structured format like JSON, so they can be easily searched and filtered.
    -   **Centralized Logging:** All logs from all services should be shipped to a centralized logging platform (e.g., Elasticsearch, Splunk).

### 3.2. Metrics

-   **Purpose:** Aggregated, numerical data about the performance of the system over time.
-   **Implementation:**
    -   **Key Metrics:** We should track key metrics for each service, such as:
        -   **Request Rate, Error Rate, Duration (RED):** The "golden signals" for any service.
        -   **Concurrency & Lock Contention:** For the Appointment Service, how many transactions are waiting for locks?
        -   **Queue Lag:** For asynchronous services, how far behind are they in processing events?
    -   **Dashboarding:** Metrics should be visualized in dashboards (e.g., in Grafana) to provide an at-a-glance view of system health.

### 3.3. Tracing

-   **Purpose:** The ability to follow a single request as it flows through all the services in our microservices architecture.
-   **Implementation:**
    -   **Correlation IDs:** When a request enters the system at the API Gateway, it is assigned a unique `correlation_id`. This ID is passed in the headers of all subsequent calls to downstream services.
    -   **Distributed Tracing:** We can use a distributed tracing system (e.g., Jaeger, OpenTelemetry) to get a rich visualization of the entire request lifecycle, showing how long it spent in each service. This is invaluable for debugging and performance analysis.

## Next Steps

- **[12-scalability-partitioning.md](./12-scalability-partitioning.md):** How we can scale the system to handle massive load.