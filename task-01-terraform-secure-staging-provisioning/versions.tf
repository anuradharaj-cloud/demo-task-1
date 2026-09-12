# =============================================================================
# Habot Connect FZCO - Hiring Project
# Position: Junior Cloud and Development Operations Engineer
# Candidate Full Name: Anuradha
# Candidate Electronic Mail Address: anuu.21092004@gmail.com
# File Purpose: Pinned provider and language versions for the staging estate.
# =============================================================================
#
# Poka-Yoke rationale for this file:
# Unpinned versions are a silent failure mode. A provider that upgrades itself
# between two runs can change a default and quietly widen access. Every version
# below is pinned to a bounded range so that the same configuration produces the
# same estate on every machine and on every pipeline run.

terraform {
  required_version = ">= 1.9.0, < 2.0.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 6.14.0, < 7.0.0"
    }
    random = {
      source  = "hashicorp/random"
      version = ">= 3.6.0, < 4.0.0"
    }
  }

  # Remote state is mandatory. Local state files have been the cause of
  # credential leakage in many organisations because they are written in plain
  # text and are easy to commit by accident. The bucket below is created and
  # managed outside this configuration by the platform bootstrap process.
  backend "gcs" {
    bucket = "habotconnect-terraform-remote-state-staging"
    prefix = "learning-support-platform/secure-staging-provisioning"
  }
}

provider "google" {
  project = var.google_cloud_project_identifier
  region  = var.google_cloud_region
}
