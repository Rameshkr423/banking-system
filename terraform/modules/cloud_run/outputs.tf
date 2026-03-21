# Only reference resources INSIDE this module
output "service_url" {
  description = "Cloud Run service URL"
  value       = google_cloud_run_v2_service.banking_api.uri
}

output "service_name" {
  description = "Cloud Run service name"
  value       = google_cloud_run_v2_service.banking_api.name
}