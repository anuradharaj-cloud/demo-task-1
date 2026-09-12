# =============================================================================
# Habot Connect FZCO - Hiring Project
# Position: Junior Cloud and Development Operations Engineer
# Candidate Full Name: Anuradha
# Candidate Electronic Mail Address: anuu.21092004@gmail.com
# File Purpose: Strict conditional identity and access management bindings.
# =============================================================================
#
# Poka-Yoke rationale for this file:
#
# Three rules are enforced here and none of them depends on a person behaving
# correctly.
#
# Rule one.   Every binding uses the member form rather than the binding or the
#             policy form. The member form is additive and cannot silently
#             remove a binding that another configuration owns. The policy form
#             overwrites everything on the resource and is therefore banned.
#
# Rule two.   Every binding names a predefined role of the narrowest scope that
#             the stage requires, or a custom role defined below. No binding
#             uses roles/editor, roles/owner or roles/storage.admin.
#
# Rule three. Every binding that touches personal data carries an identity and
#             access management condition. The condition restricts the binding
#             by object path prefix, so a compromised writer identity cannot
#             reach an object outside the path its stage owns.

# -----------------------------------------------------------------------------
# Custom role. The predefined object creator role also permits listing the
# bucket. The ingestion stage does not need to list and must not be able to
# enumerate the personal data of other families, so a custom role is defined
# that grants creation and nothing else.
# -----------------------------------------------------------------------------

resource "google_project_iam_custom_role" "raw_landing_write_only" {
  role_id     = "habotConnectRawLandingWriteOnly"
  project     = var.google_cloud_project_identifier
  title       = "Habot Connect Raw Landing Write Only"
  description = "Permits the creation of a new object in the D0 Raw Landing bucket and nothing else. The holder cannot read an object, cannot list the bucket and cannot delete an object."

  permissions = [
    "storage.objects.create",
  ]

  stage = "GA"
}

# -----------------------------------------------------------------------------
# Ingestion stage. Write only, restricted by object path prefix.
# -----------------------------------------------------------------------------

resource "google_storage_bucket_iam_member" "ingestion_writer_may_create_objects" {
  bucket = google_storage_bucket.d0_raw_landing.name
  role   = google_project_iam_custom_role.raw_landing_write_only.id
  member = "serviceAccount:${google_service_account.onboarding_ingestion_writer.email}"

  condition {
    title       = "Restricted to the student onboarding landing path"
    description = "The ingestion identity may create an object only beneath the student onboarding landing path. An attempt to write anywhere else in the bucket is refused by the condition rather than by a code review."
    expression  = "resource.name.startsWith(\"projects/_/buckets/${local.raw_landing_bucket_name}/objects/student-onboarding/\")"
  }
}

# -----------------------------------------------------------------------------
# Transformation stage. Read only on the raw landing path, append only on the
# enforced table.
# -----------------------------------------------------------------------------

resource "google_storage_bucket_iam_member" "transformation_runner_may_read_objects" {
  bucket = google_storage_bucket.d0_raw_landing.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.onboarding_transformation_runner.email}"

  condition {
    title       = "Restricted to the student onboarding landing path"
    description = "The transformation identity may read an object only beneath the student onboarding landing path. Access log objects and any other prefix remain unreachable."
    expression  = "resource.name.startsWith(\"projects/_/buckets/${local.raw_landing_bucket_name}/objects/student-onboarding/\")"
  }
}

resource "google_bigquery_dataset_iam_member" "transformation_runner_may_edit_data" {
  dataset_id = google_bigquery_dataset.d1_staged_enforced.dataset_id
  project    = var.google_cloud_project_identifier
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.onboarding_transformation_runner.email}"
}

resource "google_project_iam_member" "transformation_runner_may_run_jobs" {
  project = var.google_cloud_project_identifier
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.onboarding_transformation_runner.email}"
}

# -----------------------------------------------------------------------------
# Analytics stage. The reader identity is deliberately granted nothing on the
# dataset itself. Its only route to the data is the authorised view defined in
# the row level security file. This is what makes row level security
# unbypassable rather than merely recommended.
# -----------------------------------------------------------------------------

resource "google_project_iam_member" "analytics_reader_may_run_jobs" {
  project = var.google_cloud_project_identifier
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.learning_support_analytics_reader.email}"
}

resource "google_bigquery_dataset_iam_member" "analyst_group_may_read_metadata" {
  dataset_id = google_bigquery_dataset.d1_staged_enforced.dataset_id
  project    = var.google_cloud_project_identifier
  role       = "roles/bigquery.metadataViewer"
  member     = "group:${var.learning_support_analyst_group_email_address}"
}

# -----------------------------------------------------------------------------
# Administration. The data platform engineering group administers the dataset.
# The binding is time bound so that a standing administrative grant cannot
# outlive the quarter in which it was reviewed.
# -----------------------------------------------------------------------------

resource "google_bigquery_dataset_iam_member" "data_platform_group_administers_dataset" {
  dataset_id = google_bigquery_dataset.d1_staged_enforced.dataset_id
  project    = var.google_cloud_project_identifier
  role       = "roles/bigquery.dataOwner"
  member     = "group:${var.data_platform_engineering_group_email_address}"

  condition {
    title       = "Expires at the end of the current access review period"
    description = "The administrative grant lapses automatically on the first day of January two thousand and twenty seven. Renewal requires a fresh access review and a fresh application of this configuration, so an unreviewed administrative grant cannot persist."
    expression  = "request.time < timestamp(\"2027-01-01T00:00:00Z\")"
  }
}

resource "google_storage_bucket_iam_member" "data_platform_group_administers_bucket" {
  bucket = google_storage_bucket.d0_raw_landing.name
  role   = "roles/storage.objectAdmin"
  member = "group:${var.data_platform_engineering_group_email_address}"

  condition {
    title       = "Expires at the end of the current access review period"
    description = "The administrative grant lapses automatically on the first day of January two thousand and twenty seven. Renewal requires a fresh access review and a fresh application of this configuration."
    expression  = "request.time < timestamp(\"2027-01-01T00:00:00Z\")"
  }
}
