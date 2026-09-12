# =============================================================================
# Habot Connect FZCO - Hiring Project
# Position: Junior Cloud and Development Operations Engineer
# Candidate Full Name: Anuradha
# Candidate Electronic Mail Address: anuu.21092004@gmail.com
# File Purpose: Linter configuration for the infrastructure as code gate.
# =============================================================================
#
# Poka-Yoke rationale for this file:
# force is set to false so that a finding fails the build. Setting it to true
# would turn every finding into a warning, which is the quiet way a gate becomes
# a suggestion. disabled_by_default is also false, so a rule that the ruleset
# adds in a future version is active the moment it arrives rather than waiting
# for somebody to opt in.

config {
  format              = "compact"
  call_module_type    = "all"
  force               = false
  disabled_by_default = false
}

plugin "terraform" {
  enabled = true
  preset  = "all"
}

plugin "google" {
  enabled = true
  version = "0.31.0"
  source  = "github.com/terraform-linters/tflint-ruleset-google"
}

# Every variable must carry a description. A variable without a description is
# a variable that the next engineer guesses at.
rule "terraform_documented_variables" {
  enabled = true
}

# Every output must carry a description, for the same reason.
rule "terraform_documented_outputs" {
  enabled = true
}

# Every variable must declare a type. An untyped variable accepts anything,
# which defeats the validation blocks that sit beside it.
rule "terraform_typed_variables" {
  enabled = true
}

# Resource and variable names must use the underscore separated form so that a
# reader never has to work out which convention a given file follows.
rule "terraform_naming_convention" {
  enabled = true
  format  = "snake_case"
}

# Provider versions must be pinned. This duplicates the constraint already
# written in versions.tf on purpose, because a control that exists in one place
# only is removed by one edit.
rule "terraform_required_providers" {
  enabled = true
}

rule "terraform_required_version" {
  enabled = true
}

# Unused declarations are removed rather than tolerated. An unused variable is
# usually the remains of a control that was taken out.
rule "terraform_unused_declarations" {
  enabled = true
}

rule "terraform_unused_required_providers" {
  enabled = true
}

# Comments must use the number sign form rather than the double slash form, so
# that the file reads consistently.
rule "terraform_comment_syntax" {
  enabled = true
}

rule "terraform_deprecated_interpolation" {
  enabled = true
}

rule "terraform_deprecated_index" {
  enabled = true
}
