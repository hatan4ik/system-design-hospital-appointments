variable "subscription_id" {
  description = "Azure subscription ID."
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

variable "location" {
  description = "Azure region (e.g., eastus, westus2)."
  type        = string
}

variable "vnet_cidr" {
  description = "CIDR for the virtual network."
  type        = string
  default     = "10.20.0.0/16"
}

variable "db_username" {
  description = "Postgres admin username."
  type        = string
}

variable "db_password" {
  description = "Postgres admin password."
  type        = string
  sensitive   = true
}

variable "db_name" {
  description = "Application database name."
  type        = string
  default     = "appointments"
}

variable "postgres_version" {
  description = "Postgres major version."
  type        = string
  default     = "16"
}

variable "db_sku" {
  description = "Flexible server SKU (e.g., GP_Standard_D4s_v3)."
  type        = string
  default     = "GP_Standard_D4s_v3"
}

variable "db_storage_mb" {
  description = "Storage size in MB."
  type        = number
  default     = 131072 # 128 GB
}

variable "redis_capacity" {
  description = "Redis capacity (P1=1, P2=2, ...)."
  type        = number
  default     = 1
}
