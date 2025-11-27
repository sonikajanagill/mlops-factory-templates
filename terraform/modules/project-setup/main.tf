variable "project_id" {
  description = "The Google Cloud Project ID"
  type        = string
}

resource "google_project_service" "apis" {
  for_each = toset([
    "composer.googleapis.com",
    "dataproc.googleapis.com",
    "aiplatform.googleapis.com",
    "storage.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudfunctions.googleapis.com",
    "pubsub.googleapis.com",
    "cloudscheduler.googleapis.com",
    "iam.googleapis.com",
    "bigquery.googleapis.com"
  ])

  project = var.project_id
  service = each.key

  disable_on_destroy = false
}
