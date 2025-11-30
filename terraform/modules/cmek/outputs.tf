output "keyring_id" {
  description = "ID of the KMS key ring"
  value       = google_kms_key_ring.healthcare_ml_keyring.id
}

output "keyring_name" {
  description = "Full resource name of the KMS key ring"
  value       = google_kms_key_ring.healthcare_ml_keyring.name
}

output "vertex_artifacts_key_id" {
  description = "ID of the Vertex AI artifacts encryption key"
  value       = google_kms_crypto_key.vertex_artifacts_key.id
}

output "vertex_artifacts_key_name" {
  description = "Full resource name of the Vertex AI artifacts encryption key"
  value       = google_kms_crypto_key.vertex_artifacts_key.name
}

output "anonymized_features_key_name" {
  description = "Full resource name of the anonymized features encryption key (if created)"
  value       = var.create_separate_anonymized_key ? google_kms_crypto_key.anonymized_features_key[0].name : null
}

output "encryption_spec_key_name" {
  description = "Encryption spec key name for use in Vertex AI initialization"
  value       = google_kms_crypto_key.vertex_artifacts_key.name
}
