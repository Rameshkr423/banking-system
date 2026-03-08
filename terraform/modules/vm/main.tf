resource "google_compute_instance" "frontend_vm" {
  name         = "banking-frontend-vm"
  machine_type = "e2-micro"
  zone         = var.zone
  project      = var.project_id
  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
      size  = 20
    }
  }
  network_interface {
    network = "default"
    access_config {}
  }
  metadata_startup_script = <<-EOF
    #!/bin/bash
    apt-get update -y
    apt-get install -y nginx
    systemctl enable nginx
    systemctl start nginx
  EOF
  tags = ["http-server", "https-server"]
}
resource "google_compute_firewall" "allow_http" {
  name    = "banking-allow-http"
  network = "default"
  project = var.project_id
  allow {
    protocol = "tcp"
    ports    = ["80", "443"]
  }
  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["http-server", "https-server"]
}
