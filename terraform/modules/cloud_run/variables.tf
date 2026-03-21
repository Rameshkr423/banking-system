variable "image_tag" {
  description = "Docker image tag injected by Cloud Build"
  type        = string
  default     = "latest"
}

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
}

variable "db_password_secret" {
  description = "Secret Manager secret name for DB password"
  type        = string
}

variable "jwt_secret" {
  description = "Secret Manager secret name for JWT secret"
  type        = string
}

variable "service_account" {
  description = "Service account email for Cloud Run"
  type        = string
}

variable "cloudsql_connection_name" {
  description = "Cloud SQL connection name"
  type        = string
}

variable "service_name" {
  description = "Cloud Run service name"
  type        = string
  default     = "banking-api"
}

variable "container_port" {
  description = "Container port"
  type        = number
  default     = 8080
}