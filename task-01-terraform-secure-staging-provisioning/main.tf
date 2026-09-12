# =============================================================================
# Habot Connect FZCO - Hiring Project
# Position: Junior Cloud and Development Operations Engineer
# Candidate Full Name: Anuradha
# Candidate Electronic Mail Address: anuradha@tecofize.com
# File Purpose: Secure provisioning of the D0 Raw Landing storage bucket and the
#               D1 Staged and Enforced BigQuery dataset for the Learning Support
#               Assistant platform staging estate.
# =============================================================================
#
# Data flow that this file provisions:
#
#   Django REST Framework application
#            |
#            v
#   D0 Raw Landing            Google Cloud Storage bucket, customer managed
#   (untrusted, write only)   encryption, no reader other than the transform
#            |                 service account, thirty day lifecycle deletion
#            v
#   Transformation stage      Runs the deconstructed yes or no validation
#            |                 library before any row is permitted to land
#            v
#   D1 Staged and Enforced    BigQuery dataset, partitioned and clustered,
#   (trusted, read only)      protected by row level security
#
# The single governing rule of this file is that no principal holds a permission
# that its stage of the pipeline does not require. A principal that writes to
# D0 cannot read from D0. A principal that reads D1 cannot write to it.

locals {
  resource_name_suffix = var.environment_name

  raw_landing_bucket_name = "habotconnect-d0-raw-landing-${local.resource_name_suffix}"
  access_log_bucket_name  = "habotconnect-d0-access-logs-${local.resource_name_suffix}"
  staged_dataset_name     = "d1_staged_enforced_${local.resource_name_suffix}"
  onboarding_table_name   = "student_onboarding_submissions"

  # Labels are applied to every resource so that cost attribution and data
  # classification can be queried rather than remembered by a person.
  common_resource_labels = {
    application            = "learning-support-assistant-platform"
    environment            = var.environment_name
    data_classification    = "personal-data-of-children"
    managed_by             = "terraform"
    owning_team            = "data-platform-engineering"
    regulatory_scope       = "united-kingdom-data-protection"
    provisioning_blueprint = "secure-staging-provisioning"
  }

  required_google_cloud_services = [
    "storage.googleapis.com",
    "bigquery.googleapis.com",
    "cloudkms.googleapis.com",
    "pubsub.googleapis.com",
    "iam.googleapis.com",
  ]
}

# -----------------------------------------------------------------------------
# Section one. Enable only the application programming interfaces that the
# blueprint actually uses. Disabling on destroy is deliberately refused because
# turning off a service in a shared project would break unrelated workloads.
# -----------------------------------------------------------------------------

resource "google_project_service" "required_service" {
  for_each = toset(local.required_google_cloud_services)

  project = var.google_cloud_project_identifier
  service = each.value

  disable_on_destroy         = false
  disable_dependent_services = false
}

# -----------------------------------------------------------------------------
# Section two. Customer managed encryption. The incident that this project
# responds to involved credentials held in plain text. The corresponding control
# at the storage layer is that Habot Connect holds the encryption key rather
# than relying on the default Google managed key, and that the key rotates on a
# schedule that no person has to remember.
# -----------------------------------------------------------------------------

resource "google_kms_key_ring" "data_protection" {
  name     = "habotconnect-data-protection-${local.resource_name_suffix}"
  location = var.google_cloud_region
  project  = var.google_cloud_project_identifier

  depends_on = [google_project_service.required_service]
}

resource "google_kms_crypto_key" "learning_support_data" {
  name     = "learning-support-data-encryption-key"
  key_ring = google_kms_key_ring.data_protection.id
  purpose  = "ENCRYPT_DECRYPT"

  rotation_period = var.key_rotation_period_in_seconds
  labels          = local.common_resource_labels

  version_template {
    algorithm        = "GOOGLE_SYMMETRIC_ENCRYPTION"
    protection_level = "SOFTWARE"
  }

  # An encryption key that can be destroyed can take every object encrypted by
  # it with it. Destruction is blocked at the state level as well as by the
  # organisation policy.
  lifecycle {
    prevent_destroy = true
  }
}

data "google_storage_project_service_account" "cloud_storage_agent" {
  project    = var.google_cloud_project_identifier
  depends_on = [google_project_service.required_service]
}

data "google_bigquery_default_service_account" "bigquery_agent" {
  project    = var.google_cloud_project_identifier
  depends_on = [google_project_service.required_service]
}

resource "google_kms_crypto_key_iam_member" "cloud_storage_agent_may_use_key" {
  crypto_key_id = google_kms_crypto_key.learning_support_data.id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member        = "serviceAccount:${data.google_storage_project_service_account.cloud_storage_agent.email_address}"
}

