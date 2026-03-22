terraform {
  required_version = ">= 1.6"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# ── Cloud SQL ──
module "cloud_sql" {
  source      = "./modules/cloud_sql"
  project_id  = var.project_id
  region      = var.region
  db_password = var.db_password
}

# ── Cloud Run ──
module "cloud_run" {
  source          = "./modules/cloud_run"
  project_id      = var.project_id
  region          = var.region
  
  # ── Updated: was image = var.image ────────────────────────
  image_tag = var.image_tag
  subscriber_image_tag = var.subscriber_image_tag
  
  cloudsql_connection_name = module.cloud_sql.connection_name

  db_password_secret = "banking-db-password"
  jwt_secret         = "banking-jwt-secret"

  service_account = "banking-api-sa@${var.project_id}.iam.gserviceaccount.com"
}

# ── Pub/Sub ──
module "pubsub" {
  source     = "./modules/pubsub"
  project_id = var.project_id
}

resource "google_pubsub_subscription" "transaction_sub" {
  name    = "transaction-events-sub"
  topic   = google_pubsub_topic.transaction_events.name
  project = var.project_id
  ack_deadline_seconds = 60

  push_config {
    push_endpoint = "${var.subscriber_url}/pubsub/transaction-events"
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

# ── BigQuery ──
module "bigquery" {
  source     = "./modules/bigquery"
  project_id = var.project_id
  region     = var.region
}

# ── Storage ──
module "storage" {
  source     = "./modules/storage"
  project_id = var.project_id
  region     = var.region
}

# ── VM Frontend ──
module "vm" {
  source     = "./modules/vm"
  project_id = var.project_id
  region     = var.region
  zone       = var.zone
}