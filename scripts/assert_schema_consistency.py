"""Habot Connect FZCO - Hiring Project.

Position: Junior Cloud and Development Operations Engineer.
Candidate Full Name: Anuradha.
Candidate Electronic Mail Address: anuu.21092004@gmail.com.

File purpose: the schema consistency gate. Fails the build when the application
field contract and the warehouse table schema disagree.

Poka-Yoke rationale for this file
---------------------------------
This is the direct answer to the second half of the incident described in the
project brief. A junior developer triggered a database schema mismatch that
broke downstream analytics. That was possible because the application schema and
the warehouse schema were two documents kept in step by memory.

This script makes them one document with a proof. It runs on every commit. It
compares four properties of every field, and it fails on any disagreement in any
direction. It also fails when a column exists that neither the contract nor the
declared list of warehouse only columns accounts for, so the gate cannot quietly
stop covering part of the schema.

The script writes nothing and changes nothing. A gate that repairs the problem
it finds teaches engineers to ignore it.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
APPLICATION_SOURCE_ROOT = REPOSITORY_ROOT / "task-03-schema-mapping-and-data-validation"
WAREHOUSE_SCHEMA_PATH = (
    REPOSITORY_ROOT
    / "task-01-terraform-secure-staging-provisioning"
    / "schemas"
    / "student_onboarding_submissions_schema.json"
)

sys.path.insert(0, str(APPLICATION_SOURCE_ROOT))

from dcyn_library.field_contract import (  # noqa: E402
    FIELD_CONTRACTS,
    MAXIMUM_RULE_IDENTIFIER_LENGTH,
    MAXIMUM_RULE_QUESTION_LENGTH,
    WAREHOUSE_ONLY_COLUMN_NAMES,
)

# The limits that the repeated audit record must declare, keyed by the name of
# the nested field. Held here rather than inside the comparison so that adding a
# nested field to the audit record is a one line change that the gate then
# enforces.
AUDIT_RECORD_LENGTH_LIMITS = {
    "rule_identifier": MAXIMUM_RULE_IDENTIFIER_LENGTH,
    "rule_question": MAXIMUM_RULE_QUESTION_LENGTH,
}


def load_warehouse_columns() -> Dict[str, dict]:
    """Return the warehouse table schema keyed by column name."""
    with WAREHOUSE_SCHEMA_PATH.open(encoding="utf-8") as schema_file:
        declared_columns = json.load(schema_file)
    return {column["name"]: column for column in declared_columns}


def _compare_one_field(contract, warehouse_columns: Dict[str, dict]) -> List[str]:
    """Return every disagreement concerning one contract field."""
    column_name = contract.warehouse_column_name
    if column_name not in warehouse_columns:
        return [
            "The field contract declares the field named "
            + contract.payload_field_name
            + " which maps to the warehouse column named "
            + column_name
            + ", but that column does not exist in the warehouse schema."
        ]

    column = warehouse_columns[column_name]
    disagreements: List[str] = []

    if column["type"] != contract.warehouse_data_type:
        disagreements.append(
            "The column named "
            + column_name
            + " is declared in the warehouse as type "
            + str(column["type"])
            + " but the field contract declares it as type "
            + contract.warehouse_data_type
            + "."
        )

    if column["mode"] != contract.warehouse_mode:
        disagreements.append(
            "The column named "
            + column_name
            + " is declared in the warehouse with mode "
            + str(column["mode"])
            + " but the field contract declares mode "
            + contract.warehouse_mode
            + "."
        )

    disagreements.extend(
        _compare_one_maximum_length(
            column_name,
            column.get("maxLength"),
            contract.maximum_character_length,
        )
    )

    return disagreements


def _compare_one_maximum_length(
    column_name: str,
    declared_maximum_length,
    contract_maximum_length,
) -> List[str]:
    """Return the disagreement, if any, about one maximum length."""
    if contract_maximum_length is None and declared_maximum_length is None:
        return []

    if contract_maximum_length is None:
        return [
            "The column named "
            + column_name
            + " declares a maximum length of "
            + str(declared_maximum_length)
            + " in the warehouse but the field contract declares none."
        ]

    if declared_maximum_length is None:
        return [
            "The field contract declares a maximum length of "
            + str(contract_maximum_length)
            + " for the column named "
            + column_name
            + " but the warehouse declares none."
        ]

    if int(declared_maximum_length) != int(contract_maximum_length):
        return [
            "The column named "
            + column_name
            + " declares a maximum length of "
            + str(declared_maximum_length)
            + " in the warehouse but the field contract declares "
            + str(contract_maximum_length)
            + "."
        ]

    return []


def _detect_unaccounted_columns(warehouse_columns: Dict[str, dict]) -> List[str]:
    """Return a disagreement for every column nothing accounts for."""
    contract_field_names = {contract.payload_field_name for contract in FIELD_CONTRACTS}
    accounted_column_names = contract_field_names | set(WAREHOUSE_ONLY_COLUMN_NAMES)

    return [
        "The warehouse declares a column named "
        + column_name
        + " which is neither declared in the field contract nor listed as a "
        + "warehouse only column. Every column must be accounted for, so that "
        + "this gate cannot silently stop covering part of the schema."
        for column_name in warehouse_columns
        if column_name not in accounted_column_names
    ]


def _detect_missing_warehouse_only_columns(
    warehouse_columns: Dict[str, dict],
) -> List[str]:
    """Return a disagreement for every declared column that is absent."""
    return [
        "The column named "
        + column_name
        + " is listed as a warehouse only column but does not exist in the "
        + "warehouse schema."
        for column_name in WAREHOUSE_ONLY_COLUMN_NAMES
        if column_name not in warehouse_columns
    ]


def _compare_audit_record(warehouse_columns: Dict[str, dict]) -> List[str]:
    """Return every disagreement about the repeated audit record.

    Without this comparison the rule question column could be narrowed and
    every question would be truncated on load, which is exactly the class of
    silent failure that this project exists to remove.
    """
    audit_record_column = warehouse_columns.get("validation_rule_results")
    if audit_record_column is None:
        return [
            "The warehouse declares no column named validation_rule_results, "
            "so the answers of the validation library have nowhere to be "
            "recorded and no audit of an acceptance would be possible."
        ]

    nested_fields = {
        nested_field["name"]: nested_field
        for nested_field in audit_record_column.get("fields", [])
    }
    disagreements: List[str] = []

    for nested_field_name, expected_length in AUDIT_RECORD_LENGTH_LIMITS.items():
        if nested_field_name not in nested_fields:
            disagreements.append(
                "The audit record declares no nested field named "
                + nested_field_name
                + "."
            )
            continue

        declared_length = nested_fields[nested_field_name].get("maxLength")
        if declared_length is None or int(declared_length) != int(expected_length):
            disagreements.append(
                "The nested audit field named "
                + nested_field_name
                + " declares a maximum length of "
                + str(declared_length)
                + " in the warehouse but the validation library is bounded at "
                + str(expected_length)
                + "."
            )

    return disagreements


def collect_disagreements() -> List[str]:
    """Return every disagreement between the contract and the warehouse.

    Four directions are compared. Comparing in only one direction would let a
    column be added, or a field be removed, without the gate noticing.
    """
    warehouse_columns = load_warehouse_columns()
    disagreements: List[str] = []

    # Direction one. Every contract field must exist as a warehouse column and
    # must agree with it on type, mode and maximum length.
    for contract in FIELD_CONTRACTS:
        disagreements.extend(_compare_one_field(contract, warehouse_columns))

    # Direction two. Every warehouse column must be accounted for.
    disagreements.extend(_detect_unaccounted_columns(warehouse_columns))

    # Direction three. The nested audit record must agree with the bounds that
    # the validation library is written to.
    disagreements.extend(_compare_audit_record(warehouse_columns))

    # Direction four. Every declared warehouse only column must actually exist.
    disagreements.extend(_detect_missing_warehouse_only_columns(warehouse_columns))

    return disagreements


def main() -> int:
    """Run the gate and return the process exit status."""
    disagreements = collect_disagreements()

    warehouse_column_count = len(load_warehouse_columns())
    print("Warehouse columns examined: " + str(warehouse_column_count))
    print("Field contract entries examined: " + str(len(FIELD_CONTRACTS)))

    if warehouse_column_count == 0 or len(FIELD_CONTRACTS) == 0:
        print(
            "FAIL CLOSED. Either the warehouse schema or the field contract is "
            "empty, so this gate has nothing to compare and cannot be "
            "meaningful."
        )
        return 1

    if disagreements:
        print("")
        print("FAIL CLOSED. The application and the warehouse disagree.")
        for disagreement in disagreements:
            print("  - " + disagreement)
        print("")
        print(
            "Correct the field contract and the warehouse schema together. They "
            "describe one thing and must say the same thing about it."
        )
        return 1

    print("The application field contract and the warehouse schema agree exactly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
