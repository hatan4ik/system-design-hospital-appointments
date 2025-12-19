# Azure baseline IaC

Terraform to provision core Azure services for the hospital appointments stack:
- Resource group, VNet with delegated subnets
- Container Apps Environment (for FastAPI services + gateway)
- Azure Container Registry
- Postgres Flexible Server (zone redundant)
- Azure Cache for Redis (Premium)
- Log Analytics workspace

## Usage
```bash
cd infra/azure
terraform init
terraform plan \
  -var "subscription_id=<SUB_ID>" \
  -var "environment=dev" \
  -var "location=eastus" \
  -var "db_username=postgres" \
  -var "db_password=CHANGEME"
```

## Wiring services
- Postgres DSN: `postgresql://<db_username>:<db_password>@${postgres_fqdn}:5432/${postgres_database}?sslmode=require`
- Redis URL: `rediss://:<redis_access_key>@${redis_hostname}:${redis_ssl_port}/0` (access key from `azurerm_redis_cache.main.primary_access_key`)
- Set `DB_SSLMODE=require` and `DB_CONNECT_TIMEOUT` env vars in the services (already supported in code).
- Push images to the ACR login server and reference them in Container Apps revisions.

## Next build steps
- Define Container Apps for appointment/availability/notification and the nginx gateway, with environment variables pointing at Postgres/Redis.
- Lock down Redis/Postgres with private endpoints if you need full private access; add NSGs as required.
- Add Event Grid/Service Bus topics for domain events and Azure Cognitive Search or Elastic Cloud for provider search if needed.
