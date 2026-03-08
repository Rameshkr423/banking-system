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
      image = var.image

      ports {
        container_port = 8080
      }

      env {
        name  = "DB_HOST"
        value = var.db_connection
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