resource "google_kms_crypto_key_iam_member" "bigquery_agent_may_use_key" {
  crypto_key_id = google_kms_crypto_key.learning_support_data.id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member        = "serviceAccount:${data.google_bigquery_default_service_account.bigquery_agent.email}"
}

# -----------------------------------------------------------------------------
# Section three. The D0 Raw Landing bucket and its access log bucket.
# -----------------------------------------------------------------------------

resource "google_storage_bucket" "access_logs" {
  name     = local.access_log_bucket_name
  project  = var.google_cloud_project_identifier
  location = var.google_cloud_region

  storage_class               = "STANDARD"
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  force_destroy               = false
  labels                      = local.common_resource_labels

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 400
    }
    action {
      type = "Delete"
    }
  }
}

resource "google_storage_bucket" "d0_raw_landing" {
  name     = local.raw_landing_bucket_name
  project  = var.google_cloud_project_identifier
  location = var.google_cloud_region

  storage_class = "STANDARD"
  labels        = local.common_resource_labels

  # Uniform bucket level access removes per object access control lists.
  # Per object access control lists are the classic way an engineer grants
  # public read to one file and never notices. Removing the mechanism removes
  # the mistake.
  uniform_bucket_level_access = true

  # Public access prevention is set to enforced rather than inherited so that an
  # organisation policy change made elsewhere cannot silently open this bucket.
  public_access_prevention = "enforced"

  # Refusing forced destruction means an operator cannot delete a populated
  # bucket of children's data with a single command.
  force_destroy = false

  versioning {
    enabled = true
  }

  encryption {
    default_kms_key_name = google_kms_crypto_key.learning_support_data.id
  }

  logging {
    log_bucket        = google_storage_bucket.access_logs.name
    log_object_prefix = "d0-raw-landing-access"
  }

  # Raw personal data is deleted automatically once it has been promoted to the
  # enforced layer. Nobody has to remember to clean it up.
  lifecycle_rule {
    condition {
      age = var.raw_landing_retention_period_in_days
    }
    action {
      type = "Delete"
    }
  }

  lifecycle_rule {
    condition {
      num_newer_versions = 3
    }
    action {
      type = "Delete"
    }
  }

  soft_delete_policy {
    retention_duration_seconds = 604800
  }

  depends_on = [google_kms_crypto_key_iam_member.cloud_storage_agent_may_use_key]
}

# -----------------------------------------------------------------------------
# Section four. The D1 Staged and Enforced BigQuery dataset and its table.
# -----------------------------------------------------------------------------

resource "google_bigquery_dataset" "d1_staged_enforced" {
  dataset_id  = local.staged_dataset_name
  project     = var.google_cloud_project_identifier
  location    = var.google_cloud_region
  description = "Enforced analytics layer for the Learning Support Assistant platform. Every row in this dataset has passed the deconstructed yes or no validation library. No process writes to this dataset directly from the application."

  labels = local.common_resource_labels

  # Refusing deletion of a populated dataset is the counterpart of refusing
  # forced destruction on the bucket.
  delete_contents_on_destroy = false

  # Seven days of time travel gives an operator a recovery window after an
  # incorrect transformation without holding personal data indefinitely.
  max_time_travel_hours = "168"

  default_encryption_configuration {
    kms_key_name = google_kms_crypto_key.learning_support_data.id
  }

  default_partition_expiration_ms = var.staged_table_partition_expiration_in_days * 24 * 60 * 60 * 1000

  depends_on = [google_kms_crypto_key_iam_member.bigquery_agent_may_use_key]
}

resource "google_bigquery_table" "student_onboarding_submissions" {
  dataset_id  = google_bigquery_dataset.d1_staged_enforced.dataset_id
  table_id    = local.onboarding_table_name
  project     = var.google_cloud_project_identifier
  description = "One row for each student onboarding submission that has been accepted by the deconstructed yes or no validation library. The column set is identical to the field set of the Django REST Framework serializer."

  labels = local.common_resource_labels

  # Refusing table deletion protects the enforced layer from an accidental
  # destroy of the whole configuration.
  deletion_protection = true

  schema = file("${path.module}/schemas/student_onboarding_submissions_schema.json")

  time_partitioning {
    type                     = "DAY"
    field                    = "submission_received_timestamp"
    require_partition_filter = true
    expiration_ms            = var.staged_table_partition_expiration_in_days * 24 * 60 * 60 * 1000
  }

  clustering = [
    "assigned_local_authority_name",
    "learning_support_category",
  ]

  encryption_configuration {
    kms_key_name = google_kms_crypto_key.learning_support_data.id
  }
}
