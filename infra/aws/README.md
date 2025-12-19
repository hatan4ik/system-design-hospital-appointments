# AWS baseline IaC

Terraform modules to provision core infrastructure for the hospital appointments stack on AWS. It stands up:
- VPC with private and database subnets plus NAT
- Security groups for ECS tasks, Postgres, and Redis
- Multi-AZ RDS Postgres
- ElastiCache Redis
- ECS cluster (Fargate-ready)
- ECR repos per service

## Usage
```bash
cd infra/aws
terraform init
terraform plan \
  -var "environment=dev" \
  -var "aws_region=us-east-1" \
  -var 'azs=["us-east-1a","us-east-1b"]' \
  -var "db_username=postgres" \
  -var "db_password=CHANGEME"
```
Provide stronger passwords via `TF_VAR_*` or a Terraform Cloud workspace. No apply happens in CI; run `terraform apply` manually when ready.

## Wiring services
- Application DSN: `postgresql://<db_username>:<db_password>@${database_endpoint}:5432/${database_name}?sslmode=require`
- Redis URL: `redis://:${redis_auth_token}@${redis_endpoint}:6379/0` (enable auth in the ElastiCache parameter group before prod)
- Set `DB_SSLMODE=require` and `DB_CONNECT_TIMEOUT` in service envs.
- Push images to the ECR URLs output by Terraform; point ECS task definitions to those images.

## Next build steps
- Add ECS services + ALB/API Gateway routes for the FastAPI apps and the nginx gateway.
- Add EventBridge bus/SNS+SQS topics for domain events, and OpenSearch for provider search if needed.
- Protect secrets with AWS Secrets Manager or SSM Parameter Store and wire tasks with IAM roles.
