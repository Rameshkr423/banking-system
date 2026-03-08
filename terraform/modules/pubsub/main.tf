resource "google_pubsub_topic" "transaction_events" {
  name    = "transaction-events"
  project = var.project_id
}
resource "google_pubsub_topic" "audit_events" {
  name    = "audit-events"
  project = var.project_id
}
resource "google_pubsub_topic" "notification_events" {
  name    = "notification-events"
  project = var.project_id
}
resource "google_pubsub_subscription" "transaction_sub" {
  name    = "transaction-events-sub"
  topic   = google_pubsub_topic.transaction_events.name
  project = var.project_id
  ack_deadline_seconds = 60
}
resource "google_pubsub_subscription" "dataflow_sub" {
  name    = "transaction-dataflow-sub"
  topic   = google_pubsub_topic.transaction_events.name
  project = var.project_id
  ack_deadline_seconds = 60
}
