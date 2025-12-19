terraform {
  required_version = ">= 1.4.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.11"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

locals {
  name = "${var.project}-${var.environment}"
  labels = {
    project     = var.project
    environment = var.environment
  }
}

resource "google_project_service" "enabled" {
  for_each = toset([
    "compute.googleapis.com",
    "artifactregistry.googleapis.com",
    "run.googleapis.com",
    "redis.googleapis.com",
    "sqladmin.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
  ])
  project = var.project_id
  service = each.key
}

resource "google_compute_network" "main" {
  name                    = "${local.name}-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "app" {
  name          = "${local.name}-subnet"
  ip_cidr_range = var.subnet_cidr
  region        = var.region
  network       = google_compute_network.main.id
  private_ip_google_access = true
}

resource "google_artifact_registry_repository" "main" {
  location      = var.region
  repository_id = "${local.name}-repo"
  format        = "DOCKER"
  labels        = local.labels
}

resource "google_sql_database_instance" "main" {
  name             = "${local.name}-pg"
  region           = var.region
  database_version = "POSTGRES_16"

  settings {
    tier              = var.db_tier
    availability_type = "REGIONAL"
    disk_type         = "PD_SSD"
    disk_size         = var.db_disk_gb
    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.main.self_link
    }
    backup_configuration {
      enabled            = true
      point_in_time_recovery_enabled = true
    }
    maintenance_window {
      day          = 7
      hour         = 3
      update_track = "stable"
    }
    database_flags {
      name  = "max_connections"
      value = "500"
    }
  }

  deletion_protection = true
  depends_on          = [google_project_service.enabled]
}

resource "google_sql_user" "main" {
  instance = google_sql_database_instance.main.name
  name     = var.db_username
  password = var.db_password
}

resource "google_sql_database" "app" {
  name     = var.db_name
  instance = google_sql_database_instance.main.name
}

resource "google_redis_instance" "main" {
  name           = "${local.name}-redis"
  tier           = "STANDARD_HA"
  memory_size_gb = var.redis_memory_gb
  region         = var.region
  authorized_network = google_compute_network.main.id
  connect_mode       = "PRIVATE_SERVICE_ACCESS"
  labels             = local.labels
}

resource "google_cloud_run_service" "appointment" {
  name     = "${local.name}-appointment"
  location = var.region

  template {
    spec {
      containers {
        image = "${google_artifact_registry_repository.main.repository_url}/appointment:latest"
        env {
          name  = "DB_DSN"
          value = "postgresql://${var.db_username}:${var.db_password}@${google_sql_database_instance.main.private_ip_address}:5432/${var.db_name}"
        }
        env {
          name  = "DB_SSLMODE"
          value = "require"
        }
        env {
          name  = "REDIS_URL"
          value = "redis://${google_redis_instance.main.host}:${google_redis_instance.main.port}/0"
        }
      }
    }
  }

  traffics {
    percent         = 100
    latest_revision = true
  }
  autogenerate_revision_name = true

  depends_on = [google_project_service.enabled]
}

resource "google_cloud_run_service" "availability" {
  name     = "${local.name}-availability"
  location = var.region

  template {
    spec {
      containers {
        image = "${google_artifact_registry_repository.main.repository_url}/availability:latest"
        env {
          name  = "DB_DSN"
          value = "postgresql://${var.db_username}:${var.db_password}@${google_sql_database_instance.main.private_ip_address}:5432/${var.db_name}"
        }
        env {
          name  = "DB_SSLMODE"
          value = "require"
        }
        env {
          name  = "REDIS_URL"
          value = "redis://${google_redis_instance.main.host}:${google_redis_instance.main.port}/0"
        }
      }
    }
  }

  traffics {
    percent         = 100
    latest_revision = true
  }
  autogenerate_revision_name = true

  depends_on = [google_project_service.enabled]
}

resource "google_cloud_run_service" "notification" {
  name     = "${local.name}-notification"
  location = var.region

  template {
    spec {
      containers {
        image = "${google_artifact_registry_repository.main.repository_url}/notification:latest"
      }
    }
  }

  traffics {
    percent         = 100
    latest_revision = true
  }
  autogenerate_revision_name = true

  depends_on = [google_project_service.enabled]
}
