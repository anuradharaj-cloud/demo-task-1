# Task Two — The Poka-Yoke Automated Build Gate

**Candidate full name:** Anuradha
**Candidate electronic mail address:** anuu.21092004@gmail.com

---

## Where the files are, and why they are not in this folder

The deliverable for task two is the workflow file and its two configuration files. All three
live at the paths GitHub Actions and the tools themselves require, because a workflow placed
anywhere other than `.github/workflows/` does not run at all:

| File | Purpose |
| --- | --- |
| `../.github/workflows/poka-yoke-build-gate.yml` | The fail closed build gate |
| `../.gitleaks.toml` | Secret detection rules |
| `../.tflint.hcl` | Infrastructure linter rules |
| `../setup.cfg`, `../pyproject.toml` | Formatter, import sorter, linter and test runner configuration |
| `../requirements-development.txt` | Exactly pinned tool versions |
| `../scripts/assert_schema_consistency.py` | The schema consistency gate that gate four runs |
| `../quarantine-demonstration/run_fail_closed_demonstration.sh` | Reproducible proof that the gate fails closed |
| `../evidence/fail_closed_demonstration_transcript.txt` | The captured output of a real run |

Copying them into this folder to make the task numbering tidy would produce two copies of each
file, which is the exact failure this whole submission is built to prevent.

---

## The gate in one paragraph

Four gates run. Secret detection runs first and everything else depends on it, so a commit
carrying a credential never reaches a stage that could publish anything derived from it. The
infrastructure gate checks formatting, validates against the provider schema, lints, and
asserts that no forbidden role and no publicly reachable bucket is present. The application
gate checks formatting, import order, lint, security, and runs the test suite — then asserts
the suite was not empty. The schema gate compares the application field contract against the
warehouse table in four directions.

A fifth job, `required-status-check`, is the only job branch protection requires. It fails
unless every gate reported the literal result `success`, and it carries a completeness
assertion so that adding a gate without registering it halts the build.

Full reasoning: `../docs/GOLDEN_RULES_AND_POKA_YOKE_DESIGN.md`
Repository settings that make it binding: `../docs/BRANCH_PROTECTION_CONFIGURATION.md`
