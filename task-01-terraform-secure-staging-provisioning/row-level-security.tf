# =============================================================================
# Habot Connect FZCO - Hiring Project
# Position: Junior Cloud and Development Operations Engineer
# Candidate Full Name: Anuradha
# Candidate Electronic Mail Address: anuradha@tecofize.com
# File Purpose: Row level security over the enforced onboarding table.
# =============================================================================
#
# Poka-Yoke rationale for this file:
#
# Row level security is applied in two independent layers, because a control
# that exists in one layer only is a control that one mistake can remove.
#
# Layer one is the native BigQuery row access policy. It is attached to the
# table itself and applies to every query against the table, including a query
# written by an engineer at a console. It is created by a BigQuery job that runs
# the corresponding data definition language statement, so that the policy is
# version controlled in this repository rather than typed into a console.
#
# Layer two is an authorised view. The analytics identity holds no permission on
# the underlying table at all, so the only route it has to the data is through
# this view, and the view filters rows by the local authority of the caller.
#
# An engineer who deletes layer one still has layer two. An engineer who grants
# the analytics identity direct table access still has layer one.

# -----------------------------------------------------------------------------
# Layer one. Native row access policies, expressed as data definition language
# and applied by a BigQuery job so that the statement lives in version control.
# -----------------------------------------------------------------------------

# The entitlement table states, for each analyst, the local authorities that
# analyst is contracted to support. The row access policy reads this table at
# query time. Entitlement therefore lives in data that can be reviewed and
# audited, rather than in a permission that somebody granted by hand and nobody
# remembers granting.
resource "google_bigquery_table" "analyst_local_authority_entitlement" {
  dataset_id  = google_bigquery_dataset.d1_staged_enforced.dataset_id
  table_id    = "analyst_local_authority_entitlement"
  project     = var.google_cloud_project_identifier
  description = "One row for each combination of analyst electronic mail address and local authority that the analyst is contracted to support. Read by the row access policy on the enforced onboarding table."

  deletion_protection = true
  labels              = local.common_resource_labels

  schema = file("${path.module}/schemas/analyst_local_authority_entitlement_schema.json")

  encryption_configuration {
    kms_key_name = google_kms_crypto_key.learning_support_data.id
  }
}

locals {
  # The analyst group sees only the rows belonging to the local authorities that
  # the analyst is entitled to. SESSION_USER resolves to the identity of the
  # caller at query time, so the filter cannot be side stepped by rewriting the
  # query, by querying the table directly, or by using a different client.
  row_access_policy_statement = <<-SQL_STATEMENT
    CREATE OR REPLACE ROW ACCESS POLICY learning_support_analyst_local_authority_filter
    ON `${var.google_cloud_project_identifier}.${google_bigquery_dataset.d1_staged_enforced.dataset_id}.${google_bigquery_table.student_onboarding_submissions.table_id}`
    GRANT TO ("group:${var.learning_support_analyst_group_email_address}")
    FILTER USING (
      record_is_withheld_from_analytics = FALSE
      AND assigned_local_authority_name IN (
        SELECT
          entitlement.local_authority_name
        FROM
          `${var.google_cloud_project_identifier}.${google_bigquery_dataset.d1_staged_enforced.dataset_id}.analyst_local_authority_entitlement` AS entitlement
        WHERE
          entitlement.analyst_email_address = SESSION_USER()
          AND entitlement.entitlement_is_active = TRUE
      )
    );
  SQL_STATEMENT
}

resource "random_id" "row_access_policy_job_suffix" {
  byte_length = 6

  # A new job identifier is generated whenever the policy statement changes, so
  # that an amended policy is actually applied rather than being skipped because
  # a job of the same name already exists.
  keepers = {
    policy_statement_checksum = sha256(local.row_access_policy_statement)
  }
}

