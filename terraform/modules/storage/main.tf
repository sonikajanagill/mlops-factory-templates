variable "project_id" {}
variable "region" {}

resource "random_id" "suffix" {
  byte_length = 4
}

# Raw Data Bucket
resource "google_storage_bucket" "raw_data" {
  name          = "${var.project_id}-raw-data-${random_id.suffix.hex}"
  location      = var.region
  force_destroy = true
  uniform_bucket_level_access = true
}

# Processed Data Bucket
resource "google_storage_bucket" "processed_data" {
  name          = "${var.project_id}-processed-data-${random_id.suffix.hex}"
  location      = var.region
  force_destroy = true
  uniform_bucket_level_access = true
}

# Pipeline Root Bucket (Artifacts)
resource "google_storage_bucket" "pipeline_root" {
  name          = "${var.project_id}-pipeline-root-${random_id.suffix.hex}"
  location      = var.region
  force_destroy = true
  uniform_bucket_level_access = true
}

output "raw_data_bucket" {
  value = google_storage_bucket.raw_data.name
}

output "processed_data_bucket" {
  value = google_storage_bucket.processed_data.name
}

output "pipeline_root_bucket" {
  value = google_storage_bucket.pipeline_root.name
}
