terraform {
  required_version = ">= 1.4.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.60"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

locals {
  name = "${var.project}-${var.environment}"
  tags = {
    Project     = var.project
    Environment = var.environment
  }
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.7.0"

  name = local.name
  cidr = var.vpc_cidr

  azs             = var.azs
  private_subnets = [for i, az in var.azs : cidrsubnet(var.vpc_cidr, 4, i)]
  database_subnets = [
    for i, az in var.azs : cidrsubnet(var.vpc_cidr, 8, i + 16)
  ]

  enable_nat_gateway     = true
  single_nat_gateway     = true
  enable_dns_hostnames   = true
  enable_dns_support     = true
  create_database_subnet_group = true

  tags = local.tags
}

resource "aws_security_group" "ecs_services" {
  name        = "${local.name}-ecs"
  description = "Allow ECS tasks egress"
  vpc_id      = module.vpc.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.tags
}

resource "aws_security_group" "db" {
  name        = "${local.name}-db"
  description = "Postgres access from ECS"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description      = "ECS tasks to Postgres"
    from_port        = 5432
    to_port          = 5432
    protocol         = "tcp"
    security_groups  = [aws_security_group.ecs_services.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.tags
}

resource "aws_security_group" "redis" {
  name        = "${local.name}-redis"
  description = "Redis access from ECS"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description     = "ECS tasks to Redis"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_services.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = local.tags
}

module "rds" {
  source  = "terraform-aws-modules/rds/aws"
  version = "6.13.1"

  identifier = "${local.name}-postgres"

  engine               = "postgres"
  engine_version       = var.rds_engine_version
  family               = "postgres16"
  major_engine_version = "16"
  instance_class       = var.rds_instance_class
  allocated_storage    = var.rds_allocated_storage
  max_allocated_storage = var.rds_max_allocated_storage

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password
  port     = 5432

  multi_az               = true
  publicly_accessible    = false
  storage_encrypted      = true
  deletion_protection    = true
  skip_final_snapshot    = false
  performance_insights_enabled = true

  vpc_security_group_ids = [aws_security_group.db.id]
  db_subnet_group_name   = module.vpc.database_subnet_group

  tags = local.tags
}

module "elasticache" {
  source  = "terraform-aws-modules/elasticache/aws"
  version = "1.10.3"

  cluster_id           = "${local.name}-redis"
  engine               = "redis"
  engine_version       = var.redis_engine_version
  node_type            = var.redis_node_type
  parameter_group_name = "default.redis7"
  port                 = 6379

  number_cache_clusters  = var.redis_node_count
  subnet_group_name      = module.vpc.elasticache_subnet_group_name
  security_group_ids     = [aws_security_group.redis.id]

  tags = local.tags
}

module "ecs_cluster" {
  source  = "terraform-aws-modules/ecs/aws"
  version = "5.11.1"

  cluster_name = "${local.name}-ecs"
  tags         = local.tags
}

resource "aws_ecr_repository" "appointment" {
  name = "${local.name}-appointment"
  image_scanning_configuration { scan_on_push = true }
  tags = local.tags
}

resource "aws_ecr_repository" "availability" {
  name = "${local.name}-availability"
  image_scanning_configuration { scan_on_push = true }
  tags = local.tags
}

resource "aws_ecr_repository" "notification" {
  name = "${local.name}-notification"
  image_scanning_configuration { scan_on_push = true }
  tags = local.tags
}
