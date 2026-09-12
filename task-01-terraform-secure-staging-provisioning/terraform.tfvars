# =============================================================================
# Habot Connect FZCO - Hiring Project
# Position: Junior Cloud and Development Operations Engineer
# Candidate Full Name: Anuradha
# Candidate Electronic Mail Address: anuu.21092004@gmail.com
# File Purpose: Declared values for the staging estate.
# =============================================================================
#
# Every value in this file is a real declared value for the staging estate.
# There is no value in this file that an operator is expected to substitute
# before use. This file contains no credential of any kind, and the secret
# scanning stage of the build gate treats any credential appearing here as a
# build failure.

google_cloud_project_identifier               = "habotconnect-lsa-platform-staging"
google_cloud_region                           = "europe-west2"
environment_name                              = "staging"
data_platform_engineering_group_email_address = "data-platform-engineering@habot.io"
learning_support_analyst_group_email_address  = "learning-support-analysts@habot.io"
raw_landing_retention_period_in_days          = 30
staged_table_partition_expiration_in_days     = 365
key_rotation_period_in_seconds                = "7776000s"
