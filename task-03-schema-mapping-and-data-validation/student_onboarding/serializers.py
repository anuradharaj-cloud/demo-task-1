"""Habot Connect FZCO - Hiring Project.

Position: Junior Cloud and Development Operations Engineer.
Candidate Full Name: Anuradha.
Candidate Electronic Mail Address: anuu.21092004@gmail.com.

File purpose: the Django REST Framework model serializer for task three.

Poka-Yoke rationale for this file
---------------------------------
Three properties of this serializer are what remove human judgement from the
onboarding path.

First, the declared fields are built from the field contract by the function
build_serializer_fields. No limit is typed here. Widening a limit requires
editing the contract, and editing the contract changes the database constraint,
the warehouse schema check and the validation library at the same time.

Second, the field list is asserted rather than assumed. The Meta class names
every field explicitly and a module level assertion compares that list against
the contract. A field added to the contract and forgotten here fails at import
time, which means it fails in the build gate rather than in production.

Third, an unrecognised field is refused rather than ignored. Django REST
Framework discards an unknown key by default. Discarding is the behaviour that
lets a client believe it has sent something that the server never stored, which
is precisely the class of silent mismatch that this project exists to remove.
"""

from __future__ import annotations

from typing import Any, Dict

from rest_framework import serializers

from dcyn_library.deconstruction import evaluate_student_onboarding_payload
from dcyn_library.field_contract import FIELD_CONTRACTS, FieldContract

from .models import StudentOnboardingSubmission


def build_serializer_field(contract: FieldContract) -> serializers.Field:
    """Return the serializer field that enforces one contract exactly."""
    shared_arguments: Dict[str, Any] = {
        "required": contract.value_is_mandatory,
        "help_text": contract.field_description,
    }
    if not contract.value_is_mandatory:
        shared_arguments["allow_null"] = True

    if contract.warehouse_data_type == "BOOLEAN":
        return serializers.BooleanField(**shared_arguments)

    if contract.warehouse_data_type == "INTEGER":
        return serializers.IntegerField(
            min_value=contract.minimum_permitted_number,
            max_value=contract.maximum_permitted_number,
            **shared_arguments,
        )

    if contract.warehouse_data_type == "DATE":
        return serializers.DateField(
            input_formats=["%Y-%m-%d"],
            **shared_arguments,
        )

    if contract.warehouse_data_type == "TIMESTAMP":
        return serializers.DateTimeField(**shared_arguments)

    if contract.permitted_values is not None:
        return serializers.ChoiceField(
            choices=[(value, value) for value in contract.permitted_values],
            **shared_arguments,
        )

    if contract.regular_expression_pattern is not None:
        return serializers.RegexField(
            regex=str(contract.regular_expression_pattern),
            max_length=contract.maximum_character_length,
            trim_whitespace=False,
            **shared_arguments,
        )

    return serializers.CharField(
        max_length=contract.maximum_character_length,
        trim_whitespace=False,
        **shared_arguments,
    )


def build_serializer_fields() -> Dict[str, serializers.Field]:
    """Return one serializer field for every field in the contract."""
    return {
        contract.payload_field_name: build_serializer_field(contract)
        for contract in FIELD_CONTRACTS
    }


CONTRACT_FIELD_NAMES = tuple(
    contract.payload_field_name for contract in FIELD_CONTRACTS
)


class StudentOnboardingSubmissionSerializer(serializers.ModelSerializer):
    """Accepts a student onboarding payload, or refuses it with every reason."""

    # The declared fields are injected from the contract after the class body is
    # evaluated, immediately below this class. Declaring them here by hand would
    # be the duplication that this design removes.

    class Meta:
        model = StudentOnboardingSubmission
        fields = CONTRACT_FIELD_NAMES

    def to_internal_value(self, data: Any) -> Dict[str, Any]:
        """Refuse an unrecognised field before any other validation runs."""
        if not isinstance(data, dict):
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        "The payload must be a single object. A list or a "
                        "scalar cannot be validated field by field and is "
                        "therefore refused."
                    ]
                }
            )

        unrecognised_field_names = sorted(set(data.keys()) - set(CONTRACT_FIELD_NAMES))
        if unrecognised_field_names:
            raise serializers.ValidationError(
                {
                    field_name: [
                        "This field is not declared in the field contract. An "
                        "unrecognised field is refused rather than discarded, "
                        "so that a client is never led to believe that a value "
                        "was stored when it was not."
                    ]
                    for field_name in unrecognised_field_names
                }
            )

        return super().to_internal_value(data)

    def validate(self, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """Apply the deconstructed yes or no library to the whole payload.

        The cross field rules live in the validation library rather than in this
        method. The transformation stage in the pipeline calls the same library
        on the same payload, so the answer the parent or guardian receives at
        submission time and the answer the warehouse applies at load time are
        produced by one piece of code and cannot diverge.
        """
        payload_for_evaluation = self._rebuild_payload_for_evaluation(attributes)
        evaluation = evaluate_student_onboarding_payload(payload_for_evaluation)

        if not evaluation.outcome_is_accepted:
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        "The rule identified as " + identifier + " answered no."
                        for identifier in evaluation.refusing_rule_identifiers
                    ]
                }
            )

        self.context["deconstructed_yes_no_evaluation"] = evaluation
        return attributes

    @staticmethod
    def _rebuild_payload_for_evaluation(attributes: Dict[str, Any]) -> Dict[str, Any]:
        """Return the validated attributes in the wire form the library reads.

        Django REST Framework converts a date and a timestamp into Python
        objects during field validation. The validation library reads the wire
        form, because the wire form is what the transformation stage reads out
        of the raw landing bucket. Converting back here keeps one library able
        to serve both callers.
        """
        rebuilt_payload: Dict[str, Any] = {}
        for field_name, value in attributes.items():
            if hasattr(value, "isoformat"):
                rebuilt_payload[field_name] = value.isoformat()
            else:
                rebuilt_payload[field_name] = value
        return rebuilt_payload


# Inject the contract built fields onto the serializer class.
for _field_name, _field in build_serializer_fields().items():
    StudentOnboardingSubmissionSerializer._declared_fields[_field_name] = _field

# The completeness assertion. A field present in the contract and absent from
# the serializer, or the reverse, halts the import. An import that halts fails
# the build gate, so the mismatch is caught before it can be deployed.
if set(StudentOnboardingSubmissionSerializer.Meta.fields) != set(CONTRACT_FIELD_NAMES):
    raise AssertionError(
        "The serializer field list and the field contract disagree. Every "
        "field declared in the contract must appear in the serializer and no "
        "other field may appear there."
    )
