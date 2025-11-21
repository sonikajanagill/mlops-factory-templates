variable "project_id" {}
variable "region" {}
variable "composer_name" {}
variable "network_name" {}
variable "service_account" {}

resource "google_composer_environment" "mlops_composer" {
  name    = var.composer_name
  region  = var.region
  project = var.project_id

  config {
    software_config {
      image_version = "composer-3-airflow-2.9.1" # Latest available
    }

    node_config {
      service_account = var.service_account
      network         = "projects/${var.project_id}/global/networks/${var.network_name}"
      # For private IP (recommended for prod), uncomment below:
      # ip_allocation_policy {
      #   use_ip_aliases = true
      # }
      # enable_private_endpoint = true
    }
  }
}

output "dag_bucket" {
  value = google_composer_environment.mlops_composer.config[0].dag_gcs_prefix
}

output "airflow_uri" {
  value = google_composer_environment.mlops_composer.config[0].airflow_uri
}
