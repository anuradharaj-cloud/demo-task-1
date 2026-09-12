# Habot Connect FZCO — Hiring Project

**Position:** Junior Cloud and Development Operations Engineer (Google Cloud Platform, Django, React)
**Candidate full name:** Anuradha
**Candidate electronic mail address:** anuradha@tecofize.com
**Submitted:** September 2026

---

## The one idea this submission is built on

The brief describes an incident: a junior developer pushed an update that left unencrypted
credentials in raw application code and triggered a database schema mismatch that broke
downstream analytics.

Both halves of that incident were possible because a person was trusted to remember something.
Remember not to paste the key. Remember to update the warehouse when you change the model.

Every control in this repository replaces a thing a person has to remember with a thing a
machine refuses to allow. That is what Poka-Yoke means here, and it is the only design
principle used.

| The thing a person had to remember | What replaces it in this repository |
| --- | --- |
| Do not commit a credential | A secret scan over the full commit history that halts the build and quarantines the commit |
| Do not grant more access than needed | Conditional identity and access management bindings scoped to one object path, and a custom role that grants exactly one permission |
| Keep the serializer and the warehouse in step | A schema consistency gate that compares them in four directions on every commit |
| Use the right field limits | One field contract that the serializer, the database model, the validation library and the mapping workbook all read |
| Judge whether a submission is acceptable | 74 rules, each answering a question whose only possible answers are yes and no |
| Run the formatter before pushing | A formatting check that fails the build rather than reformatting silently |

---

## What is in this repository

```
habot-connect-hiring-project/
├── task-01-terraform-secure-staging-provisioning/   Task one. Infrastructure as code.
│   ├── main.tf                                      Storage bucket and BigQuery dataset
│   ├── identity-and-access-management.tf            Conditional least privilege bindings
│   ├── row-level-security.tf                        Two independent row level controls
│   ├── service-accounts.tf                          One identity for each pipeline stage
│   ├── variables.tf                                 Every variable carries a validation rule
│   ├── outputs.tf, versions.tf, terraform.tfvars
│   └── schemas/                                     The warehouse table schemas
│
├── .github/workflows/poka-yoke-build-gate.yml       Task two. The fail closed build gate.
├── .gitleaks.toml                                   Secret detection rules
├── .tflint.hcl                                      Infrastructure linter rules
│
├── task-03-schema-mapping-and-data-validation/      Task three. Validation.
│   ├── dcyn_library/
│   │   ├── field_contract.py                        The single source of every limit
│   │   ├── rules.py                                 The yes or no rule set
│   │   └── deconstruction.py                        The evaluator
│   ├── student_onboarding/
│   │   ├── models.py                                Django model, limits read from contract
│   │   └── serializers.py                           Django REST Framework model serializer
│   ├── sample_payloads/                             One accepted, one refused
│   └── tests/                                       51 tests
│
├── scripts/
│   ├── assert_schema_consistency.py                 The schema consistency gate
│   └── build_schema_mapping_workbook.py             Generates the mapping workbook
│
├── quarantine-demonstration/
│   └── run_fail_closed_demonstration.sh             Proves the gate fails closed
│
├── evidence/
│   └── fail_closed_demonstration_transcript.txt     The captured output of that proof
│
├── schema-mapping/
│   └── student_onboarding_schema_mapping.xlsx       Six worksheets, wrap text throughout
│
├── presentation/                                    The slide deck
└── docs/                                            Design notes and operating instructions
```

---

## How to verify every claim in this submission

Nothing below requires a Google Cloud account or a billing account.

```bash
# 1. Install the pinned development dependencies.
python3 -m pip install --requirement requirements-development.txt

# 2. Run the full validation test suite. Expect 51 passed.
python3 -m pytest

# 3. Run the schema consistency gate. Expect agreement.
python3 scripts/assert_schema_consistency.py

# 4. Prove the build gate fails closed. Expect DEMONSTRATION SUCCEEDED.
bash quarantine-demonstration/run_fail_closed_demonstration.sh

# 5. Check the infrastructure formatting.
cd task-01-terraform-secure-staging-provisioning
terraform fmt -check -recursive -diff

# 6. Validate the infrastructure against the real provider schema.
#    This step needs network access to the provider registry.
terraform init -backend=false
terraform validate
```

Steps two, three and four were run on the committed tree and their real output is recorded in
`evidence/fail_closed_demonstration_transcript.txt`.

---

## Declared values for the staging estate

There is no placeholder anywhere in this repository. Every value below is a declared value for
the staging environment, and every one of them is constrained by a validation rule that refuses
anything else.

| Item | Declared value |
| --- | --- |
| Project identifier | `habotconnect-lsa-platform-staging` |
| Region | `europe-west2` (London) |
| Raw landing bucket | `habotconnect-d0-raw-landing-staging` |
| Enforced dataset | `d1_staged_enforced_staging` |
| Reporting view dataset | `d1_reporting_views_staging` |
| Encryption key | `learning-support-data-encryption-key`, rotating every 90 days |
| Ingestion identity | `onboarding-ingestion-writer` |
| Transformation identity | `onboarding-transform-runner` |
| Reporting identity | `support-analytics-reader` |

The region is London because the platform serves learning support assistants working with
children resident in the United Kingdom, and the personal data of those children is kept in the
United Kingdom. The `google_cloud_region` variable refuses every other value.

---

## Further reading in this repository

- `docs/ARCHITECTURE_OVERVIEW.md` — the data flow and the reasoning behind each stage
- `docs/GOLDEN_RULES_AND_POKA_YOKE_DESIGN.md` — the eleven structural rules, and how each is enforced
- `docs/BRANCH_PROTECTION_CONFIGURATION.md` — the repository settings without which a pipeline is only a suggestion
- `docs/FAIL_CLOSED_DEMONSTRATION_EVIDENCE.md` — what the demonstration proves and what it does not
