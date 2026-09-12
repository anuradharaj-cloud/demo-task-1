"""Habot Connect FZCO - Hiring Project.

Position: Junior Cloud and Development Operations Engineer.
Candidate Full Name: Anuradha.
Candidate Electronic Mail Address: anuradha@tecofize.com.

File purpose: the rule set of the deconstructed yes or no validation library.

Poka-Yoke rationale for this file
---------------------------------
Every rule in this file answers a question whose only possible answers are yes
and no. There is no rule that returns a score, a severity, a warning or a
recommendation, because each of those would require a person to decide what to
do about it, and a decision left to a person is a decision that will eventually
be made differently by two people.

The per field rules are generated from the field contract rather than written by
hand. Writing them by hand would reintroduce the possibility that a field exists
in the contract with no rule checking it. Generation makes that impossible: a
field added to the contract is a field with rules.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Any, Callable, Dict, List, Optional, Tuple

from .field_contract import (
    FIELD_CONTRACTS,
    MAXIMUM_STUDENT_AGE_IN_COMPLETE_YEARS,
    MAXIMUM_SUBMISSION_AGE_IN_DAYS,
    MINIMUM_STUDENT_AGE_IN_COMPLETE_YEARS,
    FieldContract,
)

# The year group that a student of the minimum permitted age is expected to be
# in. A student of age four is expected to be in year group one, so the offset
# between age in complete years and year group is three.
AGE_TO_YEAR_GROUP_OFFSET = 3

# The number of year groups by which a stated year group may differ from the
# year group implied by the date of birth. One year of tolerance accommodates a
# student who was held back or moved forward. Two years does not occur without a
# separate arrangement, which is handled outside this platform.
PERMITTED_YEAR_GROUP_DEVIATION = 1


@dataclass(frozen=True)
class RuleAnswer:
    """The answer that one rule returned for one submission."""

    rule_identifier: str
    rule_question: str
    rule_answer_is_yes: bool

    def as_warehouse_record(self) -> Dict[str, Any]:
        """Return the answer in the shape of the warehouse repeated record."""
        return {
            "rule_identifier": self.rule_identifier,
            "rule_question": self.rule_question,
            "rule_answer_is_yes": self.rule_answer_is_yes,
        }


@dataclass(frozen=True)
class DeconstructedYesNoRule:
    """One rule of the library.

    The predicate must return a genuine boolean. A predicate that returned a
    value which merely evaluates as true or false would let an empty string or a
    zero pass as a negative answer by accident, so the evaluator checks the
    returned type and refuses anything that is not a boolean.
    """

    rule_identifier: str
    rule_question: str
    predicate: Callable[[Dict[str, Any], datetime], bool]

    def answer(
        self, payload: Dict[str, Any], evaluation_instant: datetime
    ) -> RuleAnswer:
        """Evaluate the rule and return its answer."""
        try:
            answer_is_yes = self.predicate(payload, evaluation_instant)
        except Exception:
            # A rule that raises is a rule that could not establish a yes. The
            # library treats that as a no rather than allowing the exception to
            # escape, because an exception escaping the validator would either
            # halt ingestion entirely or, worse, be caught somewhere upstream
            # and treated as a pass.
            answer_is_yes = False

        if not isinstance(answer_is_yes, bool):
            answer_is_yes = False

        return RuleAnswer(
            rule_identifier=self.rule_identifier,
            rule_question=self.rule_question,
            rule_answer_is_yes=answer_is_yes,
        )


def _value_is_present(payload: Dict[str, Any], field_name: str) -> bool:
    """Return whether a field carries a value that is neither absent nor null."""
    if field_name not in payload:
        return False
    value = payload[field_name]
    if value is None:
        return False
    if isinstance(value, str) and value.strip() == "":
        return False
    return True


def _parse_calendar_date(value: Any) -> Optional[date]:
    """Return the calendar date that a value states, or nothing."""
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _parse_instant(value: Any) -> Optional[datetime]:
    """Return the instant that a value states, or nothing.

    A value without an explicit time zone offset is refused rather than assumed
    to be coordinated universal time.
    """
    if not isinstance(value, str):
        return None
    normalised_value = value.replace("Z", "+00:00")
    try:
        parsed_instant = datetime.fromisoformat(normalised_value)
    except ValueError:
        return None
    if parsed_instant.tzinfo is None:
        return None
    return parsed_instant.astimezone(timezone.utc)


def _complete_years_between(earlier: date, later: date) -> int:
    """Return the number of complete years between two calendar dates."""
    completed_years = later.year - earlier.year
    if (later.month, later.day) < (earlier.month, earlier.day):
        completed_years -= 1
    return completed_years


def _build_presence_rule(contract: FieldContract) -> DeconstructedYesNoRule:
    field_name = contract.payload_field_name

    def presence_predicate(payload: Dict[str, Any], _instant: datetime) -> bool:
        if contract.value_is_mandatory:
            return _value_is_present(payload, field_name)
        # An optional field satisfies its presence rule when it is absent, when
        # it is null, or when it carries a value. All three are permitted, so
        # the only way to fail is for the key to hold an empty string, which is
        # neither a stated absence nor a stated value.
        if field_name not in payload:
            return True
        value = payload[field_name]
        if value is None:
            return True
        return not (isinstance(value, str) and value.strip() == "")

    question = (
        "Is the field named " + field_name + " present with a stated value?"
        if contract.value_is_mandatory
        else "Is the field named "
        + field_name
        + " either stated clearly or absent, rather than empty?"
    )

    return DeconstructedYesNoRule(
        rule_identifier="presence." + field_name,
        rule_question=question,
        predicate=presence_predicate,
    )


def _build_type_rule(contract: FieldContract) -> DeconstructedYesNoRule:
    field_name = contract.payload_field_name
    expected_type = contract.warehouse_data_type

    def type_predicate(payload: Dict[str, Any], _instant: datetime) -> bool:
        if not _value_is_present(payload, field_name):
            return not contract.value_is_mandatory
        value = payload[field_name]
        if expected_type == "BOOLEAN":
            return isinstance(value, bool)
        if expected_type == "INTEGER":
            # A boolean is an integer in Python. Accepting one here would let a
            # true value pass as the number one, so booleans are refused
            # explicitly.
            return isinstance(value, int) and not isinstance(value, bool)
        if expected_type == "DATE":
            return _parse_calendar_date(value) is not None
        if expected_type == "TIMESTAMP":
            return _parse_instant(value) is not None
        return isinstance(value, str)

    return DeconstructedYesNoRule(
        rule_identifier="type." + field_name,
        rule_question=(
            "Is the value of the field named "
            + field_name
            + " of the declared type, which is "
            + expected_type
            + "?"
        ),
        predicate=type_predicate,
    )


def _build_length_rule(contract: FieldContract) -> DeconstructedYesNoRule:
    field_name = contract.payload_field_name
    maximum_length = contract.maximum_character_length

    def length_predicate(payload: Dict[str, Any], _instant: datetime) -> bool:
        if not _value_is_present(payload, field_name):
            return not contract.value_is_mandatory
        value = payload[field_name]
        if not isinstance(value, str):
            return False
        return len(value) <= int(maximum_length)

    return DeconstructedYesNoRule(
        rule_identifier="length." + field_name,
        rule_question=(
            "Is the value of the field named "
            + field_name
            + " no longer than "
            + str(maximum_length)
            + " characters?"
        ),
        predicate=length_predicate,
    )


def _build_pattern_rule(contract: FieldContract) -> DeconstructedYesNoRule:
    field_name = contract.payload_field_name
    compiled_pattern = re.compile(str(contract.regular_expression_pattern))

    def pattern_predicate(payload: Dict[str, Any], _instant: datetime) -> bool:
        if not _value_is_present(payload, field_name):
            return not contract.value_is_mandatory
        value = payload[field_name]
        if not isinstance(value, str):
            return False
        return compiled_pattern.fullmatch(value) is not None

    return DeconstructedYesNoRule(
        rule_identifier="pattern." + field_name,
        rule_question=(
            "Does the value of the field named "
            + field_name
            + " match its required form, which is "
            + str(contract.regular_expression_explanation)
            + "?"
        ),
        predicate=pattern_predicate,
    )


def _build_permitted_values_rule(contract: FieldContract) -> DeconstructedYesNoRule:
    field_name = contract.payload_field_name
    permitted_values = tuple(contract.permitted_values or ())

    def permitted_values_predicate(payload: Dict[str, Any], _instant: datetime) -> bool:
        if not _value_is_present(payload, field_name):
            return not contract.value_is_mandatory
        return payload[field_name] in permitted_values

    return DeconstructedYesNoRule(
        rule_identifier="permitted_values." + field_name,
        rule_question=(
            "Is the value of the field named "
            + field_name
            + " one of the "
            + str(len(permitted_values))
            + " permitted values stated in the field contract?"
        ),
        predicate=permitted_values_predicate,
    )


def _build_range_rule(contract: FieldContract) -> DeconstructedYesNoRule:
    field_name = contract.payload_field_name
    minimum_number = contract.minimum_permitted_number
    maximum_number = contract.maximum_permitted_number

    def range_predicate(payload: Dict[str, Any], _instant: datetime) -> bool:
        if not _value_is_present(payload, field_name):
            return not contract.value_is_mandatory
        value = payload[field_name]
        if isinstance(value, bool) or not isinstance(value, int):
            return False
        if minimum_number is not None and value < minimum_number:
            return False
        if maximum_number is not None and value > maximum_number:
            return False
        return True

    return DeconstructedYesNoRule(
        rule_identifier="range." + field_name,
        rule_question=(
            "Is the value of the field named "
            + field_name
            + " between "
            + str(minimum_number)
            + " and "
            + str(maximum_number)
            + " inclusive?"
        ),
        predicate=range_predicate,
    )


def build_field_rules() -> List[DeconstructedYesNoRule]:
    """Generate every per field rule from the field contract."""
    generated_rules: List[DeconstructedYesNoRule] = []

    for contract in FIELD_CONTRACTS:
        generated_rules.append(_build_presence_rule(contract))
        generated_rules.append(_build_type_rule(contract))

        if contract.maximum_character_length is not None:
            generated_rules.append(_build_length_rule(contract))
        if contract.regular_expression_pattern is not None:
            generated_rules.append(_build_pattern_rule(contract))
        if contract.permitted_values is not None:
            generated_rules.append(_build_permitted_values_rule(contract))
        if (
            contract.minimum_permitted_number is not None
            or contract.maximum_permitted_number is not None
        ):
            generated_rules.append(_build_range_rule(contract))

    return generated_rules


# -----------------------------------------------------------------------------
# Cross field rules. These cannot be generated from the contract because they
# concern the relationship between two or more fields. Each one replaces a
# judgement that a reviewer would otherwise have to make.
# -----------------------------------------------------------------------------


def _no_unexpected_field_is_present(
    payload: Dict[str, Any], _instant: datetime
) -> bool:
    permitted_field_names = {
        contract.payload_field_name for contract in FIELD_CONTRACTS
    }
    return set(payload.keys()).issubset(permitted_field_names)


def _consent_is_given(payload: Dict[str, Any], _instant: datetime) -> bool:
    return payload.get("data_processing_consent_is_given") is True


def _plan_reference_matches_plan_presence(
    payload: Dict[str, Any], _instant: datetime
) -> bool:
    plan_is_present = payload.get("education_health_care_plan_is_present")
    reference_is_present = _value_is_present(
        payload, "education_health_care_plan_reference"
    )
    if plan_is_present is True:
        return reference_is_present
    if plan_is_present is False:
        return not reference_is_present
    return False


def _student_age_is_within_the_permitted_range(
    payload: Dict[str, Any], _instant: datetime
) -> bool:
    date_of_birth = _parse_calendar_date(payload.get("student_date_of_birth"))
    submission_instant = _parse_instant(payload.get("submission_received_timestamp"))
    if date_of_birth is None or submission_instant is None:
        return False
    age_in_complete_years = _complete_years_between(
        date_of_birth, submission_instant.date()
    )
    return (
        MINIMUM_STUDENT_AGE_IN_COMPLETE_YEARS
        <= age_in_complete_years
        <= MAXIMUM_STUDENT_AGE_IN_COMPLETE_YEARS
    )


def _year_group_agrees_with_age(payload: Dict[str, Any], _instant: datetime) -> bool:
    date_of_birth = _parse_calendar_date(payload.get("student_date_of_birth"))
    submission_instant = _parse_instant(payload.get("submission_received_timestamp"))
    stated_year_group = payload.get("student_year_group")
    if date_of_birth is None or submission_instant is None:
        return False
    if isinstance(stated_year_group, bool) or not isinstance(stated_year_group, int):
        return False
    age_in_complete_years = _complete_years_between(
        date_of_birth, submission_instant.date()
    )
    implied_year_group = age_in_complete_years - AGE_TO_YEAR_GROUP_OFFSET
    return abs(stated_year_group - implied_year_group) <= (
        PERMITTED_YEAR_GROUP_DEVIATION
    )


def _submission_reference_date_agrees_with_timestamp(
    payload: Dict[str, Any], _instant: datetime
) -> bool:
    submission_reference = payload.get("submission_reference")
    submission_instant = _parse_instant(payload.get("submission_received_timestamp"))
    if not isinstance(submission_reference, str) or submission_instant is None:
        return False
    reference_parts = submission_reference.split("-")
    if len(reference_parts) != 3:
        return False
    return reference_parts[1] == submission_instant.strftime("%Y%m%d")


def _submission_instant_is_not_in_the_future(
    payload: Dict[str, Any], evaluation_instant: datetime
) -> bool:
    submission_instant = _parse_instant(payload.get("submission_received_timestamp"))
    if submission_instant is None:
        return False
    return submission_instant <= evaluation_instant


def _submission_instant_is_recent_enough(
    payload: Dict[str, Any], evaluation_instant: datetime
) -> bool:
    submission_instant = _parse_instant(payload.get("submission_received_timestamp"))
    if submission_instant is None:
        return False
    oldest_permitted_instant = evaluation_instant - timedelta(
        days=MAXIMUM_SUBMISSION_AGE_IN_DAYS
    )
    return submission_instant >= oldest_permitted_instant


CROSS_FIELD_RULES: Tuple[DeconstructedYesNoRule, ...] = (
    DeconstructedYesNoRule(
        rule_identifier="structure.no_unexpected_field",
        rule_question=(
            "Is every field in the payload one of the fields declared in the "
            "field contract, with no additional field present?"
        ),
        predicate=_no_unexpected_field_is_present,
    ),
    DeconstructedYesNoRule(
        rule_identifier="consent.processing_consent_is_given",
        rule_question=(
            "Has the parent or guardian given explicit consent to the "
            "processing of the data of the student?"
        ),
        predicate=_consent_is_given,
    ),
    DeconstructedYesNoRule(
        rule_identifier="consistency.plan_reference_matches_plan_presence",
        rule_question=(
            "Is the education, health and care plan reference present exactly "
            "when the payload states that a plan is held?"
        ),
        predicate=_plan_reference_matches_plan_presence,
    ),
    DeconstructedYesNoRule(
        rule_identifier="consistency.student_age_is_in_range",
        rule_question=(
            "Was the student between "
            + str(MINIMUM_STUDENT_AGE_IN_COMPLETE_YEARS)
            + " and "
            + str(MAXIMUM_STUDENT_AGE_IN_COMPLETE_YEARS)
            + " complete years of age on the date the submission was received?"
        ),
        predicate=_student_age_is_within_the_permitted_range,
    ),
    DeconstructedYesNoRule(
        rule_identifier="consistency.year_group_agrees_with_age",
        rule_question=(
            "Is the stated year group within "
            + str(PERMITTED_YEAR_GROUP_DEVIATION)
            + " of the year group implied by the date of birth?"
        ),
        predicate=_year_group_agrees_with_age,
    ),
    DeconstructedYesNoRule(
        rule_identifier="consistency.reference_date_agrees_with_timestamp",
        rule_question=(
            "Does the date written inside the submission reference agree with "
            "the date of the submission timestamp?"
        ),
        predicate=_submission_reference_date_agrees_with_timestamp,
    ),
    DeconstructedYesNoRule(
        rule_identifier="freshness.submission_is_not_in_the_future",
        rule_question=(
            "Is the submission timestamp at or before the instant at which the "
            "payload is being evaluated?"
        ),
        predicate=_submission_instant_is_not_in_the_future,
    ),
    DeconstructedYesNoRule(
        rule_identifier="freshness.submission_is_recent_enough",
        rule_question=(
            "Is the submission timestamp within the last "
            + str(MAXIMUM_SUBMISSION_AGE_IN_DAYS)
            + " days?"
        ),
        predicate=_submission_instant_is_recent_enough,
    ),
)


def build_complete_rule_set() -> List[DeconstructedYesNoRule]:
    """Return every rule, generated and cross field, in a stable order."""
    complete_rule_set = build_field_rules() + list(CROSS_FIELD_RULES)

    # Two rules sharing an identifier would make an audit ambiguous, so the
    # library refuses to assemble such a set rather than producing one.
    seen_identifiers = set()
    for rule in complete_rule_set:
        if rule.rule_identifier in seen_identifiers:
            raise ValueError(
                "The rule identifier "
                + rule.rule_identifier
                + " is declared more than once. Every rule identifier must be "
                + "unique so that an audit can attribute an answer to exactly "
                + "one rule."
            )
        seen_identifiers.add(rule.rule_identifier)

    return complete_rule_set
