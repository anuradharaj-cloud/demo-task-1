# =============================================================================
# Habot Connect FZCO - Hiring Project
# Position: Junior Cloud and Development Operations Engineer
# Candidate Full Name: Anuradha
# Candidate Electronic Mail Address: anuu.21092004@gmail.com
# File Purpose: Input variables with concrete declared values and validation.
# =============================================================================
#
# Poka-Yoke rationale for this file:
# Every variable carries a validation block. An operator who supplies a value
# that would produce an insecure or non-conforming estate is stopped by the
# plan itself, before any application programming interface call is made. There
# is no variable in this file that a person can leave empty and no variable that
# accepts a free-form string without a rule constraining it.

variable "google_cloud_project_identifier" {
  description = "Identifier of the Google Cloud project that hosts the staging estate for the Learning Support Assistant platform."
  type        = string
  default     = "habotconnect-lsa-platform-staging"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{4,28}[a-z0-9]$", var.google_cloud_project_identifier))
    error_message = "The project identifier must be between six and thirty characters, must begin with a lower case letter, and may contain only lower case letters, digits and hyphens."
  }

  validation {
    condition     = endswith(var.google_cloud_project_identifier, "-staging")
    error_message = "This configuration provisions the staging estate only. The project identifier must end with the suffix -staging so that it can never be applied against the production project by mistake."
  }
}

variable "google_cloud_region" {
  description = "Google Cloud region that holds every regional resource in the staging estate."
  type        = string
  default     = "europe-west2"

  validation {
    condition     = contains(["europe-west2"], var.google_cloud_region)
    error_message = "The learning support data of children resident in the United Kingdom is restricted to the London region, which is europe-west2. No other region is permitted by the data residency rule."
  }
}

variable "environment_name" {
  description = "Name of the deployment environment. Used as a suffix on every resource name and as a label on every resource."
  type        = string
  default     = "staging"

  validation {
    condition     = contains(["staging"], var.environment_name)
    error_message = "This configuration is scoped to the staging environment only."
  }
}

variable "data_platform_engineering_group_email_address" {
  description = "Electronic mail address of the Google Workspace group that administers the data platform."
  type        = string
  default     = "data-platform-engineering@habot.io"

  validation {
    condition     = can(regex("^[a-z0-9._-]+@habot[.]io$", var.data_platform_engineering_group_email_address))
    error_message = "Administrative access may be granted only to a group inside the habot.io domain. External domains are refused."
  }
}

variable "learning_support_analyst_group_email_address" {
  description = "Electronic mail address of the Google Workspace group whose members read the enforced analytics layer under row level security."
  type        = string
  default     = "learning-support-analysts@habot.io"

  validation {
    condition     = can(regex("^[a-z0-9._-]+@habot[.]io$", var.learning_support_analyst_group_email_address))
    error_message = "Analytical access may be granted only to a group inside the habot.io domain. External domains are refused."
  }
}

variable "raw_landing_retention_period_in_days" {
  description = "Number of days that a raw landing object is retained before the lifecycle rule deletes it."
  type        = number
  default     = 30

  validation {
    condition     = var.raw_landing_retention_period_in_days >= 7 && var.raw_landing_retention_period_in_days <= 90
    error_message = "Raw landing retention must be at least seven days so that an ingestion incident can be investigated, and at most ninety days so that personal data of children is not held longer than the stated retention policy."
  }
}

variable "staged_table_partition_expiration_in_days" {
  description = "Number of days after which a partition of the enforced onboarding table expires."
  type        = number
  default     = 365

  validation {
    condition     = var.staged_table_partition_expiration_in_days >= 90 && var.staged_table_partition_expiration_in_days <= 730
    error_message = "Partition expiry must be between ninety and seven hundred and thirty days to satisfy both the analytical reporting window and the retention policy ceiling."
  }
}

variable "key_rotation_period_in_seconds" {
  description = "Automatic rotation period of the customer managed encryption key, expressed in seconds."
  type        = string
  default     = "7776000s"

  validation {
    condition     = can(regex("^[0-9]+s$", var.key_rotation_period_in_seconds))
    error_message = "The rotation period must be expressed as a whole number of seconds followed by the letter s, for example 7776000s."
  }

  validation {
    condition     = tonumber(trimsuffix(var.key_rotation_period_in_seconds, "s")) <= 7776000
    error_message = "The encryption key must rotate at least once every ninety days, which is 7776000 seconds. A longer rotation period is refused."
  }
}
