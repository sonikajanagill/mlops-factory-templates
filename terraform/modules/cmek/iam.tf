# IAM bindings for CMEK - Grant Vertex AI service accounts permission to use encryption keys

# Get the Vertex AI service account
data "google_service_account" "vertex_ai_sa" {
  account_id = "service-${data.google_project.current.number}@gcp-sa-aiplatform.iam.gserviceaccount.com"
  project    = var.project_id
}

# Grant Vertex AI permission to use the main encryption key
resource "google_kms_crypto_key_iam_member" "vertex_ai_encrypter_decrypter" {
  crypto_key_id = google_kms_crypto_key.vertex_artifacts_key.id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member        = "serviceAccount:${data.google_service_account.vertex_ai_sa.email}"
}

# Grant Vertex AI permission to use the anonymized features key (if created)
resource "google_kms_crypto_key_iam_member" "vertex_ai_encrypter_decrypter_anonymized" {
  count         = var.create_separate_anonymized_key ? 1 : 0
  crypto_key_id = google_kms_crypto_key.anonymized_features_key[0].id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member        = "serviceAccount:${data.google_service_account.vertex_ai_sa.email}"
}

# Grant custom service account permission to use the key (if provided)
resource "google_kms_crypto_key_iam_member" "custom_sa_encrypter_decrypter" {
  count         = var.custom_service_account_email != "" ? 1 : 0
  crypto_key_id = google_kms_crypto_key.vertex_artifacts_key.id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member        = "serviceAccount:${var.custom_service_account_email}"
}

# Allow audit logging for compliance
resource "google_kms_crypto_key_iam_member" "audit_viewer" {
  count         = var.enable_audit_logging ? 1 : 0
  crypto_key_id = google_kms_crypto_key.vertex_artifacts_key.id
  role          = "roles/cloudkms.viewer"
  member        = "serviceAccount:${data.google_service_account.vertex_ai_sa.email}"
}

# Data source to get current project info
data "google_project" "current" {
  project_id = var.project_id
}
