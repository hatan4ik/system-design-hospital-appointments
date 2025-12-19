# Hospital Appointment and Scheduling System

FANG/MANGO-style system design repository for a hospital appointment and scheduling platform. Includes design docs, reference FastAPI services, a local demo, and multi-cloud Terraform baselines.

## Audience
- System design interview prep
- Engineers studying correctness and concurrency in scheduling systems
- Readers comparing AWS/Azure/GCP service mappings

## Scope
### Goals
- Model a real hospital scheduling problem with explicit constraints and invariants.
- Demonstrate correctness patterns for concurrency and idempotent writes.
- Provide runnable services and infra baselines for hands-on exploration.

### Non-goals
- Production-ready UI or patient portal.
- Full EHR/EMR integration or billing workflows.
- Real patient data; examples are synthetic.

## Architecture at a glance
- Appointment service: booking, reschedule, cancel.
- Availability service: compute and cache open slots.
- Notification service: async reminders and waitlist messages.
- Storage: Postgres + Redis.
- Local demo: Nginx gateway on `localhost:8080`.

Diagram: [diagrams/01-high-level.mmd](diagrams/01-high-level.mmd)

## Design highlights
- Correctness: avoid double booking with advisory locks and a Postgres exclusion constraint. See [docs/06-correctness-concurrency.md](docs/06-correctness-concurrency.md) and [reference/db/schema.sql](reference/db/schema.sql).
- Idempotency: request hash guard and Idempotency-Key semantics. See [docs/06-correctness-concurrency.md](docs/06-correctness-concurrency.md).
- Availability caching: window-aware Redis caching and schedule rules. See [docs/08-availability-computation.md](docs/08-availability-computation.md).

## Documentation guide
- Overview and requirements: [docs/00-overview.md](docs/00-overview.md), [docs/01-requirements.md](docs/01-requirements.md)
- Domain and APIs: [docs/03-domain-model.md](docs/03-domain-model.md), [docs/04-api-design.md](docs/04-api-design.md), [reference/api/openapi-snippets.md](reference/api/openapi-snippets.md)
- Architecture and data model: [docs/05-core-architecture.md](docs/05-core-architecture.md), [docs/07-data-model-postgres.md](docs/07-data-model-postgres.md)
- Correctness and availability: [docs/06-correctness-concurrency.md](docs/06-correctness-concurrency.md), [docs/08-availability-computation.md](docs/08-availability-computation.md)
- Reliability, scale, and security: [docs/11-reliability-observability.md](docs/11-reliability-observability.md), [docs/12-scalability-partitioning.md](docs/12-scalability-partitioning.md), [docs/10-security-privacy-compliance.md](docs/10-security-privacy-compliance.md)
- Interview prep: [docs/13-interview-playbook.md](docs/13-interview-playbook.md), [interview/01-golden-answer-outline.md](interview/01-golden-answer-outline.md)

## Repository map
| Path | Purpose |
| --- | --- |
| docs/ | Design narrative from requirements to scaling |
| diagrams/ | Architecture and infra diagrams (Mermaid) |
| services/ | FastAPI services (appointment, availability, notification) |
| labs/ | Runnable demos and drills |
| infra/ | Terraform baselines for AWS/Azure/GCP |
| reference/ | API and DB references |
| interview/ | Interview playbook and outlines |

## Quickstart (local demo)
Prereqs: Docker and Docker Compose.

```bash
cd labs/01-local-demo
docker compose up --build
curl -s localhost:8080/healthz | jq
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
