"""Habot Connect FZCO - Hiring Project.

Position: Junior Cloud and Development Operations Engineer.
Candidate Full Name: Anuradha.
Candidate Electronic Mail Address: anuradha@tecofize.com.

File purpose: minimal Django configuration so that the serializer can be tested
without a running database or a deployed application.

Poka-Yoke rationale for this file
---------------------------------
The test suite must be runnable by anybody who has cloned the repository, with
no setup step that a person has to remember. A validation control that is only
testable on a correctly prepared machine is a control that stops being tested.

The secret key below is generated at import time and exists only inside the test
process. It is not a credential, it authenticates nothing, and it is never the
same twice. It is written this way rather than as a literal so that no string in
this repository has the shape of a credential.
"""

from __future__ import annotations

import secrets

import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=False,
        SECRET_KEY=secrets.token_urlsafe(48),
        USE_TZ=True,
        TIME_ZONE="UTC",
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "rest_framework",
            "student_onboarding",
        ],
        DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        REST_FRAMEWORK={
            # An unauthenticated default would let a view ship without anybody
            # noticing that it is open. The default is closed.
            "DEFAULT_PERMISSION_CLASSES": [
                "rest_framework.permissions.IsAuthenticated",
            ],
        },
    )
    django.setup()
