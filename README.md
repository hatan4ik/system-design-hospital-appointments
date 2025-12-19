# System Design: Hospital Appointment & Scheduling System

FAANG/MANGA-grade training repo for the prompt **“Design a hospital appointment and scheduling system.”** It includes production-minded microservice code, correctness patterns, infra blueprints across AWS/Azure/GCP, and interview prep material.

## What’s inside
- Code: FastAPI services (appointment, availability, notification) with idempotency, Redis holds, Postgres exclusion constraints (`services/`).
- Docs: End-to-end system design narrative (`docs/00-overview.md` through `docs/13-interview-playbook.md`).
- Diagrams: High-level + cloud-specific infra Mermaid files (`diagrams/01-high-level.mmd`, `diagrams/infra-*.mmd`).
- Labs: Runnable local demo (`labs/01-local-demo`) and drills.
- Infra: Terraform baselines for AWS, Azure, GCP (`infra/*`), plus CI for tests and Terraform validation.
- Interview: Golden answers and follow-ups (`interview/`).

## Quickstart (local demo)
```bash
cd labs/01-local-demo
docker compose up --build
curl -s localhost:8080/healthz | jq
```

## Service behavior highlights
- Appointment API: durable idempotency (Postgres+Redis with request-hash check), provider/day advisory locks + Redis mutex, Postgres exclusion constraint to stop overlaps.
- Availability API: serves availability bounded by provider schedules/blocks with window-aware caching in Redis.
- Schemas: `labs/01-local-demo/schema.sql` and `reference/db/schema.sql` install `btree_gist` + `no_overlap_per_provider` exclusion constraint.

## Documentation path (suggested)
1) Core: `docs/00-overview.md` → `docs/05-core-architecture.md` → `diagrams/01-high-level.mmd`  
2) Correctness & availability: `docs/06-correctness-concurrency.md`, `docs/08-availability-computation.md`  
3) Data & scale: `docs/07-data-model-postgres.md`, `docs/12-scalability-partitioning.md`  
4) Ops & trust: `docs/10-security-privacy-compliance.md`, `docs/11-reliability-observability.md`  
5) Interview prep: `docs/13-interview-playbook.md`, `interview/01-golden-answer-outline.md`

## Infrastructure (baseline blueprints)
- AWS: `infra/aws/` (VPC, RDS, ElastiCache, ECS Fargate, ECR). Diagram: `diagrams/infra-aws.mmd`.
- Azure: `infra/azure/` (VNet, Container Apps, Postgres Flexible Server, Azure Cache). Diagram: `diagrams/infra-azure.mmd`.
- GCP: `infra/gcp/` (VPC, Cloud Run, Cloud SQL, Memorystore, Artifact Registry). Diagram: `diagrams/infra-gcp.mmd`.

## Tests
```bash
python -m pytest services/appointment_service/app/test_main.py
```

## License
MIT — see [LICENSE](./LICENSE).
