variable "project_id" {}

# 1. Cloud Composer Service Account
resource "google_service_account" "sa_composer" {
  account_id   = "sa-composer"
  display_name = "Cloud Composer Service Account"
  project      = var.project_id
}

resource "google_project_iam_member" "composer_roles" {
  for_each = toset([
    "roles/composer.worker",
    "roles/dataproc.editor", # To trigger Dataproc
    "roles/aiplatform.user", # To trigger Vertex AI
    "roles/iam.serviceAccountUser" # To act as other SAs
  ])
  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.sa_composer.email}"
}

# 2. Dataproc Service Account
resource "google_service_account" "sa_dataproc" {
  account_id   = "sa-dataproc"
  display_name = "Dataproc Service Account"
  project      = var.project_id
}

resource "google_project_iam_member" "dataproc_roles" {
  for_each = toset([
    "roles/dataproc.worker",
    "roles/storage.objectAdmin",
    "roles/bigquery.dataEditor"
  ])
  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.sa_dataproc.email}"
}

# 3. Vertex AI Pipeline Service Account
resource "google_service_account" "sa_vertex_pipeline" {
  account_id   = "sa-vertex-pipeline"
  display_name = "Vertex AI Pipeline Service Account"
  project      = var.project_id
}

resource "google_project_iam_member" "vertex_roles" {
  for_each = toset([
    "roles/aiplatform.user",
    "roles/storage.objectAdmin",
    "roles/bigquery.dataEditor"
  ])
  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.sa_vertex_pipeline.email}"
}

# Outputs
output "sa_composer_email" {
  value = google_service_account.sa_composer.email
}

output "sa_dataproc_email" {
  value = google_service_account.sa_dataproc.email
}

output "sa_vertex_pipeline_email" {
  value = google_service_account.sa_vertex_pipeline.email
}
