terraform {
  backend "gcs" {
    bucket = "banking-tfstate-banking-system-prod"  # hardcoded — no vars allowed in backend
    prefix = "terraform/state"
  }
}