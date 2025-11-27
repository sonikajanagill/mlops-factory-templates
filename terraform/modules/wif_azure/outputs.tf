output "pool_name" {
  description = "The resource name of the Workload Identity Pool"
  value       = google_iam_workload_identity_pool.azure_pool.name
}

output "provider_name" {
  description = "The resource name of the Workload Identity Pool Provider"
  value       = google_iam_workload_identity_pool_provider.azure_provider.name
}
