output "vpc_id" {
  value = module.vpc.vpc_id
}

output "private_subnets" {
  value = module.vpc.private_subnets
}

output "database_endpoint" {
  value = module.rds.db_instance_address
}

output "database_name" {
  value = module.rds.db_instance_name
}

output "redis_endpoint" {
  value = module.elasticache.primary_endpoint_address
}

output "ecs_cluster_id" {
  value = module.ecs_cluster.ecs_cluster_id
}

output "ecr_repositories" {
  value = {
    appointment  = aws_ecr_repository.appointment.repository_url
    availability = aws_ecr_repository.availability.repository_url
    notification = aws_ecr_repository.notification.repository_url
  }
}
