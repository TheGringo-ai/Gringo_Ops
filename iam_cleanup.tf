terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  # This will use your gcloud credentials
}

variable "project_id" {
  type        = string
  description = "Your GCP Project ID"
}

variable "project_number" {
  type        = string
  description = "Your GCP Project Number"
}

locals {
  default_compute_sa = "${var.project_number}-compute@developer.gserviceaccount.com"
}

# Remove overly broad roles
resource "google_project_iam_binding" "remove_editor" {
  project = var.project_id
  role    = "roles/editor"

  members = []
}

resource "google_project_iam_member" "remove_cloud_run_admin" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${local.default_compute_sa}"
  lifecycle {
    prevent_destroy = false
  }
}

resource "google_project_iam_member" "remove_log_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${local.default_compute_sa}"
  lifecycle {
    prevent_destroy = false
  }
}

resource "google_project_iam_member" "remove_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${local.default_compute_sa}"
  lifecycle {
    prevent_destroy = false
  }
}
