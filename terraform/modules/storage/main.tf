resource "google_storage_bucket" "banking_logs" {
  name          = "banking-logs-${var.project_id}"
  location      = var.region
  project       = var.project_id
  force_destroy = true
  uniform_bucket_level_access = true
  lifecycle_rule {
    condition { age = 90 }
    action { type = "Delete" }
  }
}
resource "google_storage_bucket" "banking_cdn" {
  name          = "banking-cdn-${var.project_id}"
  location      = var.region
  project       = var.project_id
  force_destroy = true
  website {
    main_page_suffix = "index.html"
    not_found_page   = "404.html"
  }
}
resource "google_storage_bucket_iam_member" "cdn_public" {
  bucket = google_storage_bucket.banking_cdn.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}
