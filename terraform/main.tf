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
  image           = var.api_image
  db_connection   = module.cloud_sql.connection_name
  db_password_secret = "banking-db-password"
  jwt_secret         = "banking-jwt-secret"
  service_account = "banking-api-sa@${var.project_id}.iam.gserviceaccount.com"
}

# ── Pub/Sub ──
module "pubsub" {
  source     = "./modules/pubsub"
  project_id = var.project_id
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