#!/usr/bin/env bash
# =============================================================================
# Habot Connect FZCO - Hiring Project
# Position: Junior Cloud and Development Operations Engineer
# Candidate Full Name: Anuradha
# Candidate Electronic Mail Address: anuu.21092004@gmail.com
# File Purpose: Demonstrate that the build gate fails closed on an insecure
#               commit, and passes on the clean tree.
# =============================================================================
#
# What this script proves
# -----------------------
# The project brief asks for a demonstration that the automated build gate
# triggers a fail closed status on an invalid or insecure commit. This script
# produces that demonstration reproducibly, on any machine, without needing a
# GitHub account.
#
# It runs the same checks that the pipeline runs, in the same order, twice:
#
#   Part one.   Against the committed tree. Every check must pass.
#   Part two.   Against a throwaway copy of the tree into which a deliberately
#               insecure commit has been made. Every affected check must fail.
#
# The insecure commit reproduces both halves of the incident described in the
# project brief: a credential held in plain text in application code, and a
# schema change made on one side only.
#
# The insecure file is written into a temporary directory that is deleted when
# the script exits. It is never committed to this repository, which is why this
# repository can itself pass the secret scan.

set -euo pipefail

REPOSITORY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEMONSTRATION_WORKSPACE="$(mktemp --directory)"
FAILURE_COUNT_IN_PART_ONE=0
PASS_COUNT_IN_PART_TWO=0

cleanup() {
  rm --recursive --force "${DEMONSTRATION_WORKSPACE}"
}
trap cleanup EXIT

announce_section() {
  echo ""
  echo "==============================================================================="
  echo "$1"
  echo "==============================================================================="
  echo ""
}

# -----------------------------------------------------------------------------
announce_section "PART ONE. The committed tree. Every check must pass."
# -----------------------------------------------------------------------------

cd "${REPOSITORY_ROOT}"

echo "--- Check one. Secret detection across the whole tree."
if gitleaks detect --source . --config .gitleaks.toml --no-git --redact --exit-code 1 \
  >/dev/null 2>&1; then
  echo "    RESULT: PASS. No credential found."
else
  echo "    RESULT: FAIL. A credential was found in the committed tree."
  FAILURE_COUNT_IN_PART_ONE=$((FAILURE_COUNT_IN_PART_ONE + 1))
fi

echo "--- Check two. Python formatting."
if black --check --quiet . >/dev/null 2>&1; then
  echo "    RESULT: PASS. The Python source is in canonical format."
else
  echo "    RESULT: FAIL. The Python source is not in canonical format."
  FAILURE_COUNT_IN_PART_ONE=$((FAILURE_COUNT_IN_PART_ONE + 1))
fi

echo "--- Check three. Python linting."
if flake8 . >/dev/null 2>&1; then
  echo "    RESULT: PASS. The linter reported nothing."
else
  echo "    RESULT: FAIL. The linter reported a finding."
  FAILURE_COUNT_IN_PART_ONE=$((FAILURE_COUNT_IN_PART_ONE + 1))
fi

echo "--- Check four. Schema consistency between the application and the warehouse."
if python3 scripts/assert_schema_consistency.py >/dev/null 2>&1; then
  echo "    RESULT: PASS. The application and the warehouse agree."
else
  echo "    RESULT: FAIL. The application and the warehouse disagree."
  FAILURE_COUNT_IN_PART_ONE=$((FAILURE_COUNT_IN_PART_ONE + 1))
fi

echo "--- Check five. The validation test suite."
if python3 -m pytest --quiet >/dev/null 2>&1; then
  echo "    RESULT: PASS. Every test passed."
else
  echo "    RESULT: FAIL. A test failed."
  FAILURE_COUNT_IN_PART_ONE=$((FAILURE_COUNT_IN_PART_ONE + 1))
fi

echo ""
echo "Part one summary: ${FAILURE_COUNT_IN_PART_ONE} check or checks failed."
if [[ "${FAILURE_COUNT_IN_PART_ONE}" -ne 0 ]]; then
  echo "The committed tree does not pass its own gate. The demonstration stops here."
  exit 1
fi
echo "The gate is OPEN for the committed tree. A commit of this tree may proceed."

# -----------------------------------------------------------------------------
announce_section "PART TWO. An insecure commit. Every affected check must fail."
# -----------------------------------------------------------------------------

cp --recursive "${REPOSITORY_ROOT}/." "${DEMONSTRATION_WORKSPACE}/"
cd "${DEMONSTRATION_WORKSPACE}"
rm --recursive --force .git
git init --quiet --initial-branch=main
git config user.email "demonstration@habot.io"
git config user.name "Fail Closed Demonstration"
git add --all
git commit --quiet --message "The clean tree, for comparison."

