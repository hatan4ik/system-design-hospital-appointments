variable "project" {
  description = "Project name prefix."
  type        = string
  default     = "hospital-appointments"
}

variable "environment" {
  description = "Deployment environment (e.g., dev/stage/prod)."
  type        = string
}

variable "aws_region" {
  description = "AWS region to deploy into."
  type        = string
}

variable "azs" {
  description = "Availability zones to use (at least two)."
  type        = list(string)
}

variable "vpc_cidr" {
  description = "VPC CIDR block."
  type        = string
  default     = "10.0.0.0/16"
}

variable "db_username" {
  description = "Master username for Postgres."
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "Master password for Postgres."
  type        = string
  sensitive   = true
}

variable "db_name" {
  description = "Initial database name."
  type        = string
  default     = "appointments"
}

variable "rds_engine_version" {
  description = "Postgres engine version."
  type        = string
  default     = "16.3"
}

variable "rds_instance_class" {
  description = "Instance class for RDS."
  type        = string
  default     = "db.r6g.large"
}

variable "rds_allocated_storage" {
  description = "Initial allocated storage (GB)."
  type        = number
  default     = 200
}

variable "rds_max_allocated_storage" {
  description = "Max storage for autoscaling (GB)."
  type        = number
  default     = 1000
}

variable "redis_engine_version" {
  description = "Redis engine version."
  type        = string
  default     = "7.1"
}

variable "redis_node_type" {
  description = "ElastiCache node type."
  type        = string
  default     = "cache.r6g.large"
}

variable "redis_node_count" {
  description = "Number of cache nodes."
  type        = number
  default     = 1
}
