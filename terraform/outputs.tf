output "cloud_run_url" {
  description = "Banking API URL"
  value       = module.cloud_run.api_url
}

output "cloud_sql_connection" {
  description = "Cloud SQL Connection Name"
  value       = module.cloud_sql.connection_name
}

output "vm_ip" {
  description = "Frontend VM IP"
  value       = module.vm.vm_ip
}

output "api_image_path" {
  description = "Docker image push path"
  value       = "us-west1-docker.pkg.dev/banking-system-prod/banking-repo/banking-api:latest"
}