output "connection_name" {
  value = google_sql_database_instance.banking_db.connection_name
}

output "db_ip" {
  value = google_sql_database_instance.banking_db.public_ip_address
}