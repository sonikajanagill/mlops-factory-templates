output "pool_name" {
  description = "The resource name of the Workload Identity Pool"
  value       = google_iam_workload_identity_pool.aws_pool.name
}

output "provider_name" {
  description = "The resource name of the Workload Identity Pool Provider"
  value       = google_iam_workload_identity_pool_provider.aws_provider.name
}

output "service_account_email" {
  description = "The email of the created Service Account"
  value       = google_service_account.vertex_sa.email
}
