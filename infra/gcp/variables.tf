variable "project_id" {
  description = "GCP project ID."
  type        = string
}

variable "project" {
  description = "Project name prefix."
  type        = string
  default     = "hospital-appointments"
}

variable "environment" {
  description = "Environment name (dev/stage/prod)."
  type        = string
}

variable "region" {
  description = "GCP region (e.g., us-central1)."
  type        = string
}

variable "subnet_cidr" {
  description = "CIDR for the app subnet."
  type        = string
  default     = "10.40.0.0/20"
}

variable "db_username" {
  description = "Postgres username."
  type        = string
}

variable "db_password" {
  description = "Postgres password."
  type        = string
  sensitive   = true
}

variable "db_name" {
  description = "Database name."
  type        = string
  default     = "appointments"
}

variable "db_tier" {
  description = "Cloud SQL machine tier."
  type        = string
  default     = "db-custom-2-7680"
}

variable "db_disk_gb" {
  description = "Disk size for Cloud SQL (GB)."
  type        = number
  default     = 200
}

variable "redis_memory_gb" {
  description = "Memory size for Memorystore Redis (GB)."
  type        = number
  default     = 4
}
