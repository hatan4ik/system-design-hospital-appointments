output "artifact_registry_repo" {
  value = google_artifact_registry_repository.main.repository_url
}

output "cloud_run_services" {
  value = {
    appointment  = google_cloud_run_service.appointment.status[0].url
    availability = google_cloud_run_service.availability.status[0].url
    notification = google_cloud_run_service.notification.status[0].url
  }
}

output "cloud_sql_private_ip" {
  value = google_sql_database_instance.main.private_ip_address
}

output "redis_host" {
  value = google_redis_instance.main.host
}

output "redis_port" {
  value = google_redis_instance.main.port
}
