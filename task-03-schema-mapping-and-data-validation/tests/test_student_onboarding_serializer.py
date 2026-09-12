"""Habot Connect FZCO - Hiring Project.

Position: Junior Cloud and Development Operations Engineer.
Candidate Full Name: Anuradha.
Candidate Electronic Mail Address: anuu.21092004@gmail.com.

File purpose: tests of the Django REST Framework model serializer.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from dcyn_library import FIELD_CONTRACTS
from student_onboarding.serializers import (
    CONTRACT_FIELD_NAMES,
    StudentOnboardingSubmissionSerializer,
)

SAMPLE_PAYLOAD_DIRECTORY = Path(__file__).resolve().parent.parent / "sample_payloads"


def load_sample_payload(file_name: str) -> dict:
    """Return one sample payload from disk."""
    with (SAMPLE_PAYLOAD_DIRECTORY / file_name).open(encoding="utf-8") as payload_file:
        return json.load(payload_file)


@pytest.fixture()
def accepted_payload() -> dict:
    """Return a payload that the serializer accepts."""
    return load_sample_payload("accepted_student_onboarding_payload.json")


def test_the_serializer_declares_every_contract_field() -> None:
    """A field in the contract must appear in the serializer."""
    serializer = StudentOnboardingSubmissionSerializer()
    assert set(serializer.fields.keys()) == set(CONTRACT_FIELD_NAMES)


def test_the_serializer_declares_no_extra_field() -> None:
    """A field in the serializer must appear in the contract."""
    serializer = StudentOnboardingSubmissionSerializer()
    contract_names = {contract.payload_field_name for contract in FIELD_CONTRACTS}
    assert set(serializer.fields.keys()) <= contract_names


def test_every_limit_reaches_the_serializer() -> None:
    """A limit declared in the contract must be present on the field."""
    serializer = StudentOnboardingSubmissionSerializer()
    for contract in FIELD_CONTRACTS:
        field = serializer.fields[contract.payload_field_name]

        if contract.minimum_permitted_number is not None:
            assert (
                getattr(field, "min_value", None) == contract.minimum_permitted_number
            )
        if contract.maximum_permitted_number is not None:
            assert (
                getattr(field, "max_value", None) == contract.maximum_permitted_number
            )
        if contract.permitted_values is not None:
            assert set(getattr(field, "choices", {}).keys()) == set(
                contract.permitted_values
            )


def test_a_mandatory_field_is_marked_required() -> None:
    """A mandatory field must not be optional on the serializer."""
    serializer = StudentOnboardingSubmissionSerializer()
    for contract in FIELD_CONTRACTS:
        field = serializer.fields[contract.payload_field_name]
        assert field.required == contract.value_is_mandatory


def test_a_valid_payload_is_accepted(accepted_payload: dict) -> None:
    """The reference payload must pass serializer validation."""
    serializer = StudentOnboardingSubmissionSerializer(data=accepted_payload)
    assert serializer.is_valid(), serializer.errors


def test_an_unrecognised_field_is_refused_not_discarded(
    accepted_payload: dict,
) -> None:
    """An unknown key must produce an error rather than be silently dropped."""
    payload = copy.deepcopy(accepted_payload)
    payload["reviewer_discretionary_note"] = "Approved on the nod."
    serializer = StudentOnboardingSubmissionSerializer(data=payload)
    assert serializer.is_valid() is False
    assert "reviewer_discretionary_note" in serializer.errors


def test_a_value_over_the_maximum_length_is_refused(accepted_payload: dict) -> None:
    """A name longer than the column would be truncated on load."""
    payload = copy.deepcopy(accepted_payload)
    payload["student_given_name"] = "A" * 61
    serializer = StudentOnboardingSubmissionSerializer(data=payload)
    assert serializer.is_valid() is False
    assert "student_given_name" in serializer.errors


def test_a_number_outside_the_range_is_refused(accepted_payload: dict) -> None:
    """A year group outside the permitted range must be refused."""
    payload = copy.deepcopy(accepted_payload)
    payload["student_year_group"] = 14
    serializer = StudentOnboardingSubmissionSerializer(data=payload)
    assert serializer.is_valid() is False
    assert "student_year_group" in serializer.errors


def test_a_value_outside_the_permitted_list_is_refused(
    accepted_payload: dict,
) -> None:
    """A language outside the permitted list must be refused."""
    payload = copy.deepcopy(accepted_payload)
    payload["preferred_session_language"] = "Not a permitted language"
    serializer = StudentOnboardingSubmissionSerializer(data=payload)
    assert serializer.is_valid() is False
    assert "preferred_session_language" in serializer.errors


def test_a_missing_mandatory_field_is_refused(accepted_payload: dict) -> None:
    """A mandatory field that is absent must be refused."""
    payload = copy.deepcopy(accepted_payload)
    del payload["home_postal_code"]
    serializer = StudentOnboardingSubmissionSerializer(data=payload)
    assert serializer.is_valid() is False
    assert "home_postal_code" in serializer.errors


def test_a_malformed_reference_is_refused(accepted_payload: dict) -> None:
    """A submission reference of the wrong form must be refused."""
    payload = copy.deepcopy(accepted_payload)
    payload["submission_reference"] = "HCSO-2026-09-08-4F2A9C1D"
    serializer = StudentOnboardingSubmissionSerializer(data=payload)
    assert serializer.is_valid() is False
    assert "submission_reference" in serializer.errors


def test_a_cross_field_failure_is_reported(accepted_payload: dict) -> None:
    """The serializer must apply the validation library, not only field rules."""
    payload = copy.deepcopy(accepted_payload)
    payload["education_health_care_plan_is_present"] = False
    serializer = StudentOnboardingSubmissionSerializer(data=payload)
    assert serializer.is_valid() is False
    assert "non_field_errors" in serializer.errors


def test_a_payload_that_is_not_an_object_is_refused() -> None:
    """A list must be refused with an error rather than raise an exception."""
    serializer = StudentOnboardingSubmissionSerializer(data=["not", "an", "object"])
    assert serializer.is_valid() is False
