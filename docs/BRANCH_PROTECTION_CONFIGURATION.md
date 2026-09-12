# Branch Protection Configuration

**Habot Connect FZCO — Hiring Project**
**Position:** Junior Cloud and Development Operations Engineer
**Candidate full name:** Anuradha
**Candidate electronic mail address:** anuradha@tecofize.com

---

## Why this document exists

A pipeline that can be merged around is a recommendation, not a gate.

The workflow in `.github/workflows/poka-yoke-build-gate.yml` fails closed on every check.
None of that matters if a person with write access can press "Merge without waiting for
requirements to be met", or push straight to `main`. The repository settings below are half of
the control, and the workflow is the other half. Presenting the workflow without them would be
presenting a lock with no door.

---

## Required settings on the `main` branch

| Setting | Value | Why |
| --- | --- | --- |
| Require a pull request before merging | Enabled | A direct push bypasses every check that runs on a pull request |
| Required approvals | 1 | The gate catches what is mechanical; a reviewer catches intent |
| Dismiss stale approvals on new commits | Enabled | An approval of the third commit is not an approval of the fourth |
| Require status checks to pass | Enabled | This is what makes the gate binding |
| Required status check | `Required status check` — **this job only** | See below |
| Require branches to be up to date before merging | Enabled | Two branches that each pass alone can fail together; this forces the merged state to be tested |
| Require conversation resolution | Enabled | An unresolved review comment is an open question |
| Require signed commits | Enabled | An unsigned commit has an unverified author |
| Require linear history | Enabled | A merge commit can silently contain changes neither parent reviewed |
| Do not allow bypassing the above | **Enabled** | Without this, every setting above is advisory for administrators |
| Allow force pushes | Disabled | A force push rewrites the history the secret scan read |
| Allow deletions | Disabled | — |

---

## Why exactly one required status check

It would seem safer to require all four gate jobs. It is not.

GitHub Actions **skips** a dependent job when its dependency fails, and a skipped job reports as
*neutral* rather than as a failure. A required check that is never reported can, depending on
configuration, be treated as satisfied.

The `required-status-check` job closes this. It runs with `if: always()`, so it runs even when
every gate before it failed, and it fails unless each gate reported the literal string
`success`. Cancelled, skipped and neutral are all failures to it.

It also carries a completeness assertion: it counts the gates that reported and requires that
count to be four. An engineer who adds a fifth gate job without adding it to the `needs` list
is caught by that assertion, which is what stops the required check from quietly becoming a
check of three gates out of five.

---

## The deployment environment

The `deploy-to-staging-estate` job declares `environment: production-staging`. That environment
must be configured in the repository settings with:

- **Required reviewers:** at least one named person outside the pull request author
- **Deployment branches:** `main` only
- **Wait timer:** 0 minutes

A green build is evidence that the code is correct. It is not a decision to change the estate.
A named person makes that decision, and the environment is where that requirement is enforced.

---

## Workload identity federation

The deploy job authenticates with `google-github-actions/auth@v2` using workload identity
federation, not a service account key file.

On the Google Cloud side the pool provider must restrict the attribute condition to this
repository — for example `assertion.repository == "habotconnect/learning-support-platform"`.
Without that condition, any repository on GitHub can exchange its token for a credential in the
Habot Connect project, which converts a key management improvement into a far worse problem.

---

## Setting this up with the command line

```bash
gh api --method PUT \
  repos/habotconnect/learning-support-platform/branches/main/protection \
  --input branch-protection-settings.json
```

The settings document is not committed here because it names the real repository and the real
reviewing team, and those belong in the platform repository rather than in a hiring submission.
