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

### Part 1: The Core System

1.  **[docs/00-overview.md](./docs/00-overview.md):** A high-level overview of the system, its goals, and its core components.
2.  **[docs/01-requirements.md](./docs/01-requirements.md):** A detailed breakdown of the functional and non-functional requirements.
3.  **[docs/05-core-architecture.md](./docs/05-core-architecture.md):** A tour of the microservices-based architecture, the services involved, and the data stores.
4.  **[diagrams/01-high-level.mmd](./diagrams/01-high-level.mmd):** The high-level architecture diagram.

### Part 2: Deep Dive & Key Challenges

5.  **[docs/06-correctness-concurrency.md](./docs/06-correctness-concurrency.md):** A critical discussion of how to ensure correctness and prevent race conditions (e.g., double-booking). This is a key differentiator in an interview.
6.  **[docs/08-availability-computation.md](./docs/08-availability-computation.md):** A deep dive into the logic of computing and caching provider availability.
7.  **[docs/07-data-model-postgres.md](./docs/07-data-model-postgres.md):** The detailed PostgreSQL schema and data model.

### Part 3: Advanced Topics & Interview Preparation

8.  **[docs/09-notifications-waitlist.md](./docs/09-notifications-waitlist.md):** The design of the notification and waitlist systems.
9.  **[docs/10-security-privacy-compliance.md](./docs/10-security-privacy-compliance.md):** A guide to handling security, privacy, and HIPAA compliance.
10. **[docs/11-reliability-observability.md](./docs/11-reliability-observability.md):** Strategies for ensuring reliability and observability.
11. **[docs/12-scalability-partitioning.md](./docs/12-scalability-partitioning.md):** Techniques for scaling the system and partitioning data.
12. **[interview/01-golden-answer-outline.md](./interview/01-golden-answer-outline.md):** An outline for a "golden answer" in a system design interview.
13. **[interview/02-follow-up-questions.md](./interview/02-follow-up-questions.md):** A list of common follow-up questions to prepare for.

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