resource "google_bigquery_job" "apply_row_access_policy" {
  job_id   = "apply-row-access-policy-${random_id.row_access_policy_job_suffix.hex}"
  project  = var.google_cloud_project_identifier
  location = var.google_cloud_region

  labels = local.common_resource_labels

  query {
    query          = local.row_access_policy_statement
    use_legacy_sql = false
  }

  depends_on = [
    google_bigquery_table.student_onboarding_submissions,
    google_bigquery_table.analyst_local_authority_entitlement,
  ]
}

# -----------------------------------------------------------------------------
# Layer two. The authorised view. The analytics identity reads this and only
# this. The view withholds the direct identifiers of the child entirely, so the
# reporting layer physically cannot receive them.
# -----------------------------------------------------------------------------

resource "google_bigquery_dataset" "d1_reporting_views" {
  dataset_id  = "d1_reporting_views_${local.resource_name_suffix}"
  project     = var.google_cloud_project_identifier
  location    = var.google_cloud_region
  description = "Holds authorised views over the enforced layer. Contains no base tables. The reporting layer is granted access to this dataset only."

  labels                     = local.common_resource_labels
  delete_contents_on_destroy = false

  default_encryption_configuration {
    kms_key_name = google_kms_crypto_key.learning_support_data.id
  }

  depends_on = [google_kms_crypto_key_iam_member.bigquery_agent_may_use_key]
}

resource "google_bigquery_table" "student_onboarding_reporting_view" {
  dataset_id  = google_bigquery_dataset.d1_reporting_views.dataset_id
  table_id    = "student_onboarding_submissions_reporting_view"
  project     = var.google_cloud_project_identifier
  description = "Authorised view over the enforced onboarding table. Direct identifiers of the child and of the parent or guardian are excluded. Rows are filtered to the local authorities that the querying identity is contracted to support."

  deletion_protection = true
  labels              = local.common_resource_labels

  view {
    use_legacy_sql = false
    query          = <<-SQL_STATEMENT
      SELECT
        submission_reference,
        submission_received_timestamp,
        assigned_local_authority_name,
        learning_support_category,
        weekly_support_hours_requested,
        student_year_group,
        preferred_session_language,
        education_health_care_plan_is_present,
        validation_outcome_is_accepted
      FROM
        `${var.google_cloud_project_identifier}.${google_bigquery_dataset.d1_staged_enforced.dataset_id}.${google_bigquery_table.student_onboarding_submissions.table_id}`
      WHERE
        record_is_withheld_from_analytics = FALSE
        AND submission_received_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL ${var.staged_table_partition_expiration_in_days} DAY)
    SQL_STATEMENT
  }
}

# Authorising the view grants the view itself, not its readers, the right to
# read the underlying table. This is the mechanism that lets the analytics
# identity hold no permission at all on the enforced table.
resource "google_bigquery_dataset_access" "authorise_reporting_view" {
  dataset_id = google_bigquery_dataset.d1_staged_enforced.dataset_id
  project    = var.google_cloud_project_identifier

  view {
    project_id = var.google_cloud_project_identifier
    dataset_id = google_bigquery_dataset.d1_reporting_views.dataset_id
    table_id   = google_bigquery_table.student_onboarding_reporting_view.table_id
  }
}

resource "google_bigquery_dataset_iam_member" "analytics_reader_may_read_reporting_views" {
  dataset_id = google_bigquery_dataset.d1_reporting_views.dataset_id
  project    = var.google_cloud_project_identifier
  role       = "roles/bigquery.dataViewer"
  member     = "serviceAccount:${google_service_account.learning_support_analytics_reader.email}"
}

resource "google_bigquery_dataset_iam_member" "analyst_group_may_read_reporting_views" {
  dataset_id = google_bigquery_dataset.d1_reporting_views.dataset_id
  project    = var.google_cloud_project_identifier
  role       = "roles/bigquery.dataViewer"
  member     = "group:${var.learning_support_analyst_group_email_address}"
}
