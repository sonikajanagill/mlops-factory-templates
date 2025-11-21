variable "project_id" {}

# Notification Channel (Email)
resource "google_monitoring_notification_channel" "email" {
  display_name = "MLOps Team Email"
  type         = "email"
  project      = var.project_id
  labels = {
    email_address = "mlops-team@example.com" # Change this in prod
  }
}

# Alert Policy for Pipeline Failures (Log-based)
resource "google_monitoring_alert_policy" "pipeline_failure" {
  display_name = "Vertex AI Pipeline Failure"
  project      = var.project_id
  combiner     = "OR"
  conditions {
    display_name = "Pipeline Failed"
    condition_matched_log {
      filter = "resource.type=\"aiplatform.googleapis.com/PipelineJob\" AND jsonPayload.state=\"PIPELINE_STATE_FAILED\""
    }
  }
  notification_channels = [google_monitoring_notification_channel.email.name]
}

variable "cloud_function_url" {
  description = "URL of the Cloud Function to trigger"
  type        = string
  default     = "" # Optional, can be passed if function exists
}

# Pub/Sub Topic for Model Monitoring Alerts
resource "google_pubsub_topic" "model_monitoring_alerts" {
  name    = "vertex-ai-model-monitoring-alerts"
  project = var.project_id
}

# Pub/Sub Subscription for Cloud Function
resource "google_pubsub_subscription" "monitoring_trigger_sub" {
  name    = "monitoring-trigger-subscription"
  topic   = google_pubsub_topic.model_monitoring_alerts.name
  project = var.project_id

  ack_deadline_seconds = 20
  
  # Only configure push if URL is provided
  dynamic "push_config" {
    for_each = var.cloud_function_url != "" ? [1] : []
    content {
      push_endpoint = var.cloud_function_url
    }
  }
}

output "monitoring_topic_name" {
  value = google_pubsub_topic.model_monitoring_alerts.name
}
