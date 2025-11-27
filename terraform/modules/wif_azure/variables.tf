variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "pool_id" {
  description = "Workload Identity Pool ID"
  type        = string
  default     = "azure-health-pool"
}

variable "pool_display_name" {
  description = "Display name for the Workload Identity Pool"
  type        = string
  default     = "Azure Healthcare Workloads"
}

variable "pool_description" {
  description = "Description for the Workload Identity Pool"
  type        = string
  default     = "Federated access for Azure-based healthcare pipelines"
}

variable "provider_id" {
  description = "Workload Identity Pool Provider ID"
  type        = string
  default     = "azure-provider"
}

variable "provider_display_name" {
  description = "Display name for the Workload Identity Pool Provider"
  type        = string
  default     = "Azure OIDC Provider"
}

variable "azure_tenant_id" {
  description = "Azure Tenant ID"
  type        = string
}

variable "allowed_audiences" {
  description = "Allowed audiences for OIDC token exchange"
  type        = list(string)
  default     = ["api://AzureADTokenExchange"]
}
