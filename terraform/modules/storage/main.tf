variable "project_id" {
  description = "The Google Cloud Project ID"
  type        = string
}

variable "region" {
  description = "The Google Cloud region for storage buckets"
  type        = string
}

resource "random_id" "suffix" {
  byte_length = 4
}

# Raw Data Bucket
resource "google_storage_bucket" "raw_data" {
  name                        = "${var.project_id}-raw-data-${random_id.suffix.hex}"
  location                    = var.region
  force_destroy               = true  # Set to false for production
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      num_newer_versions = 3
    }
    action {
      type = "Delete"
    }
  }
}

# Processed Data Bucket
resource "google_storage_bucket" "processed_data" {
  name                        = "${var.project_id}-processed-data-${random_id.suffix.hex}"
  location                    = var.region
  force_destroy               = true  # Set to false for production
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      num_newer_versions = 3
    }
    action {
      type = "Delete"
    }
  }
}

# Pipeline Root Bucket (Artifacts)
resource "google_storage_bucket" "pipeline_root" {
  name                        = "${var.project_id}-pipeline-root-${random_id.suffix.hex}"
  location                    = var.region
  force_destroy               = true  # Set to false for production
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 90  # Delete artifacts older than 90 days
    }
    action {
      type = "Delete"
    }
  }
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
