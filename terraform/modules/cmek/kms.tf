# KMS Key Ring and Encryption Key for Vertex AI CMEK
# This creates the cryptographic infrastructure for healthcare/compliance workloads

resource "google_kms_key_ring" "healthcare_ml_keyring" {
  name     = var.keyring_name
  location = var.kms_location
  project  = var.project_id
}

resource "google_kms_crypto_key" "vertex_artifacts_key" {
  name            = var.crypto_key_name
  key_ring        = google_kms_key_ring.healthcare_ml_keyring.id
  rotation_period = var.key_rotation_period
  purpose         = "ENCRYPT_DECRYPT"

  lifecycle {
    prevent_destroy = true
  }

  version_template {
    algorithm = "GOOGLE_SYMMETRIC_ENCRYPTION"
  }
}

# Optional: Create a separate key for anonymized features (lower sensitivity)
resource "google_kms_crypto_key" "anonymized_features_key" {
  count           = var.create_separate_anonymized_key ? 1 : 0
  name            = "${var.crypto_key_name}-anonymized"
  key_ring        = google_kms_key_ring.healthcare_ml_keyring.id
  rotation_period = var.key_rotation_period
  purpose         = "ENCRYPT_DECRYPT"

  lifecycle {
    prevent_destroy = true
  }

  version_template {
    algorithm = "GOOGLE_SYMMETRIC_ENCRYPTION"
  }
}
