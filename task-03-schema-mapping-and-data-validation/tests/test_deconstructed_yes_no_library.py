"""Habot Connect FZCO - Hiring Project.

Position: Junior Cloud and Development Operations Engineer.
Candidate Full Name: Anuradha.
Candidate Electronic Mail Address: anuradha@tecofize.com.

File purpose: tests of the deconstructed yes or no validation library.

Every test pins the evaluation instant. A test that read the current clock would
pass today and fail next week, and a test that fails for reasons unrelated to
the code is a test that engineers learn to ignore.
"""

from __future__ import annotations

import copy
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from dcyn_library import (
    FIELD_CONTRACTS,
    DeconstructedYesNoEvaluator,
    evaluate_student_onboarding_payload,
)
from dcyn_library.field_contract import (
    MAXIMUM_RULE_IDENTIFIER_LENGTH,
    MAXIMUM_RULE_QUESTION_LENGTH,
    FieldContract,
)

SAMPLE_PAYLOAD_DIRECTORY = Path(__file__).resolve().parent.parent / "sample_payloads"

PINNED_EVALUATION_INSTANT = datetime(2026, 9, 9, 12, 0, 0, tzinfo=timezone.utc)


def load_sample_payload(file_name: str) -> dict:
    """Return one sample payload from disk."""
    with (SAMPLE_PAYLOAD_DIRECTORY / file_name).open(encoding="utf-8") as payload_file:
        return json.load(payload_file)


@pytest.fixture()
def accepted_payload() -> dict:
    """Return a payload that every rule answers yes to."""
    return load_sample_payload("accepted_student_onboarding_payload.json")


@pytest.fixture()
def refused_payload() -> dict:
    """Return a payload that many rules answer no to."""
    return load_sample_payload("refused_student_onboarding_payload.json")


def test_the_rule_set_is_not_empty() -> None:
    """A library with no rules would accept everything."""
    evaluator = DeconstructedYesNoEvaluator()
    assert evaluator.rule_count > 0


def test_every_rule_identifier_is_unique() -> None:
    """An audit must attribute each answer to exactly one rule."""
    evaluator = DeconstructedYesNoEvaluator()
    identifiers = evaluator.rule_identifiers
    assert len(identifiers) == len(set(identifiers))


def test_every_contract_field_has_at_least_one_rule() -> None:
    """No field may exist in the contract without a rule examining it."""
    evaluator = DeconstructedYesNoEvaluator()
    identifiers = evaluator.rule_identifiers
    for contract in FIELD_CONTRACTS:
        assert any(
            identifier.endswith("." + contract.payload_field_name)
            for identifier in identifiers
        ), (
            "The field named "
            + contract.payload_field_name
            + " has no rule examining it."
        )


def test_constructing_an_evaluator_with_no_rules_is_refused() -> None:
    """An empty rule set must be impossible to construct."""
    with pytest.raises(ValueError):
        DeconstructedYesNoEvaluator(rules=[])


def test_a_contract_without_any_limit_is_refused() -> None:
    """A field that declares no limit would enforce nothing."""
    with pytest.raises(ValueError):
        FieldContract(
            payload_field_name="unconstrained_field",
            warehouse_column_name="unconstrained_field",
            warehouse_data_type="STRING",
            warehouse_mode="REQUIRED",
            value_is_mandatory=True,
        )


def test_the_accepted_payload_is_accepted(accepted_payload: dict) -> None:
    """The reference payload must satisfy every rule."""
    evaluation = evaluate_student_onboarding_payload(
        accepted_payload, PINNED_EVALUATION_INSTANT
    )
    assert evaluation.outcome_is_accepted is True
    assert evaluation.refusing_rule_identifiers == ()


def test_the_refused_payload_is_refused(refused_payload: dict) -> None:
    """The deliberately malformed payload must be refused."""
    evaluation = evaluate_student_onboarding_payload(
        refused_payload, PINNED_EVALUATION_INSTANT
    )
    assert evaluation.outcome_is_accepted is False


def test_every_reason_for_refusal_is_reported(refused_payload: dict) -> None:
    """Evaluation must not stop at the first rule that answers no."""
    evaluation = evaluate_student_onboarding_payload(
        refused_payload, PINNED_EVALUATION_INSTANT
    )
    assert len(evaluation.refusing_rule_identifiers) > 5


def test_an_unrecognised_field_is_refused(accepted_payload: dict) -> None:
    """A field outside the contract must cause refusal, not be ignored."""
    payload = copy.deepcopy(accepted_payload)
    payload["reviewer_discretionary_note"] = "Looks acceptable to me."
    evaluation = evaluate_student_onboarding_payload(payload, PINNED_EVALUATION_INSTANT)
    assert evaluation.outcome_is_accepted is False
    assert "structure.no_unexpected_field" in evaluation.refusing_rule_identifiers


def test_a_missing_consent_is_refused(accepted_payload: dict) -> None:
    """Processing without consent must never be accepted."""
    payload = copy.deepcopy(accepted_payload)
    payload["data_processing_consent_is_given"] = False
    evaluation = evaluate_student_onboarding_payload(payload, PINNED_EVALUATION_INSTANT)
    assert evaluation.outcome_is_accepted is False
    assert "consent.processing_consent_is_given" in evaluation.refusing_rule_identifiers


