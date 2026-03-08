resource "google_sql_database_instance" "banking_db" {
  name             = "banking-mysql"
  database_version = "MYSQL_8_0"
  region           = var.region
  project          = var.project_id

  settings {
    tier              = "db-f1-micro"
    availability_type = "ZONAL"
    disk_size         = 10
    disk_type         = "PD_SSD"

    backup_configuration {
      enabled            = true
      binary_log_enabled = true
      start_time         = "02:00"
    }

    ip_configuration {
      ipv4_enabled = true
      authorized_networks {
        name  = "allow-all-temp"
        value = "0.0.0.0/0"
      }
    }
  }

  deletion_protection = false
}

resource "google_sql_database" "bank_db" {
  name     = "bank_db"
  instance = google_sql_database_instance.banking_db.name
  project  = var.project_id
}

resource "google_sql_user" "db_user" {
  name     = "banking_user"
  instance = google_sql_database_instance.banking_db.name
  password = var.db_password
  project  = var.project_id
}