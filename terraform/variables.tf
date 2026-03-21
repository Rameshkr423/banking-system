variable "project_id" {
  description = "GCP Project ID"
  default     = "banking-system-prod"
}

variable "region" {
  description = "GCP Region"
  default     = "us-west1"
}

variable "zone" {
  description = "GCP Zone"
  default     = "us-west1-a"
}

variable "db_password" {
  description = "Cloud SQL DB Password"
  sensitive   = true
}

variable "api_image" {
  description = "Docker image for Cloud Run"
  default     = "us-west1-docker.pkg.dev/banking-system-prod/banking-repo/banking-api:latest"
}


variable "image_tag" {
  description = "Docker image tag from CI/CD (git commit SHA)"
  type        = string
  default     = "latest"
}

variable "subscriber_image_tag" {
  description = "Subscriber image tag from CI/CD (git commit SHA)"
  type        = string
  default     = "latest"
}

