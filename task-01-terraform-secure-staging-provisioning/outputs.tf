# =============================================================================
# Habot Connect FZCO - Hiring Project
# Position: Junior Cloud and Development Operations Engineer
# Candidate Full Name: Anuradha
# Candidate Electronic Mail Address: anuradha@tecofize.com
# File Purpose: Outputs consumed by the application and by the pipeline.
# =============================================================================
#
# Poka-Yoke rationale for this file:
# No output exposes a secret. The application discovers the names of the
# resources it must address from these outputs rather than from a value typed
# into a configuration file, which is how a name drifts out of step with the
# estate and how an application ends up writing to the wrong bucket.

output "raw_landing_bucket_name" {
  description = "Name of the D0 Raw Landing storage bucket that the ingestion stage writes to."
  value       = google_storage_bucket.d0_raw_landing.name
}

output "raw_landing_object_path_prefix" {
  description = "The only object path prefix that the ingestion identity is permitted to write to. The application must construct every object name beneath this prefix."
  value       = "student-onboarding/"
}

output "staged_enforced_dataset_identifier" {
  description = "Identifier of the D1 Staged and Enforced BigQuery dataset."
  value       = google_bigquery_dataset.d1_staged_enforced.dataset_id
}

output "enforced_onboarding_table_identifier" {
  description = "Fully qualified identifier of the enforced student onboarding table."
  value       = "${var.google_cloud_project_identifier}.${google_bigquery_dataset.d1_staged_enforced.dataset_id}.${google_bigquery_table.student_onboarding_submissions.table_id}"
}

output "reporting_view_identifier" {
  description = "Fully qualified identifier of the authorised reporting view. This is the only object that the reporting layer is permitted to query."
  value       = "${var.google_cloud_project_identifier}.${google_bigquery_dataset.d1_reporting_views.dataset_id}.${google_bigquery_table.student_onboarding_reporting_view.table_id}"
}

output "ingestion_writer_service_account_email_address" {
  description = "Electronic mail address of the write only ingestion service account."
  value       = google_service_account.onboarding_ingestion_writer.email
}

output "transformation_runner_service_account_email_address" {
  description = "Electronic mail address of the transformation service account."
  value       = google_service_account.onboarding_transformation_runner.email
}

output "analytics_reader_service_account_email_address" {
  description = "Electronic mail address of the reporting service account."
  value       = google_service_account.learning_support_analytics_reader.email
}

output "customer_managed_encryption_key_identifier" {
  description = "Identifier of the customer managed encryption key protecting both the raw landing bucket and the enforced dataset. This is a resource name and not key material."
  value       = google_kms_crypto_key.learning_support_data.id
}
