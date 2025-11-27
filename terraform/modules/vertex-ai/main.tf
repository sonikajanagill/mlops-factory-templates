variable "project_id" {
  description = "The Google Cloud Project ID"
  type        = string
}

variable "region" {
  description = "The Google Cloud region for Vertex AI resources"
  type        = string
}

variable "service_account" {
  description = "The service account email for Vertex AI pipelines"
  type        = string
}

# 1. Feature Store (BigQuery backed)
# Note: Feature Online Store is the modern way, but for batch serving we just need the BQ source.
# We will create a Feature Online Store for low-latency serving if needed.

resource "google_vertex_ai_feature_online_store" "feature_store" {
  name     = "mlops_feature_store"
  project  = var.project_id
  region   = var.region
  
  bigtable {
    auto_scaling {
      min_node_count = 1
      max_node_count = 2
      cpu_utilization_target = 50
    }
  }
}

# 2. Artifact Registry (for custom containers)
resource "google_artifact_registry_repository" "mlops_repo" {
  location      = var.region
  repository_id = "mlops-repo"
  description   = "Docker repository for MLOps Factory"
  format        = "DOCKER"
  project       = var.project_id
}

output "feature_store_name" {
  value = google_vertex_ai_feature_online_store.feature_store.name
}

output "artifact_registry_repo" {
  value = google_artifact_registry_repository.mlops_repo.name
}
