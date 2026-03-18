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

      # ✅ FIX: DB_HOST must be the Cloud SQL connection name (not a socket path).
      # config.py builds the socket path as:
      #   ?unix_socket=/cloudsql/{DB_HOST}
      # So DB_HOST should be just: project:region:instance
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

      # ✅ FIX: Tell config.py to use the Unix socket path (production mode)
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
