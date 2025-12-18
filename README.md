# System Design: Hospital Appointment & Scheduling System

This repository is a comprehensive, FAANG/MANGA-grade training resource for the system design interview question: **"Design a hospital appointment and scheduling system."**

It provides a complete package for understanding the complexities of such a system, including in-depth documentation, architectural diagrams, and a runnable local demonstration environment.

## Getting Started: Running the Local Demo

To get a feel for the system in action, you can run the services locally using Docker.

1.  **Navigate to the local demo directory:**
    ```bash
    cd labs/01-local-demo
    ```

2.  **Start the services:**
    ```bash
    docker compose up --build
    ```

3.  **Check the health of the services:**
    In a separate terminal, you can send a request to the API gateway to check the health of the running services:
    ```bash
    curl -s localhost:8080/healthz | jq
    ```

## System Design Documentation

For those preparing for a system design interview or seeking to understand the system in depth, we recommend reading the documentation in the following order. This path is designed to build your knowledge from the ground up, from requirements to advanced architectural considerations.

### Part 1: System Fundamentals
1.  **[docs/00-overview.md](docs/00-overview.md):** High-level overview, goals, and core components.
2.  **[docs/01-requirements.md](docs/01-requirements.md):** Functional and non-functional requirements.
3.  **[docs/02-capacity-estimation.md](docs/02-capacity-estimation.md):** Back-of-the-envelope calculations for scale.
4.  **[docs/03-domain-model.md](docs/03-domain-model.md):** Core entities and their relationships.
5.  **[docs/04-api-design.md](docs/04-api-design.md):** API design for the services.

### Part 2: Architecture & Implementation
6.  **[docs/05-core-architecture.md](docs/05-core-architecture.md):** Microservices architecture, services, and data stores.
7.  **[diagrams/01-high-level.mmd](diagrams/01-high-level.mmd):** High-level architecture diagram.
8.  **[docs/07-data-model-postgres.md](docs/07-data-model-postgres.md):** Detailed PostgreSQL schema.
9.  **[docs/08-availability-computation.md](docs/08-availability-computation.md):** Logic for computing and caching availability.

### Part 3: Key Challenges & Advanced Topics
10. **[docs/06-correctness-concurrency.md](docs/06-correctness-concurrency.md):** Ensuring correctness and preventing double-booking.
11. **[docs/09-notifications-waitlist.md](docs/09-notifications-waitlist.md):** Notification and waitlist systems.
12. **[docs/10-security-privacy-compliance.md](docs/10-security-privacy-compliance.md):** Security, privacy, and HIPAA.
13. **[docs/11-reliability-observability.md](docs/11-reliability-observability.md):** Reliability and observability.
14. **[docs/12-scalability-partitioning.md](docs/12-scalability-partitioning.md):** Scaling and data partitioning.

### Part 4: Interview Preparation
15. **[docs/13-interview-playbook.md](docs/13-interview-playbook.md):** Playbook for the interview.
16. **[interview/01-golden-answer-outline.md](interview/01-golden-answer-outline.md):** Outline for a "golden answer".
17. **[interview/02-follow-up-questions.md](interview/02-follow-up-questions.md):** Common follow-up questions.

## Repository Structure

```
/
├───docs/                 # In-depth system design documentation
├───diagrams/             # Mermaid diagrams of the architecture
├───services/             # Source code for the microservices
│   ├───appointment_service/
│   ├───availability_service/
│   └───...
├───labs/                 # Hands-on labs and local demo environment
│   └───01-local-demo/
├───interview/            # Interview preparation materials
└───README.md             # This file
```

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.