def test_a_plan_reference_without_a_plan_is_refused(accepted_payload: dict) -> None:
    """The reference must be present exactly when a plan is held."""
    payload = copy.deepcopy(accepted_payload)
    payload["education_health_care_plan_is_present"] = False
    evaluation = evaluate_student_onboarding_payload(payload, PINNED_EVALUATION_INSTANT)
    assert evaluation.outcome_is_accepted is False
    assert (
        "consistency.plan_reference_matches_plan_presence"
        in evaluation.refusing_rule_identifiers
    )


def test_a_plan_held_without_a_reference_is_refused(accepted_payload: dict) -> None:
    """The converse of the preceding test must also hold."""
    payload = copy.deepcopy(accepted_payload)
    payload["education_health_care_plan_reference"] = None
    evaluation = evaluate_student_onboarding_payload(payload, PINNED_EVALUATION_INSTANT)
    assert evaluation.outcome_is_accepted is False
    assert (
        "consistency.plan_reference_matches_plan_presence"
        in evaluation.refusing_rule_identifiers
    )


def test_a_plan_absent_with_no_reference_is_accepted(accepted_payload: dict) -> None:
    """A student without a plan and without a reference is valid."""
    payload = copy.deepcopy(accepted_payload)
    payload["education_health_care_plan_is_present"] = False
    payload["education_health_care_plan_reference"] = None
    evaluation = evaluate_student_onboarding_payload(payload, PINNED_EVALUATION_INSTANT)
    assert evaluation.outcome_is_accepted is True


def test_a_value_outside_the_permitted_list_is_refused(
    accepted_payload: dict,
) -> None:
    """A category outside the permitted list must be refused."""
    payload = copy.deepcopy(accepted_payload)
    payload["learning_support_category"] = "Something not on the list"
    evaluation = evaluate_student_onboarding_payload(payload, PINNED_EVALUATION_INSTANT)
    assert evaluation.outcome_is_accepted is False
    assert (
        "permitted_values.learning_support_category"
        in evaluation.refusing_rule_identifiers
    )


def test_a_number_above_the_maximum_is_refused(accepted_payload: dict) -> None:
    """Requested hours above the ceiling must be refused."""
    payload = copy.deepcopy(accepted_payload)
    payload["weekly_support_hours_requested"] = 26
    evaluation = evaluate_student_onboarding_payload(payload, PINNED_EVALUATION_INSTANT)
    assert evaluation.outcome_is_accepted is False
    assert (
        "range.weekly_support_hours_requested" in evaluation.refusing_rule_identifiers
    )


def test_a_number_at_the_maximum_is_accepted(accepted_payload: dict) -> None:
    """The boundary itself must be inside the permitted range."""
    payload = copy.deepcopy(accepted_payload)
    payload["weekly_support_hours_requested"] = 25
    evaluation = evaluate_student_onboarding_payload(payload, PINNED_EVALUATION_INSTANT)
    assert evaluation.outcome_is_accepted is True


def test_a_boolean_is_not_accepted_where_a_number_is_required(
    accepted_payload: dict,
) -> None:
    """A boolean must not pass as the number one."""
    payload = copy.deepcopy(accepted_payload)
    payload["weekly_support_hours_requested"] = True
    evaluation = evaluate_student_onboarding_payload(payload, PINNED_EVALUATION_INSTANT)
    assert evaluation.outcome_is_accepted is False
    assert "type.weekly_support_hours_requested" in evaluation.refusing_rule_identifiers


def test_a_timestamp_without_a_time_zone_is_refused(accepted_payload: dict) -> None:
    """A timestamp that requires a reader to assume a zone must be refused."""
    payload = copy.deepcopy(accepted_payload)
    payload["submission_received_timestamp"] = "2026-09-08T09:14:32"
    evaluation = evaluate_student_onboarding_payload(payload, PINNED_EVALUATION_INSTANT)
    assert evaluation.outcome_is_accepted is False
    assert "type.submission_received_timestamp" in evaluation.refusing_rule_identifiers


def test_a_submission_from_the_future_is_refused(accepted_payload: dict) -> None:
    """A submission timestamp after the evaluation instant must be refused."""
    payload = copy.deepcopy(accepted_payload)
    payload["submission_reference"] = "HCSO-20260920-4F2A9C1D"
    payload["submission_received_timestamp"] = "2026-09-20T09:14:32+00:00"
    evaluation = evaluate_student_onboarding_payload(payload, PINNED_EVALUATION_INSTANT)
    assert evaluation.outcome_is_accepted is False
    assert (
        "freshness.submission_is_not_in_the_future"
        in evaluation.refusing_rule_identifiers
    )


