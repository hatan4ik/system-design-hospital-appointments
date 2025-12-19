# GCP baseline IaC

Terraform to stand up core GCP services for the hospital appointments stack:
- VPC + custom subnet with private access
- Artifact Registry (Docker)
- Cloud SQL for Postgres (regional, private IP)
- Memorystore for Redis (private)
- Cloud Run services (appointment, availability, notification)
- Enables required APIs

## Usage
```bash
cd infra/gcp
terraform init
terraform plan \
  -var "project_id=<GCP_PROJECT_ID>" \
  -var "environment=dev" \
  -var "region=us-central1" \
  -var "db_username=postgres" \
  -var "db_password=CHANGEME"
```

## Wiring services
- Postgres DSN: `postgresql://<db_username>:<db_password>@${cloud_sql_private_ip}:5432/${db_name}?sslmode=require`
- Redis URL: `redis://${redis_host}:${redis_port}/0` (private access)
- Push service images to the Artifact Registry repo and deploy new revisions pointing at those images.

## Next build steps
- Add Cloud Run load balancer / API Gateway in front of the services and configure auth (IAP/JWT).
- Add Pub/Sub topics for domain events and Elastic Cloud on GCP or self-hosted OpenSearch for provider search if needed.
- Use Secret Manager for credentials and inject via Cloud Run secrets.
