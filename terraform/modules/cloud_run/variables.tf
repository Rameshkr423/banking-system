
# ── Add this instead ──────────────────────────────────────
variable "image_tag" {
  description = "Docker image tag injected by Cloud Build (git commit SHA)"
  type        = string
  default     = "latest"
}

variable "project_id" {}
variable "region" {}
variable "db_password_secret" {}
variable "jwt_secret" {}
variable "service_account" {}
variable "cloudsql_connection_name" {
  description = "Cloud SQL connection name"
  type        = string
}
