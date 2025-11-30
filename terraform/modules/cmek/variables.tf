variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "kms_location" {
  description = "Location for KMS key ring (e.g., us-central1, europe-west1)"
  type        = string
  default     = "us-central1"
}

variable "keyring_name" {
  description = "Name of the KMS key ring"
  type        = string
  default     = "healthcare-ml-keyring"
}

variable "crypto_key_name" {
  description = "Name of the encryption key for Vertex AI artifacts"
  type        = string
  default     = "vertex-artifacts-key"
}

variable "key_rotation_period" {
  description = "Rotation period for the encryption key (e.g., 7776000s for 90 days)"
  type        = string
  default     = "7776000s" # 90 days
}

variable "create_separate_anonymized_key" {
  description = "Create a separate encryption key for anonymized features (lower sensitivity)"
  type        = bool
  default     = false
}

variable "custom_service_account_email" {
  description = "Email of a custom service account to grant CMEK permissions (optional)"
  type        = string
  default     = ""
}

variable "enable_audit_logging" {
  description = "Enable audit logging for KMS key usage"
  type        = bool
  default     = true
}
