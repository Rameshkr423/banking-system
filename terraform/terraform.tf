@'
project_id  = "banking-system-prod"
region      = "us-west1"
zone        = "us-west1-a"
db_password = "Banking@Secure123"
'@ | Out-File -FilePath "terraform.tfvars" -Encoding UTF8