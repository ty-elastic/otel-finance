variable "k3s_version" {
  type = string
}

variable "project_id" {
	type = string
}

variable "region" {
	type = string
	default = "us-central1"
}

variable "zone" {
	type = string
	default = "us-central1-a"
}

variable "build" {
	type = string
	default = "latest"
}

packer {
  required_plugins {
    googlecompute = {
      source  = "github.com/hashicorp/googlecompute"
      version = "~> 1"
    }
  }
}

source "googlecompute" "k3s" {
  project_id = var.project_id
  region     = var.region
  zone       = var.zone

  image_family = regex_replace("k3s-${regex_replace(var.k3s_version, "\\+.*$", "")}", "[^a-zA-Z0-9_-]", "-")
  image_name   = regex_replace("k3s-${var.k3s_version}-${var.build}", "[^a-zA-Z0-9_-]", "-")

  source_image_family             = "ubuntu-2204-lts"
  machine_type                    = "n2-standard-8"
  disk_size                       = 100
  disable_default_service_account = true

  ssh_username = "root"
}

build {
  sources = ["source.googlecompute.k3s"]

  provisioner "shell" {
    script = "k3s/k3s-install.sh"
    environment_vars = [
      "K3S_VERSION=${var.k3s_version}"
    ]
  }

  provisioner "file" {
    sources = [
      "k3s/k3s.service",
      "k3s/kubectl-proxy.service",
      "k3s/kube-dashboard.service",
    ]
    destination = "/etc/systemd/system/"
  }

  provisioner "file" {
    source      = "k3s/k3s-start.sh"
    destination = "/usr/local/bin/k3s-start.sh"
  }

  provisioner "file" {
    source      = "k3s/start.sh"
    destination = "/usr/bin/start.sh"
  }

  provisioner "shell" {
    inline = ["mkdir -p /opt/kube-dashboard"]
  }

  provisioner "file" {
    sources = [
      "k3s/dashboard.yml",
      "k3s/dashboard-sa.yml",
    ]
    destination = "/opt/kube-dashboard/"
  }
}