def test_a_stale_submission_is_refused(accepted_payload: dict) -> None:
    """A submission older than the freshness window must be refused."""
    payload = copy.deepcopy(accepted_payload)
    payload["submission_reference"] = "HCSO-20260701-4F2A9C1D"
    payload["submission_received_timestamp"] = "2026-07-01T09:14:32+00:00"
    evaluation = evaluate_student_onboarding_payload(payload, PINNED_EVALUATION_INSTANT)
    assert evaluation.outcome_is_accepted is False
    assert (
        "freshness.submission_is_recent_enough" in evaluation.refusing_rule_identifiers
    )


def test_a_reference_date_that_disagrees_is_refused(accepted_payload: dict) -> None:
    """The date inside the reference must match the timestamp."""
    payload = copy.deepcopy(accepted_payload)
    payload["submission_reference"] = "HCSO-20260903-4F2A9C1D"
    evaluation = evaluate_student_onboarding_payload(payload, PINNED_EVALUATION_INSTANT)
    assert evaluation.outcome_is_accepted is False
    assert (
        "consistency.reference_date_agrees_with_timestamp"
        in evaluation.refusing_rule_identifiers
    )


def test_a_year_group_that_disagrees_with_age_is_refused(
    accepted_payload: dict,
) -> None:
    """A year group more than one away from the implied group is refused."""
    payload = copy.deepcopy(accepted_payload)
    payload["student_year_group"] = 2
    evaluation = evaluate_student_onboarding_payload(payload, PINNED_EVALUATION_INSTANT)
    assert evaluation.outcome_is_accepted is False
    assert (
        "consistency.year_group_agrees_with_age" in evaluation.refusing_rule_identifiers
    )


def test_a_postal_code_in_lower_case_is_refused(accepted_payload: dict) -> None:
    """The stored form is upper case with one space, and only that form."""
    payload = copy.deepcopy(accepted_payload)
    payload["home_postal_code"] = "m14 5rt"
    evaluation = evaluate_student_onboarding_payload(payload, PINNED_EVALUATION_INSTANT)
    assert evaluation.outcome_is_accepted is False
    assert "pattern.home_postal_code" in evaluation.refusing_rule_identifiers


def test_a_telephone_number_without_a_country_is_refused(
    accepted_payload: dict,
) -> None:
    """A national format number requires a reader to infer a country."""
    payload = copy.deepcopy(accepted_payload)
    payload["parent_or_guardian_telephone_number"] = "07700900412"
    evaluation = evaluate_student_onboarding_payload(payload, PINNED_EVALUATION_INSTANT)
    assert evaluation.outcome_is_accepted is False
    assert (
        "pattern.parent_or_guardian_telephone_number"
        in evaluation.refusing_rule_identifiers
    )


def test_a_payload_that_is_not_an_object_is_refused() -> None:
    """A list or a scalar must be refused rather than raising."""
    evaluation = evaluate_student_onboarding_payload(
        ["not", "an", "object"], PINNED_EVALUATION_INSTANT
    )
    assert evaluation.outcome_is_accepted is False


def test_an_empty_payload_is_refused() -> None:
    """An empty object must fail every presence rule rather than pass."""
    evaluation = evaluate_student_onboarding_payload({}, PINNED_EVALUATION_INSTANT)
    assert evaluation.outcome_is_accepted is False


def test_every_answer_is_a_genuine_boolean(accepted_payload: dict) -> None:
    """No rule may return a value that merely evaluates as true or false."""
    evaluation = evaluate_student_onboarding_payload(
        accepted_payload, PINNED_EVALUATION_INSTANT
    )
    for answer in evaluation.rule_answers:
        assert isinstance(answer.rule_answer_is_yes, bool)


def test_the_warehouse_record_shape_is_complete(accepted_payload: dict) -> None:
    """Every answer must serialise into the repeated warehouse record."""
    evaluation = evaluate_student_onboarding_payload(
        accepted_payload, PINNED_EVALUATION_INSTANT
    )
    records = evaluation.as_warehouse_records()
    assert len(records) == len(evaluation.rule_answers)
    for record in records:
        assert set(record.keys()) == {
            "rule_identifier",
            "rule_question",
            "rule_answer_is_yes",
        }


def test_every_rule_question_is_answerable_with_yes_or_no() -> None:
    """A question that is not a question invites a judgement."""
    evaluator = DeconstructedYesNoEvaluator()
    evaluation = evaluator.evaluate({}, PINNED_EVALUATION_INSTANT)
    for answer in evaluation.rule_answers:
        assert answer.rule_question.endswith("?"), (
            "The rule identified as "
            + answer.rule_identifier
            + " does not state a question."
        )


def test_every_rule_question_fits_the_warehouse_column() -> None:
    """A question longer than the column would be truncated on load.

    The two limits are read from the field contract rather than written here,
    for the same reason that every other limit is read from it.
    """
    evaluator = DeconstructedYesNoEvaluator()
    evaluation = evaluator.evaluate({}, PINNED_EVALUATION_INSTANT)
    for answer in evaluation.rule_answers:
        assert len(answer.rule_question) <= MAXIMUM_RULE_QUESTION_LENGTH, (
            "The question stated by the rule identified as "
            + answer.rule_identifier
            + " is longer than the warehouse column that receives it."
        )
        assert len(answer.rule_identifier) <= MAXIMUM_RULE_IDENTIFIER_LENGTH
