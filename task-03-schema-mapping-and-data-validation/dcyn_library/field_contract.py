"""Habot Connect FZCO - Hiring Project.

Position: Junior Cloud and Development Operations Engineer.
Candidate Full Name: Anuradha.
Candidate Electronic Mail Address: anuradha@tecofize.com.

File purpose: the single authoritative statement of every field in the student
onboarding payload, its limits, and the warehouse column it maps to.

Poka-Yoke rationale for this file
---------------------------------
The second half of the incident that this project responds to was a schema
mismatch. A schema mismatch is only possible when the same fact is written down
in more than one place and a person is expected to keep the copies in step.

This file removes that possibility. It is the only place in the repository where
a field limit is stated. Three consumers read it and none of them restates it:

    1. The Django REST Framework serializer builds its fields from this file, so
       a limit cannot exist in the serializer that is absent here.
    2. The deconstructed yes or no validation library builds its rules from this
       file, so a rule cannot check a limit that is not declared here.
    3. The schema consistency gate in the build pipeline compares this file
       against the BigQuery table schema on every commit, so a column cannot
       drift away from the field that feeds it.

Changing a limit is therefore a single edit in a single file, and the pipeline
proves that the change reached every consumer.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

# The number of complete years of age that a student must have reached, and must
# not have exceeded, at the moment a submission is received.
MINIMUM_STUDENT_AGE_IN_COMPLETE_YEARS = 4
MAXIMUM_STUDENT_AGE_IN_COMPLETE_YEARS = 19

# The number of days before the current instant within which a submission
# timestamp must fall. A timestamp outside this window indicates either a clock
# problem or a replayed payload, and in both cases the submission is refused.
MAXIMUM_SUBMISSION_AGE_IN_DAYS = 7

# The limits of the audit record that every rule answer is written into. These
# are declared here, beside the field limits, because they are the same class of
# fact: a length that the application and the warehouse must agree on. The
# schema consistency gate compares both of them against the repeated record
# declared in the warehouse table, so a rule question that would be truncated on
# load fails the build rather than losing its ending in the warehouse.
MAXIMUM_RULE_IDENTIFIER_LENGTH = 48
MAXIMUM_RULE_QUESTION_LENGTH = 400

PERMITTED_LEARNING_SUPPORT_CATEGORIES: Tuple[str, ...] = (
    "Specific learning difficulty",
    "Speech, language and communication need",
    "Autism spectrum condition",
    "Social, emotional and mental health need",
    "Moderate learning difficulty",
    "Physical or sensory impairment",
)

PERMITTED_SESSION_LANGUAGES: Tuple[str, ...] = (
    "English",
    "Welsh",
    "Polish",
    "Urdu",
    "Bengali",
    "Somali",
    "Romanian",
    "Arabic",
)

PERMITTED_LOCAL_AUTHORITY_NAMES: Tuple[str, ...] = (
    "Birmingham City Council",
    "Bradford Metropolitan District Council",
    "Cardiff Council",
    "Leeds City Council",
    "Manchester City Council",
    "Newham London Borough Council",
    "Sheffield City Council",
    "Tower Hamlets London Borough Council",
)


@dataclass(frozen=True)
class FieldContract:
    """One field of the student onboarding payload, stated exhaustively.

    Every attribute below is a limit that is mechanically enforceable. There is
    deliberately no attribute that expresses guidance, preference or anything
    else that would require a person to form a judgement.
    """

    payload_field_name: str
    warehouse_column_name: str
    warehouse_data_type: str
    warehouse_mode: str
    value_is_mandatory: bool
    maximum_character_length: Optional[int] = None
    minimum_permitted_number: Optional[int] = None
    maximum_permitted_number: Optional[int] = None
    permitted_values: Optional[Tuple[str, ...]] = None
    regular_expression_pattern: Optional[str] = None
    regular_expression_explanation: Optional[str] = None
    is_direct_identifier: bool = False
    field_description: str = ""

    def __post_init__(self) -> None:
        """Refuse a contract that cannot be enforced.

        A contract that declares no limit at all would silently accept any
        value. Rather than trusting the author of a future field to remember to
        add a limit, the contract refuses to be constructed without one.
        """
        declared_limits = (
            self.maximum_character_length,
            self.minimum_permitted_number,
            self.maximum_permitted_number,
            self.permitted_values,
            self.regular_expression_pattern,
        )
        if self.warehouse_data_type != "BOOLEAN" and not any(
            limit is not None for limit in declared_limits
        ):
            raise ValueError(
                "The field "
                + self.payload_field_name
                + " declares no enforceable limit. Every non boolean field must "
                + "declare at least one limit, because a field without a limit "
                + "accepts any value and therefore enforces nothing."
            )


FIELD_CONTRACTS: Tuple[FieldContract, ...] = (
    FieldContract(
        payload_field_name="submission_reference",
        warehouse_column_name="submission_reference",
        warehouse_data_type="STRING",
        warehouse_mode="REQUIRED",
        value_is_mandatory=True,
        maximum_character_length=22,
        regular_expression_pattern=r"^HCSO-[0-9]{8}-[0-9A-F]{8}$",
        regular_expression_explanation=(
            "The four letters HCSO, a hyphen, the submission date written as "
            "four digits of year followed by two digits of month followed by "
            "two digits of day, a hyphen, and eight upper case hexadecimal "
            "characters."
        ),
        field_description="Unique reference of the onboarding submission.",
    ),
    FieldContract(
        payload_field_name="submission_received_timestamp",
        warehouse_column_name="submission_received_timestamp",
        warehouse_data_type="TIMESTAMP",
        warehouse_mode="REQUIRED",
        value_is_mandatory=True,
        regular_expression_pattern=(
            r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
            r"(\.[0-9]{1,6})?(Z|[+-][0-9]{2}:[0-9]{2})$"
        ),
        regular_expression_explanation=(
            "A date and time written in the international standard combined "
            "format, carrying an explicit time zone offset. A timestamp without "
            "an offset is refused, because interpreting it requires a person to "
            "assume which zone was meant."
        ),
        field_description=(
            "Instant at which the application accepted the submission. This is "
            "the partitioning column of the warehouse table."
        ),
    ),
    FieldContract(
        payload_field_name="student_given_name",
        warehouse_column_name="student_given_name",
        warehouse_data_type="STRING",
        warehouse_mode="REQUIRED",
        value_is_mandatory=True,
        maximum_character_length=60,
        regular_expression_pattern=r"^[\w][\w' \-.]{0,59}$",
        regular_expression_explanation=(
            "One or more word characters, apostrophes, spaces, hyphens or full "
            "stops, beginning with a word character. Word characters include "
            "letters outside the English alphabet."
        ),
        is_direct_identifier=True,
        field_description="Given name of the student.",
    ),
    FieldContract(
        payload_field_name="student_family_name",
        warehouse_column_name="student_family_name",
        warehouse_data_type="STRING",
        warehouse_mode="REQUIRED",
        value_is_mandatory=True,
        maximum_character_length=60,
        regular_expression_pattern=r"^[\w][\w' \-.]{0,59}$",
        regular_expression_explanation=(
            "One or more word characters, apostrophes, spaces, hyphens or full "
            "stops, beginning with a word character."
        ),
        is_direct_identifier=True,
        field_description="Family name of the student.",
    ),
    FieldContract(
        payload_field_name="student_date_of_birth",
        warehouse_column_name="student_date_of_birth",
        warehouse_data_type="DATE",
        warehouse_mode="REQUIRED",
        value_is_mandatory=True,
        regular_expression_pattern=r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$",
        regular_expression_explanation=(
            "A calendar date written as four digits of year, a hyphen, two "
            "digits of month, a hyphen and two digits of day."
        ),
        is_direct_identifier=True,
        field_description="Date of birth of the student.",
    ),
    FieldContract(
        payload_field_name="student_year_group",
        warehouse_column_name="student_year_group",
        warehouse_data_type="INTEGER",
        warehouse_mode="REQUIRED",
        value_is_mandatory=True,
        minimum_permitted_number=1,
        maximum_permitted_number=13,
        field_description="National curriculum year group of the student.",
    ),
    FieldContract(
        payload_field_name="parent_or_guardian_full_name",
        warehouse_column_name="parent_or_guardian_full_name",
        warehouse_data_type="STRING",
        warehouse_mode="REQUIRED",
        value_is_mandatory=True,
        maximum_character_length=120,
        regular_expression_pattern=r"^[\w][\w' \-.]{0,119}$",
        regular_expression_explanation=(
            "One or more word characters, apostrophes, spaces, hyphens or full "
            "stops, beginning with a word character."
        ),
        is_direct_identifier=True,
        field_description="Full name of the parent or guardian.",
    ),
    FieldContract(
        payload_field_name="parent_or_guardian_email_address",
        warehouse_column_name="parent_or_guardian_email_address",
        warehouse_data_type="STRING",
        warehouse_mode="REQUIRED",
        value_is_mandatory=True,
        maximum_character_length=254,
        regular_expression_pattern=r"^[^@\s]{1,64}@[^@\s.]+(\.[^@\s.]+)+$",
        regular_expression_explanation=(
            "A local part of between one and sixty four characters containing "
            "no space and no commercial at sign, a commercial at sign, and a "
            "domain of at least two labels separated by full stops."
        ),
        is_direct_identifier=True,
        field_description="Electronic mail address of the parent or guardian.",
    ),
    FieldContract(
        payload_field_name="parent_or_guardian_telephone_number",
        warehouse_column_name="parent_or_guardian_telephone_number",
        warehouse_data_type="STRING",
        warehouse_mode="REQUIRED",
        value_is_mandatory=True,
        maximum_character_length=16,
        regular_expression_pattern=r"^\+[1-9][0-9]{7,14}$",
        regular_expression_explanation=(
            "A plus sign, a leading digit from one to nine, and between seven "
            "and fourteen further digits. The international format is required "
            "so that no reader has to infer a country."
        ),
        is_direct_identifier=True,
        field_description="Telephone number of the parent or guardian.",
    ),
    FieldContract(
        payload_field_name="home_postal_code",
        warehouse_column_name="home_postal_code",
        warehouse_data_type="STRING",
        warehouse_mode="REQUIRED",
        value_is_mandatory=True,
        maximum_character_length=8,
        regular_expression_pattern=r"^[A-Z]{1,2}[0-9][0-9A-Z]? [0-9][A-Z]{2}$",
        regular_expression_explanation=(
            "A United Kingdom postal code in upper case with exactly one space "
            "before the final three characters."
        ),
        is_direct_identifier=True,
        field_description="Postal code of the home address of the student.",
    ),
    FieldContract(
        payload_field_name="assigned_local_authority_name",
        warehouse_column_name="assigned_local_authority_name",
        warehouse_data_type="STRING",
        warehouse_mode="REQUIRED",
        value_is_mandatory=True,
        maximum_character_length=80,
        permitted_values=PERMITTED_LOCAL_AUTHORITY_NAMES,
        field_description=(
            "Local authority responsible for the student. This is the column "
            "that the warehouse row access policy filters on."
        ),
    ),
    FieldContract(
        payload_field_name="school_unique_reference_number",
        warehouse_column_name="school_unique_reference_number",
        warehouse_data_type="STRING",
        warehouse_mode="REQUIRED",
        value_is_mandatory=True,
        maximum_character_length=6,
        regular_expression_pattern=r"^[0-9]{6}$",
        regular_expression_explanation="Exactly six digits.",
        field_description=(
            "Unique reference number of the school that the student attends. "
            "Held as text rather than as a number because a leading zero is "
            "significant and would be lost by numeric storage."
        ),
    ),
    FieldContract(
        payload_field_name="learning_support_category",
        warehouse_column_name="learning_support_category",
        warehouse_data_type="STRING",
        warehouse_mode="REQUIRED",
        value_is_mandatory=True,
        maximum_character_length=48,
        permitted_values=PERMITTED_LEARNING_SUPPORT_CATEGORIES,
        field_description="Category of learning support requested.",
    ),
    FieldContract(
        payload_field_name="weekly_support_hours_requested",
        warehouse_column_name="weekly_support_hours_requested",
        warehouse_data_type="INTEGER",
        warehouse_mode="REQUIRED",
        value_is_mandatory=True,
        minimum_permitted_number=1,
        maximum_permitted_number=25,
        field_description="Support hours requested each week.",
    ),
    FieldContract(
        payload_field_name="preferred_session_language",
        warehouse_column_name="preferred_session_language",
        warehouse_data_type="STRING",
        warehouse_mode="REQUIRED",
        value_is_mandatory=True,
        maximum_character_length=24,
        permitted_values=PERMITTED_SESSION_LANGUAGES,
        field_description="Language in which support sessions are delivered.",
    ),
    FieldContract(
        payload_field_name="education_health_care_plan_is_present",
        warehouse_column_name="education_health_care_plan_is_present",
        warehouse_data_type="BOOLEAN",
        warehouse_mode="REQUIRED",
        value_is_mandatory=True,
        field_description=(
            "True when the student holds an education, health and care plan."
        ),
    ),
    FieldContract(
        payload_field_name="education_health_care_plan_reference",
        warehouse_column_name="education_health_care_plan_reference",
        warehouse_data_type="STRING",
        warehouse_mode="NULLABLE",
        value_is_mandatory=False,
        maximum_character_length=14,
        regular_expression_pattern=r"^EHCP-[0-9]{4}-[0-9]{4}$",
        regular_expression_explanation=(
            "The four letters EHCP, a hyphen, four digits of issuing year, a "
            "hyphen and a four digit sequence number."
        ),
        field_description=(
            "Reference of the education, health and care plan. Present exactly "
            "when the preceding field is true, which is checked by a dedicated "
            "rule rather than left to the judgement of a reviewer."
        ),
    ),
    FieldContract(
        payload_field_name="data_processing_consent_is_given",
        warehouse_column_name="data_processing_consent_is_given",
        warehouse_data_type="BOOLEAN",
        warehouse_mode="REQUIRED",
        value_is_mandatory=True,
        field_description=(
            "True when the parent or guardian has given explicit consent to "
            "processing. A submission where this is false is never written."
        ),
    ),
    FieldContract(
        payload_field_name="record_is_withheld_from_analytics",
        warehouse_column_name="record_is_withheld_from_analytics",
        warehouse_data_type="BOOLEAN",
        warehouse_mode="REQUIRED",
        value_is_mandatory=True,
        field_description=(
            "True when the parent or guardian has objected to analytical "
            "processing. Both the row access policy and the reporting view "
            "exclude rows where this is true."
        ),
    ),
)

# Columns that the transformation stage writes and the payload does not carry.
# They are listed here so that the schema consistency gate can account for every
# column in the warehouse table rather than ignoring the ones it does not
# recognise, which is how a gate quietly stops covering half of a schema.
WAREHOUSE_ONLY_COLUMN_NAMES: Tuple[str, ...] = (
    "validation_outcome_is_accepted",
    "validation_rule_results",
    "ingestion_source_object_path",
)

FIELD_CONTRACTS_BY_NAME = {
    contract.payload_field_name: contract for contract in FIELD_CONTRACTS
}
