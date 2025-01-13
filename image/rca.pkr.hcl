variable "elastic_stack_version" {
  type    = string
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

source "googlecompute" "rca" {
  project_id = var.project_id
  region     = var.region
  zone       = var.zone

  image_family = regex_replace("rca-${regex_replace(var.elastic_stack_version, "\\+.*$", "")}", "[^a-zA-Z0-9_-]", "-")
  image_name   = regex_replace("rca-${var.elastic_stack_version}-${var.build}", "[^a-zA-Z0-9_-]", "-")

  source_image_family             = regex_replace("elastic-${regex_replace(var.elastic_stack_version, "\\+.*$", "")}", "[^a-zA-Z0-9_-]", "-")
  machine_type                    = "n2-standard-8"
  disk_size                       = 100
  disable_default_service_account = true

  ssh_username = "root"
}

build {
    sources = ["source.googlecompute.rca"]

    provisioner "shell" {
        script = "rca/rca-install.sh"
    }
}