echo "Writing the insecure change that a junior developer might push."
echo ""
echo "The change does three things, each of which the gate must catch:"
echo "  1. It holds a credential in plain text in application code."
echo "  2. It is formatted incorrectly."
echo "  3. It adds a warehouse column without adding the matching field."
echo ""

# The credential below is assembled from parts at write time so that this
# script itself never contains a string with the shape of a credential. The
# assembled value is structurally valid and authenticates nothing.
CREDENTIAL_PREFIX="AIza"
CREDENTIAL_BODY="SyDEMOfakeKEY0000000000000000000000x"
ASSEMBLED_EXAMPLE_CREDENTIAL="${CREDENTIAL_PREFIX}${CREDENTIAL_BODY}"

cat > task-03-schema-mapping-and-data-validation/student_onboarding/notifier.py <<PYTHON_SOURCE
import requests
def send( parent_email,message ):
    api_key = "${ASSEMBLED_EXAMPLE_CREDENTIAL}"
    return requests.post("https://api.example.org/send",json={"key":api_key,"to":parent_email,"body":message})
PYTHON_SOURCE

python3 - <<'PYTHON_SOURCE'
import json
from pathlib import Path

schema_path = Path(
    "task-01-terraform-secure-staging-provisioning/schemas/"
    "student_onboarding_submissions_schema.json"
)
declared_columns = json.loads(schema_path.read_text(encoding="utf-8"))
declared_columns.append(
    {
        "name": "parent_marketing_preference",
        "type": "STRING",
        "mode": "NULLABLE",
        "maxLength": "32",
        "description": "Added to the warehouse without adding the field.",
    }
)
schema_path.write_text(json.dumps(declared_columns, indent=2), encoding="utf-8")
PYTHON_SOURCE

git add --all
git commit --quiet --message "Add a parent notifier and a marketing preference column."

echo "--- Gate one. Secret detection and quarantine."
if gitleaks detect --source . --config .gitleaks.toml --redact --exit-code 1 \
  >/dev/null 2>&1; then
  echo "    RESULT: PASSED, WHICH IS WRONG. The scanner did not find the credential."
  PASS_COUNT_IN_PART_TWO=$((PASS_COUNT_IN_PART_TWO + 1))
else
  echo "    RESULT: FAIL CLOSED. A credential was detected. The build is halted."
  echo "    The commit is quarantined and the credential must be rotated at its issuer."
fi

echo "--- Gate two. Python formatting."
if black --check --quiet . >/dev/null 2>&1; then
  echo "    RESULT: PASSED, WHICH IS WRONG. The formatter accepted malformed source."
  PASS_COUNT_IN_PART_TWO=$((PASS_COUNT_IN_PART_TWO + 1))
else
  echo "    RESULT: FAIL CLOSED. The source is not in canonical format."
fi

echo "--- Gate three. Python linting."
if flake8 . >/dev/null 2>&1; then
  echo "    RESULT: PASSED, WHICH IS WRONG. The linter accepted the new file."
  PASS_COUNT_IN_PART_TWO=$((PASS_COUNT_IN_PART_TWO + 1))
else
  echo "    RESULT: FAIL CLOSED. The linter reported a finding."
fi

echo "--- Gate four. Schema consistency."
if python3 scripts/assert_schema_consistency.py >/dev/null 2>&1; then
  echo "    RESULT: PASSED, WHICH IS WRONG. The schema mismatch was not detected."
  PASS_COUNT_IN_PART_TWO=$((PASS_COUNT_IN_PART_TWO + 1))
else
  echo "    RESULT: FAIL CLOSED. The application and the warehouse disagree."
  echo "    The exact disagreement reported by the gate:"
  python3 scripts/assert_schema_consistency.py 2>&1 | sed 's/^/      /' || true
fi

# -----------------------------------------------------------------------------
announce_section "OUTCOME"
# -----------------------------------------------------------------------------

if [[ "${PASS_COUNT_IN_PART_TWO}" -ne 0 ]]; then
  echo "DEMONSTRATION FAILED."
  echo "${PASS_COUNT_IN_PART_TWO} gate or gates admitted the insecure commit."
  exit 1
fi

echo "DEMONSTRATION SUCCEEDED."
echo ""
echo "The clean tree opened every gate."
echo "The insecure commit closed every gate it touched."
echo ""
echo "No gate in this system reports a warning and continues. A check either"
echo "passes or the build halts, which is what the phrase fail closed means."
