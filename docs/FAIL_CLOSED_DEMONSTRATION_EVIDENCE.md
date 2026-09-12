# Fail Closed Demonstration — What It Proves

**Habot Connect FZCO — Hiring Project**
**Position:** Junior Cloud and Development Operations Engineer
**Candidate full name:** Anuradha
**Candidate electronic mail address:** anuradha@tecofize.com

---

## How to reproduce it

```bash
bash quarantine-demonstration/run_fail_closed_demonstration.sh
```

The captured output of a real run against the committed tree is in
`evidence/fail_closed_demonstration_transcript.txt`. It was not written by hand.

---

## What the demonstration does

It runs the same checks the pipeline runs, in the same order, twice.

**Part one — the committed tree.** Every check must pass. If the repository cannot open its own
gate, the demonstration stops there rather than proceeding to the interesting half. A gate that
the codebase itself cannot satisfy is a gate that will be turned off within a week.

**Part two — an insecure commit.** A throwaway copy of the tree is made, a deliberately
insecure change is committed into it, and every affected gate must now fail. The change
reproduces both halves of the incident described in the brief, plus a formatting violation:

1. A credential held in plain text in application code
2. Source that is not in canonical format
3. A warehouse column added without the matching application field

---

## The result

| Gate | Clean tree | Insecure commit |
| --- | --- | --- |
| Secret detection and quarantine | Pass | **Fail closed** — credential detected, build halted, commit quarantined |
| Python formatting | Pass | **Fail closed** — source not in canonical format |
| Python linting | Pass | **Fail closed** — finding reported |
| Schema consistency | Pass | **Fail closed** — application and warehouse disagree |
| Validation test suite (51 tests) | Pass | — |

The schema consistency gate named the exact disagreement:

> The warehouse declares a column named `parent_marketing_preference` which is neither declared
> in the field contract nor listed as a warehouse only column. Every column must be accounted
> for, so that this gate cannot silently stop covering part of the schema.

That is the point of the whole design. The gate did not say "something looks wrong". It named
the column, said which side declared it, said which side did not, and said what to do.

---

## Why the insecure file is not committed to this repository

The demonstration writes its insecure file into a temporary directory that is deleted when the
script exits, and commits it into a throwaway repository — never into this one.

Committing a deliberately bad file here, even as an example, would mean this repository could
never pass its own secret scan. The alternative would be adding an allow-list entry for it, and
an allow-list entry is exactly the mechanism by which a real credential eventually gets waved
through. The example credential is also assembled from two fragments at run time, so that no
string in this repository has the shape of a credential.

---

## What the demonstration does not prove

- It does not prove the GitHub Actions workflow syntax is correct. That is proved by a real run on GitHub, which requires the repository to exist there.
- It does not prove the Terraform provisions a correct estate. It proves the configuration is canonically formatted and parses. `terraform validate` against the real provider schema is step six of the verification list in the README and requires registry access.
- It does not prove branch protection is configured. That is a repository setting, documented in `docs/BRANCH_PROTECTION_CONFIGURATION.md`, and it is the half of the control that lives outside the code.

Stating these honestly is part of the submission. A demonstration that claims more than it
shows is the same species of problem as a linter that warns and continues.
