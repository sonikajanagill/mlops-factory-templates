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
