variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "pool_id" {
  description = "Workload Identity Pool ID"
  type        = string
  default     = "aws-prod-pool"
}

variable "pool_display_name" {
  description = "Display name for the Workload Identity Pool"
  type        = string
  default     = "AWS Production ML Workloads"
}

variable "pool_description" {
  description = "Description for the Workload Identity Pool"
  type        = string
  default     = "Federated access for AWS-based ML pipelines"
}

variable "provider_id" {
  description = "Workload Identity Pool Provider ID"
  type        = string
  default     = "aws-provider"
}

variable "provider_display_name" {
  description = "Display name for the Workload Identity Pool Provider"
  type        = string
  default     = "AWS Provider"
}

variable "aws_account_id" {
  description = "AWS Account ID to trust"
  type        = string
}

variable "service_account_id" {
  description = "Service Account ID for the Vertex AI agent"
  type        = string
  default     = "vertex-training-sa"
}

variable "service_account_display_name" {
  description = "Display name for the Service Account"
  type        = string
  default     = "Vertex AI Training Agent"
}

variable "aws_role_name" {
  description = "Name of the AWS IAM Role to allow impersonation from"
  type        = string
  default     = "ml-training-role"
}
