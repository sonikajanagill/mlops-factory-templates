output "composer_bucket" {
  description = "GCS Bucket for Composer DAGs"
  value       = module.composer.dag_bucket
}

output "raw_data_bucket" {
  description = "Bucket for raw data"
  value       = module.storage.raw_data_bucket
}

output "processed_data_bucket" {
  description = "Bucket for processed data"
  value       = module.storage.processed_data_bucket
}

output "vertex_pipeline_root" {
  description = "GCS path for Vertex Pipeline root"
  value       = module.storage.pipeline_root_bucket
}
