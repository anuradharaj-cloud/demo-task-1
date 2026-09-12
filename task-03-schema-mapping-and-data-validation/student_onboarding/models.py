"""Habot Connect FZCO - Hiring Project.

Position: Junior Cloud and Development Operations Engineer.
Candidate Full Name: Anuradha.
Candidate Electronic Mail Address: anuradha@tecofize.com.

File purpose: the Django model behind the student onboarding serializer.

Poka-Yoke rationale for this file
---------------------------------
Not one limit in this file is typed as a literal. Every maximum length, every
numeric bound, every pattern and every choice list is read from the field
contract. An engineer who widens a limit here without widening it in the
contract cannot do so, because there is nothing here to widen. The database
constraint, the serializer validation and the warehouse column therefore cannot
disagree.
"""

from __future__ import annotations

from typing import List

from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models

from dcyn_library.field_contract import FIELD_CONTRACTS_BY_NAME


def _contract(field_name: str):
    """Return the contract of one field, refusing an unknown field name."""
    if field_name not in FIELD_CONTRACTS_BY_NAME:
        raise KeyError(
            "The field named "
            + field_name
            + " is not declared in the field contract. A model field that has "
            + "no contract cannot be validated and is therefore refused."
        )
    return FIELD_CONTRACTS_BY_NAME[field_name]


def _maximum_length(field_name: str) -> int:
    return int(_contract(field_name).maximum_character_length)


def _pattern_validators(field_name: str) -> List[RegexValidator]:
    contract = _contract(field_name)
    return [
        RegexValidator(
            regex=str(contract.regular_expression_pattern),
            message=(
                "The value of "
                + field_name
                + " must match its required form, which is "
                + str(contract.regular_expression_explanation)
            ),
        )
    ]


def _numeric_validators(field_name: str) -> List[object]:
    contract = _contract(field_name)
    return [
        MinValueValidator(int(contract.minimum_permitted_number)),
        MaxValueValidator(int(contract.maximum_permitted_number)),
    ]


def _choices(field_name: str) -> List[tuple]:
    contract = _contract(field_name)
    return [(value, value) for value in tuple(contract.permitted_values or ())]


class StudentOnboardingSubmission(models.Model):
    """One onboarding submission made by a parent or guardian."""

    submission_reference = models.CharField(
        max_length=_maximum_length("submission_reference"),
        unique=True,
        validators=_pattern_validators("submission_reference"),
        help_text=_contract("submission_reference").field_description,
    )
    submission_received_timestamp = models.DateTimeField(
        help_text=_contract("submission_received_timestamp").field_description,
    )
    student_given_name = models.CharField(
        max_length=_maximum_length("student_given_name"),
        validators=_pattern_validators("student_given_name"),
        help_text=_contract("student_given_name").field_description,
    )
    student_family_name = models.CharField(
        max_length=_maximum_length("student_family_name"),
        validators=_pattern_validators("student_family_name"),
        help_text=_contract("student_family_name").field_description,
    )
    student_date_of_birth = models.DateField(
        help_text=_contract("student_date_of_birth").field_description,
    )
    student_year_group = models.PositiveSmallIntegerField(
        validators=_numeric_validators("student_year_group"),
        help_text=_contract("student_year_group").field_description,
    )
    parent_or_guardian_full_name = models.CharField(
        max_length=_maximum_length("parent_or_guardian_full_name"),
        validators=_pattern_validators("parent_or_guardian_full_name"),
        help_text=_contract("parent_or_guardian_full_name").field_description,
    )
    parent_or_guardian_email_address = models.CharField(
        max_length=_maximum_length("parent_or_guardian_email_address"),
        validators=_pattern_validators("parent_or_guardian_email_address"),
        help_text=_contract("parent_or_guardian_email_address").field_description,
    )
    parent_or_guardian_telephone_number = models.CharField(
        max_length=_maximum_length("parent_or_guardian_telephone_number"),
        validators=_pattern_validators("parent_or_guardian_telephone_number"),
        help_text=_contract("parent_or_guardian_telephone_number").field_description,
    )
    home_postal_code = models.CharField(
        max_length=_maximum_length("home_postal_code"),
        validators=_pattern_validators("home_postal_code"),
        help_text=_contract("home_postal_code").field_description,
    )
    assigned_local_authority_name = models.CharField(
        max_length=_maximum_length("assigned_local_authority_name"),
        choices=_choices("assigned_local_authority_name"),
        help_text=_contract("assigned_local_authority_name").field_description,
    )
    school_unique_reference_number = models.CharField(
        max_length=_maximum_length("school_unique_reference_number"),
        validators=_pattern_validators("school_unique_reference_number"),
        help_text=_contract("school_unique_reference_number").field_description,
    )
    learning_support_category = models.CharField(
        max_length=_maximum_length("learning_support_category"),
        choices=_choices("learning_support_category"),
        help_text=_contract("learning_support_category").field_description,
    )
    weekly_support_hours_requested = models.PositiveSmallIntegerField(
        validators=_numeric_validators("weekly_support_hours_requested"),
        help_text=_contract("weekly_support_hours_requested").field_description,
    )
    preferred_session_language = models.CharField(
        max_length=_maximum_length("preferred_session_language"),
        choices=_choices("preferred_session_language"),
        help_text=_contract("preferred_session_language").field_description,
    )
    education_health_care_plan_is_present = models.BooleanField(
        help_text=_contract("education_health_care_plan_is_present").field_description,
    )
    education_health_care_plan_reference = models.CharField(
        max_length=_maximum_length("education_health_care_plan_reference"),
        null=True,
        blank=True,
        validators=_pattern_validators("education_health_care_plan_reference"),
        help_text=_contract("education_health_care_plan_reference").field_description,
    )
    data_processing_consent_is_given = models.BooleanField(
        help_text=_contract("data_processing_consent_is_given").field_description,
    )
    record_is_withheld_from_analytics = models.BooleanField(
        default=False,
        help_text=_contract("record_is_withheld_from_analytics").field_description,
    )

    class Meta:
        app_label = "student_onboarding"
        db_table = "student_onboarding_submission"
        verbose_name = "student onboarding submission"
        verbose_name_plural = "student onboarding submissions"
        constraints = [
            # The database refuses a row without consent. The serializer refuses
            # it too. Two independent refusals are deliberate: an engineer who
            # writes to the table with a management command bypasses the
            # serializer but cannot bypass the constraint.
            models.CheckConstraint(
                condition=models.Q(data_processing_consent_is_given=True),
                name="consent_to_processing_must_be_given",
            ),
            # The plan reference is present exactly when a plan is held. Stated
            # as a constraint so that the invariant survives any route into the
            # table.
            models.CheckConstraint(
                condition=(
                    models.Q(
                        education_health_care_plan_is_present=True,
                        education_health_care_plan_reference__isnull=False,
                    )
                    | models.Q(
                        education_health_care_plan_is_present=False,
                        education_health_care_plan_reference__isnull=True,
                    )
                ),
                name="plan_reference_present_exactly_when_plan_is_held",
            ),
        ]

    def __str__(self) -> str:
        """Return the submission reference, never a name of a child."""
        return str(self.submission_reference)
