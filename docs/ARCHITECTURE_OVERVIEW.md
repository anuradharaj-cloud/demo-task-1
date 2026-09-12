# Architecture Overview and Logic Flow

**Habot Connect FZCO — Hiring Project**
**Position:** Junior Cloud and Development Operations Engineer
**Candidate full name:** Anuradha
**Candidate electronic mail address:** anuradha@tecofize.com

---

## The path one submission takes

```
  A parent or guardian submits the onboarding form
                    │
                    ▼
  ┌───────────────────────────────────────────────────────┐
  │  Django REST Framework application                    │
  │                                                       │
  │  StudentOnboardingSubmissionSerializer                │
  │    • fields built from the field contract             │
  │    • an unrecognised field is refused, not discarded  │
  │    • validate() delegates to the validation library   │
  └───────────────────────────┬───────────────────────────┘
                              │  every one of 74 rules answered yes
                              ▼
  ┌───────────────────────────────────────────────────────┐
  │  D0 Raw Landing                                       │
  │  habotconnect-d0-raw-landing-staging                  │
  │                                                       │
  │  uniform bucket level access · public access          │
  │  prevention enforced · customer managed key rotating  │
  │  every 90 days · versioned · access logged · objects  │
  │  deleted automatically after 30 days                  │
  │                                                       │
  │  writer: onboarding-ingestion-writer                  │
  │  one permission, one object path, no read, no list    │
  └───────────────────────────┬───────────────────────────┘
                              │
                              ▼
  ┌───────────────────────────────────────────────────────┐
  │  Transformation stage                                 │
  │                                                       │
  │  Runs the SAME validation library a second time, so   │
  │  the answer the parent received at submission and the │
  │  answer applied at load are produced by one piece of  │
  │  code and cannot diverge.                             │
  │                                                       │
  │  runner: onboarding-transform-runner                  │
  │  read the landing path, append to the table, nothing  │
  │  else — it cannot delete                              │
  └───────────────────────────┬───────────────────────────┘
                              │
                              ▼
  ┌───────────────────────────────────────────────────────┐
  │  D1 Staged and Enforced                               │
  │  d1_staged_enforced_staging                           │
  │  → student_onboarding_submissions                     │
  │                                                       │
  │  partitioned by day on the submission timestamp       │
  │  clustered by local authority and support category    │
  │  partition filter required on every query             │
  │  customer managed key · deletion protected            │
  │                                                       │
  │  Row level security, layer one:                       │
  │  a native row access policy filtering on the local    │
  │  authority the querying analyst is entitled to        │
  └───────────────────────────┬───────────────────────────┘
                              │
                              ▼
  ┌───────────────────────────────────────────────────────┐
  │  D1 Reporting Views                                   │
  │  → student_onboarding_submissions_reporting_view      │
  │                                                       │
  │  Row level security, layer two:                       │
  │  an authorised view. The reporting identity holds NO  │
  │  permission on the underlying table, so the view is   │
  │  its only route to the data. Direct identifiers of    │
  │  the child and of the parent are excluded entirely.   │
  │                                                       │
  │  reader: support-analytics-reader                     │
  └───────────────────────────────────────────────────────┘
```

---

## Why row level security is built in two independent layers

A control that exists in one layer only is a control that one mistake removes.

**Layer one** is the native BigQuery row access policy. It is attached to the table and applies
to every query against it, including one an engineer types into a console. Entitlement is read
from a table — `analyst_local_authority_entitlement` — rather than from a permission someone
granted by hand. Revoking access is then setting one boolean to false, which takes effect on
the next query and leaves an audit trail with a review reference attached.

**Layer two** is the authorised view. Authorising a view grants *the view*, not its readers, the
right to read the underlying table. That is what allows the analytics identity to hold no
permission on the table at all.

An engineer who deletes the row access policy still has the authorised view. An engineer who
mistakenly grants the analytics identity direct table access still has the row access policy.

---

## Why the raw landing bucket is write-only for the application

The ingestion identity can create objects and do nothing else — it cannot read what it wrote,
and cannot list the bucket.

This is the containment property that matters. If the Django application is compromised
tomorrow, the attacker gains the ability to *add* onboarding records. They do not gain the
ability to read a single existing family's data, and they cannot enumerate what is there. The
blast radius of a compromised web application is bounded by what that application's identity
can do, so the identity is given the narrowest capability that lets the application function.

---

## Why the same validation library runs twice

Running validation only at the application boundary means a payload that arrives by any other
route — a backfill, a migration, a manual load, a second service written later — reaches the
warehouse unvalidated.

Running it only at load means the parent gets no immediate feedback and a bad submission
occupies the raw landing bucket until someone investigates.

Running the *same code* at both points gives immediate feedback and an unbypassable boundary.
The important word is *same*: two implementations of the same rules drift, and the drift is
silent, which returns us to precisely the class of failure this project exists to remove.

---

## Where each layer's controls live

| Layer | Control | File |
| --- | --- | --- |
| Encryption | Customer managed key, 90 day rotation, destruction prevented | `main.tf` |
| Storage | Uniform access, public access prevention, versioning, lifecycle deletion, access logging | `main.tf` |
| Warehouse | Partitioning, clustering, required partition filter, deletion protection | `main.tf` |
| Identity | Three stage identities, one custom single-permission role | `service-accounts.tf`, `identity-and-access-management.tf` |
| Access conditions | Object path conditions, time bound administrative grants | `identity-and-access-management.tf` |
| Row level security | Native row access policy and authorised view | `row-level-security.tf` |
| Input validation | 74 yes or no rules, field limits, database check constraints | `dcyn_library/`, `student_onboarding/` |
| Schema integrity | Four direction consistency comparison | `scripts/assert_schema_consistency.py` |
| Delivery | Secret detection, formatting, linting, security scan, tests, required status check | `.github/workflows/poka-yoke-build-gate.yml` |
