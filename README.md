# Hospital Appointment and Scheduling System

FANG/MANGO-style system design repository for a hospital appointment and scheduling platform. Includes design docs, reference FastAPI services, a local demo, and multi-cloud Terraform baselines.

## Audience
- System design interview prep
- Engineers studying correctness and concurrency in scheduling systems
- Readers comparing AWS/Azure/GCP service mappings

## Scope

### In Scope
- **Core Scheduling System**: A microservices-based system that models the core functionality of a hospital appointment scheduling platform. This includes appointment booking, rescheduling, and cancellation, as well as provider availability lookups.
- **Correctness and Concurrency Patterns**: Demonstrating advanced techniques to prevent common scheduling issues like double booking. This is achieved through a combination of Redis-based distributed locks, PostgreSQL advisory locks, and database-level exclusion constraints.
- **Idempotent API Design**: Implementation of an idempotent API for write operations using an `Idempotency-Key` header and a multi-layered check mechanism (in-memory cache and durable database storage).
- **Reference Implementations**: Runnable FastAPI services for appointment, availability, and notification, designed for local and cloud deployment.
- **Multi-Cloud Infrastructure Blueprints**: Terraform baselines for deploying the system on AWS, Azure, and GCP, providing a practical reference for multi-cloud architecture.

### Out of Scope
- **User-Facing Applications**: This project does not include a production-ready UI, patient portal, or any other front-end application. The focus is on the back-end system design.
- **Clinical and Financial Systems**: Full integration with Electronic Health Records (EHR/EMR), billing systems, or insurance providers is not part of this project.
- **HIPAA Compliance**: While the design considers security and privacy, it is not certified as HIPAA compliant. The provided infrastructure baselines would require further hardening and auditing for a production healthcare environment.
- **Production Data**: The system is designed to work with synthetic data for demonstration and testing purposes. No real patient data is used.

## Architecture at a glance
- Appointment service: booking, reschedule, cancel.
- Availability service: compute and cache open slots.
- Notification service: async reminders and waitlist messages.
- Storage: Postgres + Redis.
- Local demo: Nginx gateway on `localhost:8080`.

Diagram: [High-Level Architecture Diagram](diagrams/01-high-level.mmd)

## Design highlights
- Correctness: avoid double booking with advisory locks and a Postgres exclusion constraint. See [Correctness & Concurrency](docs/06-correctness-concurrency.md) and [Database Schema](reference/db/schema.sql).
- Idempotency: request hash guard and Idempotency-Key semantics. See [Correctness & Concurrency](docs/06-correctness-concurrency.md).
- Availability caching: window-aware Redis caching and schedule rules. See [Availability Computation](docs/08-availability-computation.md).

## Content Index

### System Design & Architecture
- [Overall System Architecture](diagrams/01-high-level.mmd)
- [Requirements & Capacity Estimation](docs/01-requirements.md)
- [Core Architecture & Domain Model](docs/05-core-architecture.md)
- [API Design & OpenAPI Snippets](docs/04-api-design.md)
- [Data Model (Postgres)](docs/07-data-model-postgres.md)

### Deep Dives
- [Correctness & Concurrency (Preventing Double Booking)](docs/06-correctness-concurrency.md)
- [Availability Computation & Caching](docs/08-availability-computation.md)
- [Notifications & Waitlists](docs/09-notifications-waitlist.md)

### Implementation
- Services:
    - [Appointment Service](services/appointment_service)
    - [Availability Service](services/availability_service)
    - [Notification Service](services/notification_service)
- [Database Schema](reference/db/schema.sql)

### Operations & Infrastructure
- [Local Demo & Quickstart](labs/01-local-demo)
- [Reliability & Observability](docs/11-reliability-observability.md)
- [Scalability & Partitioning](docs/12-scalability-partitioning.md)
- [Security, Privacy & Compliance](docs/10-security-privacy-compliance.md)
- Infrastructure as Code (Terraform):
    - [AWS](infra/aws)
    - [Azure](infra/azure)
    - [GCP](infra/gcp)

### Interview Preparation
- [Interview Playbook](docs/13-interview-playbook.md)
- [Golden Answer Outline](interview/01-golden-answer-outline.md)
- [Follow-up Questions](interview/02-follow-up-questions.md)

## Quickstart (local demo)
Prereqs: Docker and Docker Compose.

```bash
cd labs/01-local-demo
docker compose up --build
curl -s localhost:8080/healthz | jq
```

Seed synthetic data (200-1000 patients supported, no real patient data):
```bash
python labs/01-local-demo/seed_data.py --patients 500 --providers 25 --days 21 --truncate
psql "postgresql://postgres:postgres@localhost:5432/postgres" -f labs/01-local-demo/seed.sql
```

Try a sample flow:

```bash
curl -s "localhost:8080/availability?provider_id=prov_1&start=2025-12-18T15:00:00Z&end=2025-12-18T18:00:00Z&slot_minutes=15" | jq
curl -s -X POST localhost:8080/appointments \
  -H 'content-type: application/json' \
  -H 'Idempotency-Key: 11111111-1111-1111-1111-111111111111' \
  -d '{"patient_id":"pat_1","provider_id":"prov_1","visit_type":"FOLLOW_UP_15","start_ts":"2025-12-18T15:00:00Z","end_ts":"2025-12-18T15:15:00Z","location_id":"loc_1"}' | jq
```

## Testing
Prereqs: Python 3.12.

```bash
python -m pytest services/appointment_service/app/test_main.py
```

## CI and quality gates
- GitHub Actions runs pytest for the appointment service.
- Terraform formatting and validation run against `infra/aws`.

See `.github/workflows/ci.yml`.

## Infrastructure blueprints
- AWS: [infra/aws](infra/aws) (VPC, RDS, ElastiCache, ECS Fargate, ECR)
- Azure: [infra/azure](infra/azure) (VNet, Container Apps, Postgres Flexible Server, Azure Cache)
- GCP: [infra/gcp](infra/gcp) (VPC, Cloud Run, Cloud SQL, Memorystore, Artifact Registry)

Diagrams: [diagrams/infra-aws.mmd](diagrams/infra-aws.mmd), [diagrams/infra-azure.mmd](diagrams/infra-azure.mmd), [diagrams/infra-gcp.mmd](diagrams/infra-gcp.mmd)

## Contributing
- See [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## License
MIT. See [LICENSE](LICENSE).
