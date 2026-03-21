resource "google_cloud_run_v2_service" "banking_api" {
  name     = "banking-api"
  location = var.region
  project  = var.project_id

  template {
    service_account = var.service_account

    scaling {
      min_instance_count = 0
      max_instance_count = 5
    }

    containers {
      image = "us-west1-docker.pkg.dev/${var.project_id}/banking-repo/banking-api:${var.image_tag}"

      ports {
        container_port = 8080
      }

      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }

      env {
        name  = "DB_HOST"
        value = var.cloudsql_connection_name
      }

      env {
        name  = "DB_USER"
        value = "banking_user"
      }

      env {
        name  = "DB_NAME"
        value = "bank_db"
      }

      env {
        name  = "ENV"
        value = "production"
      }

      env {
        name = "DB_PASSWORD"
        value_source {
          secret_key_ref {
            secret  = var.db_password_secret
            version = "latest"
          }
        }
      }

      env {
        name = "SECRET_KEY"
        value_source {
          secret_key_ref {
            secret  = var.jwt_secret
            version = "latest"
          }
        }
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }

      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
      }
    }

    volumes {
      name = "cloudsql"
      cloud_sql_instance {
        instances = [var.cloudsql_connection_name]
      }
    }
  }
}

resource "google_cloud_run_v2_service_iam_member" "public_access" {
  project  = var.project_id
  location = google_cloud_run_v2_service.banking_api.location
  name     = google_cloud_run_v2_service.banking_api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# ── Subscriber Cloud Run ──────────────────────────────────────
resource "google_cloud_run_v2_service" "banking_subscriber" {
  name     = "banking-subscriber"
  location = var.region
  project  = var.project_id

  template {
    service_account = var.service_account

    scaling {
      min_instance_count = 0
      max_instance_count = 5
    }

    containers {
      image = "us-west1-docker.pkg.dev/${var.project_id}/banking-repo/banking-subscriber:${var.subscriber_image_tag}"

      ports {
        container_port = 8080
      }

      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }

      env {
        name  = "PUBSUB_SUBSCRIPTION"
        value = "transaction-events-sub"
      }

      env {
        name  = "DB_HOST"
        value = var.cloudsql_connection_name
      }

      env {
        name  = "DB_USER"
        value = "banking_user"
      }

      env {
        name  = "DB_NAME"
        value = "bank_db"
      }

      env {
        name  = "ENV"
        value = "production"
      }

      env {
        name = "DB_PASSWORD"
        value_source {
          secret_key_ref {
            secret  = var.db_password_secret
            version = "latest"
          }
        }
      }

      env {
        name = "SECRET_KEY"
        value_source {
          secret_key_ref {
            secret  = var.jwt_secret
            version = "latest"
          }
        }
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }

      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
      }
    }

    volumes {
      name = "cloudsql"
      cloud_sql_instance {
        instances = [var.cloudsql_connection_name]
      }
    }
  }
}

resource "google_cloud_run_v2_service_iam_member" "subscriber_public_access" {
  project  = var.project_id
  location = google_cloud_run_v2_service.banking_subscriber.location
  name     = google_cloud_run_v2_service.banking_subscriber.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}