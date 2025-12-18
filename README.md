# System Design: Medical Hospital Appointment & Scheduling System

This repository provides a FAANG/MANGO-grade training pack for the system design interview question: "**Design a medical hospital appointment and schedule system**".

It includes:
- Interview-ready frameworks, deep tradeoffs, and follow-up answers.
- Architectural designs for APIs, data models, scheduling engines, notifications, and integrations.
- Considerations for reliability, scalability, privacy (HIPAA), security, observability, and cost management.
- Reference implementation skeletons and a runnable local lab environment.

## Quick Start (Local Demo)

To run the local demo environment:
```bash
cd labs/01-local-demo
docker compose up --build
```

In another terminal, you can check the health of the services:
```bash
curl -s localhost:8080/healthz | jq
```

## Where to Start

For a comprehensive understanding of the system design, we recommend reading the documentation in the following order:

1.  **[docs/00-overview.md](docs/00-overview.md)**: A high-level overview of the system and its core components.
2.  **[docs/01-requirements.md](docs/01-requirements.md)**: Detailed functional and non-functional requirements.
3.  **[docs/05-core-architecture.md](docs/05-core-architecture.md)**: The core architecture of the system.
4.  **[docs/06-correctness-concurrency.md](docs/06-correctness-concurrency.md)**: A key interview differentiator, discussing correctness and concurrency.
5.  **[interview/01-golden-answer-outline.md](interview/01-golden-answer-outline.md)**: An outline for a golden answer in an interview setting.

## Documentation

The `docs` directory contains a comprehensive set of documents covering all aspects of the system design:

- **[00-overview.md](docs/00-overview.md)**: High-level overview of the system.
- **[01-requirements.md](docs/01-requirements.md)**: Functional and non-functional requirements.
- **[02-capacity-estimation.md](docs/02-capacity-estimation.md)**: Capacity estimation and scaling.
- **[03-domain-model.md](docs/03-domain-model.md)**: The domain model of the system.
- **[04-api-design.md](docs/04-api-design.md)**: API design and definitions.
- **[05-core-architecture.md](docs/05-core-architecture.md)**: Core architecture of the system.
- **[06-correctness-concurrency.md](docs/06-correctness-concurrency.md)**: Correctness and concurrency considerations.
- **[07-data-model-postgres.md](docs/07-data-model-postgres.md)**: The PostgreSQL data model.
- **[08-availability-computation.md](docs/08-availability-computation.md)**: Availability computation logic.
- **[09-notifications-waitlist.md](docs/09-notifications-waitlist.md)**: Notification and waitlist system.
- **[10-security-privacy-compliance.md](docs/10-security-privacy-compliance.md)**: Security, privacy, and compliance (HIPAA).
- **[11-reliability-observability.md](docs/11-reliability-observability.md)**: Reliability and observability.
- **[12-scalability-partitioning.md](docs/12-scalability-partitioning.md)**: Scalability and partitioning.
- **[13-interview-playbook.md](docs/13-interview-playbook.md)**: A playbook for the interview.

License: MIT
