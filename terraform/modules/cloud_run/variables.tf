variable "project_id" {}
variable "region" {}
variable "image" {}
variable "db_password_secret" {}
variable "jwt_secret" {}
variable "service_account" {}
variable "cloudsql_connection_name" {
  description = "Cloud SQL connection name"
  type        = string
}
