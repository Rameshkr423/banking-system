# ── Topics ────────────────────────────────────────────────────
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

# ── Push Subscriptions ─────────────────────────────────────────
# Pub/Sub POSTs directly to Cloud Run — no streaming pull,
# no min-instances needed, zero cost when idle.

resource "google_pubsub_subscription" "transaction_sub" {
  name    = "transaction-events-sub"
  topic   = google_pubsub_topic.transaction_events.name
  project = var.project_id

  ack_deadline_seconds = 60

  push_config {
    push_endpoint = "${var.subscriber_url}/pubsub/transaction-events"
  }

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "300s"
  }
}

resource "google_pubsub_subscription" "audit_events_sub" {
  name    = "audit-events-sub"
  topic   = google_pubsub_topic.audit_events.name
  project = var.project_id

  ack_deadline_seconds = 60

  push_config {
    push_endpoint = "${var.subscriber_url}/pubsub/audit-events"
  }

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }
}
