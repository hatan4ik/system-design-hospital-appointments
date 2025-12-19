# System Design: Hospital Appointment & Scheduling System

FAANG/MANGA-grade training repo for **“Design a hospital appointment and scheduling system.”** Includes production-minded FastAPI services, correctness patterns, IaC for AWS/Azure/GCP, and interview prep.

## TL;DR
- **Run the local demo:** `cd labs/01-local-demo && docker compose up --build`
- **Health check:** `curl -s localhost:8080/healthz | jq`
- **Unit tests:** `python -m pytest services/appointment_service/app/test_main.py`

## Contents (at a glance)
- **Code:** `services/` — appointment, availability, notification services (FastAPI + Redis + Postgres).
- **Docs:** `docs/` — end-to-end design narrative from overview to interview playbook.
- **Diagrams:** `diagrams/` — high-level and cloud infra Mermaid diagrams.
- **Labs:** `labs/` — runnable local demo and drills.
- **Infra:** `infra/aws`, `infra/azure`, `infra/gcp` — Terraform baselines; CI runs pytest and Terraform validate.
- **Interview:** `interview/` — golden answer outline and follow-up questions.

## Service behavior highlights
- **Appointment API:** Durable idempotency (Postgres + Redis with request-hash guard), provider/day advisory locks plus Redis mutex, Postgres exclusion constraint preventing overlapping bookings.
- **Availability API:** Availability bounded by provider schedules/blocks with window-aware Redis caching.
- **Schemas:** `labs/01-local-demo/schema.sql`, `reference/db/schema.sql` enable `btree_gist` + `no_overlap_per_provider` constraint.

## Documentation path (recommended)
1. Core flow: [docs/00-overview.md](docs/00-overview.md) → [docs/05-core-architecture.md](docs/05-core-architecture.md) → [diagrams/01-high-level.mmd](diagrams/01-high-level.mmd)
2. Correctness & availability: [docs/06-correctness-concurrency.md](docs/06-correctness-concurrency.md), [docs/08-availability-computation.md](docs/08-availability-computation.md)
3. Data & scale: [docs/07-data-model-postgres.md](docs/07-data-model-postgres.md), [docs/12-scalability-partitioning.md](docs/12-scalability-partitioning.md)
4. Ops & trust: [docs/10-security-privacy-compliance.md](docs/10-security-privacy-compliance.md), [docs/11-reliability-observability.md](docs/11-reliability-observability.md)
5. Interview prep: [docs/13-interview-playbook.md](docs/13-interview-playbook.md), [interview/01-golden-answer-outline.md](interview/01-golden-answer-outline.md)

## Infrastructure blueprints
- **AWS:** [infra/aws](infra/aws) (VPC, RDS, ElastiCache, ECS Fargate, ECR). Diagram: [diagrams/infra-aws.mmd](diagrams/infra-aws.mmd)
- **Azure:** [infra/azure](infra/azure) (VNet, Container Apps, Postgres Flexible Server, Azure Cache). Diagram: [diagrams/infra-azure.mmd](diagrams/infra-azure.mmd)
- **GCP:** [infra/gcp](infra/gcp) (VPC, Cloud Run, Cloud SQL, Memorystore, Artifact Registry). Diagram: [diagrams/infra-gcp.mmd](diagrams/infra-gcp.mmd)

## Local demo
```bash
cd labs/01-local-demo
docker compose up --build
curl -s localhost:8080/healthz | jq
```

## Testing
```bash
python -m pytest services/appointment_service/app/test_main.py
```

## License
MIT — see [LICENSE](LICENSE).
