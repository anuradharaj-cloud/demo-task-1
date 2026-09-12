# The Golden Rules, and how each one is enforced

**Habot Connect FZCO — Hiring Project**
**Position:** Junior Cloud and Development Operations Engineer
**Candidate full name:** Anuradha
**Candidate electronic mail address:** anuradha@tecofize.com

---

## The test every rule in this document has to pass

A rule is only a Golden Rule if breaking it is **impossible**, not merely **discouraged**.

Anything enforced by a code review, a checklist, a wiki page or an onboarding conversation is a
recommendation. It works until somebody is tired, or new, or shipping at half past six on a
Friday. Each rule below names the mechanism that refuses the mistake, and the file where that
mechanism lives, so that a reviewer can check the claim rather than take it.

---

### Rule one. A credential cannot enter the repository

**Enforced by:** `.gitleaks.toml` and gate one of `.github/workflows/poka-yoke-build-gate.yml`

The scan runs with `fetch-depth: 0`, so it reads the whole commit history rather than the tip.
A credential committed on Tuesday and deleted on Wednesday is still recoverable from the
history and is still reported. The scan runs *first*, before any job that could publish a log
line, a cache entry or an artefact derived from the code.

A second, independent detector — Bandit — reads the same source for the code *patterns* that
hold credentials. The secret scanner looks for values shaped like a credential; Bandit looks
for the shape of the code around them. Either one alone has blind spots.

The absence of a scan report is treated as a failure. A scanner that exits zero because it
never ran is the exact failure this check exists to catch.

### Rule two. A credential cannot exist to be committed

**Enforced by:** the `deploy-to-staging-estate` job, which uses workload identity federation

There is no service account key file anywhere in this system. The pipeline exchanges its own
signed token for a short lived Google Cloud credential at deploy time. Rule one stops a key
from being committed; rule two removes the key.

### Rule three. No principal holds a permission its stage does not need

**Enforced by:** `service-accounts.tf` and `identity-and-access-management.tf`

Three identities, one for each stage, none spanning two stages. A single shared application
identity would force every binding to be the union of every permission the platform needs,
which is the condition that makes a compromised credential catastrophic rather than contained.

The ingestion identity holds a custom role granting exactly one permission,
`storage.objects.create`. The predefined object creator role also permits listing the bucket,
and an identity that can list the bucket can enumerate the families of other children.

### Rule four. A binding that touches personal data is scoped by condition

**Enforced by:** the `condition` block on every relevant binding

The ingestion and transformation bindings carry a condition restricting them to the
`student-onboarding/` object path. A compromised writer identity cannot reach an object outside
the path its stage owns. Administrative bindings carry a time condition that lapses on the
first day of January 2027, so an unreviewed administrative grant cannot quietly persist for
years.

### Rule five. A forbidden role cannot reach the main branch

**Enforced by:** the least privilege assertion in gate two

`roles/owner`, `roles/editor` and `roles/storage.admin` are searched for by name. No correct
configuration in this repository can need any of them. The search is cheap and the failure is
unambiguous.

### Rule six. A storage bucket cannot be public

**Enforced by:** the public access assertion in gate two

The assertion counts declared buckets and counts buckets with both
`public_access_prevention = "enforced"` and `uniform_bucket_level_access = true`, then requires
the counts to be equal. It also fails when it finds zero buckets, because an assertion with
nothing to assert against is not evidence of anything.

### Rule seven. The application and the warehouse cannot disagree

**Enforced by:** `scripts/assert_schema_consistency.py`, gate four

This is the direct answer to the second half of the incident. The gate compares in four
directions:

1. Every contract field exists as a warehouse column with matching type, mode and maximum length
2. Every warehouse column is accounted for by the contract or by the declared list of columns the transformation stage writes
3. The nested audit record agrees with the bounds the validation library is written to
4. Every declared warehouse-only column actually exists

Comparing in one direction only would let a column be added, or a field removed, without the
gate noticing. The gate writes nothing and repairs nothing: a gate that fixes the problem it
finds teaches engineers to ignore it.

### Rule eight. A limit is stated once

**Enforced by:** `dcyn_library/field_contract.py`

Every maximum length, numeric bound, pattern and permitted value list lives in that one file.
The Django model reads it. The serializer builds its fields from it. The validation library
generates its rules from it. The mapping workbook is generated from it. The schema gate
compares it against the warehouse.

There is no literal limit typed into the model or the serializer. An engineer cannot widen a
limit in one place, because there is no second place to widen.

### Rule nine. A field cannot exist without a rule

**Enforced by:** generation in `rules.py`, plus two assertions

Per-field rules are generated from the contract rather than written by hand. A field added to
the contract is a field with rules, automatically. A `FieldContract` that declares no
enforceable limit at all refuses to be constructed. The serializer asserts at import time that
its field list and the contract agree — an import that fails, fails the build.

### Rule ten. No validation outcome requires a judgement

**Enforced by:** the design of `rules.py` and `deconstruction.py`

Every one of the 74 rules answers a question admitting only yes and no. There is no score, no
severity, no warning and no override. A submission is accepted when every rule answers yes.

The evaluator runs every rule even after the first no, so the parent receives every correction
at once rather than one per resubmission, and so an auditor gets the complete record. Every
answer is written into the warehouse beside the row, so any acceptance can be reconstructed
years later.

A rule that raises an exception is recorded as *no*, never allowed to escape. An exception
escaping the validator would either halt ingestion or — far worse — be caught upstream and
treated as a pass.

### Rule eleven. A pipeline that can be merged around is not a gate

**Enforced by:** the `required-status-check` job and `docs/BRANCH_PROTECTION_CONFIGURATION.md`

Branch protection requires one job, and that job fails unless every gate reported the literal
result `success`. This closes a real gap: GitHub Actions *skips* a dependent job when its
dependency fails, and a skipped job reports as neutral rather than as a failure. A neutral
result can be read as satisfied.

The job also carries a completeness assertion. It counts the gates that reported and requires
the count to equal four. An engineer who adds a fifth gate without adding it to the required
check is caught immediately, which stops the required check from decaying into a check of a
subset of the gates.

---

## What this design deliberately does not do

Stating the limits honestly matters more than claiming completeness.

- **It does not scan for vulnerable dependencies.** Dependencies are pinned to exact versions, which makes the build reproducible but does not make it current. A production version of this system needs Dependabot or an equivalent, plus a gate on known vulnerabilities.
- **It does not run a policy engine over the Terraform plan.** The assertions in gate two are targeted greps. They catch the specific mistakes named above and nothing else. Open Policy Agent or Checkov would generalise this properly.
- **It does not test the Terraform against a real project.** `terraform validate` proves the configuration is correct against the provider schema. It does not prove the estate behaves as intended. Terratest against a throwaway project would close that gap.
- **The row access policy is applied by a BigQuery job rather than by a first class resource.** This keeps the policy statement in version control, which is the important property, but a job resource is one-shot by nature and the keeper checksum is what forces reapplication when the statement changes.

Each of these is a deliberate scope decision for a four-to-six hour project, not an oversight.
