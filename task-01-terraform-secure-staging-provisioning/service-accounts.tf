# =============================================================================
# Habot Connect FZCO - Hiring Project
# Position: Junior Cloud and Development Operations Engineer
# Candidate Full Name: Anuradha
# Candidate Electronic Mail Address: anuradha@tecofize.com
# File Purpose: Workload identities, one for each stage of the pipeline.
# =============================================================================
#
# Poka-Yoke rationale for this file:
# There is one identity for each stage and no identity spans two stages. This is
# what makes the least privilege bindings in the identity and access management
# file expressible at all. A single shared application service account would
# force every binding to be the union of every permission the platform needs,
# which is the condition under which the original incident became possible.

resource "google_service_account" "onboarding_ingestion_writer" {
  account_id   = "onboarding-ingestion-writer"
  project      = var.google_cloud_project_identifier
  display_name = "Onboarding Ingestion Writer"
  description  = "Used by the Django REST Framework application to write an accepted onboarding payload into the D0 Raw Landing bucket. This identity cannot read any object it has written and cannot reach BigQuery at all."

  depends_on = [google_project_service.required_service]
}

resource "google_service_account" "onboarding_transformation_runner" {
  account_id   = "onboarding-transformation-runner"
  project      = var.google_cloud_project_identifier
  display_name = "Onboarding Transformation Runner"
  description  = "Used by the transformation stage to read from the D0 Raw Landing bucket, apply the deconstructed yes or no validation library, and append accepted rows to the D1 enforced table. This identity cannot delete data and cannot modify the table schema."

  depends_on = [google_project_service.required_service]
}

resource "google_service_account" "learning_support_analytics_reader" {
  account_id   = "learning-support-analytics-reader"
  project      = var.google_cloud_project_identifier
  display_name = "Learning Support Analytics Reader"
  description  = "Used by the reporting layer to query the D1 enforced dataset through the authorised view only. This identity has no access to the underlying table and no access to the D0 Raw Landing bucket."

  depends_on = [google_project_service.required_service]
}
