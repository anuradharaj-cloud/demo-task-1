"""Habot Connect FZCO - Hiring Project.

Position: Junior Cloud and Development Operations Engineer.
Candidate Full Name: Anuradha.
Candidate Electronic Mail Address: anuradha@tecofize.com.

File purpose: tests of the schema consistency gate itself.

A gate is a piece of software and can be wrong. These tests prove that the gate
reports agreement when the two schemas agree, and that it reports disagreement
when they do not, so that a green result from the gate means something.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent.parent
GATE_SCRIPT_PATH = REPOSITORY_ROOT / "scripts" / "assert_schema_consistency.py"
WAREHOUSE_SCHEMA_PATH = (
    REPOSITORY_ROOT
    / "task-01-terraform-secure-staging-provisioning"
    / "schemas"
    / "student_onboarding_submissions_schema.json"
)


def load_gate_module():
    """Import the gate script as a module so that it can be called directly."""
    specification = importlib.util.spec_from_file_location(
        "assert_schema_consistency", GATE_SCRIPT_PATH
    )
    module = importlib.util.module_from_spec(specification)
    sys.modules["assert_schema_consistency"] = module
    specification.loader.exec_module(module)
    return module


def test_the_gate_script_exists() -> None:
    """The build gate calls this script by path, so the path must be right."""
    assert GATE_SCRIPT_PATH.is_file()


def test_the_warehouse_schema_is_valid_json() -> None:
    """Terraform reads this file, so malformed content would fail at apply."""
    with WAREHOUSE_SCHEMA_PATH.open(encoding="utf-8") as schema_file:
        declared_columns = json.load(schema_file)
    assert isinstance(declared_columns, list)
    assert len(declared_columns) > 0


def test_every_warehouse_column_declares_a_description() -> None:
    """An undescribed column is a column the next engineer guesses at."""
    with WAREHOUSE_SCHEMA_PATH.open(encoding="utf-8") as schema_file:
        declared_columns = json.load(schema_file)
    for column in declared_columns:
        assert column.get("description", "").strip() != "", (
            "The column named " + str(column.get("name")) + " declares no description."
        )


def test_the_application_and_the_warehouse_agree() -> None:
    """The gate must report no disagreement for the committed schemas."""
    gate_module = load_gate_module()
    disagreements = gate_module.collect_disagreements()
    assert disagreements == [], "\n".join(disagreements)


def test_the_gate_returns_success_for_the_committed_schemas() -> None:
    """The exit status the pipeline reads must be zero."""
    gate_module = load_gate_module()
    assert gate_module.main() == 0


def test_the_gate_detects_a_removed_column(tmp_path: Path) -> None:
    """A gate that cannot fail is not a gate."""
    gate_module = load_gate_module()

    with WAREHOUSE_SCHEMA_PATH.open(encoding="utf-8") as schema_file:
        declared_columns = json.load(schema_file)

    damaged_columns = [
        column for column in declared_columns if column["name"] != "home_postal_code"
    ]
    damaged_schema_path = tmp_path / "damaged_schema.json"
    damaged_schema_path.write_text(json.dumps(damaged_columns), encoding="utf-8")

    original_schema_path = gate_module.WAREHOUSE_SCHEMA_PATH
    try:
        gate_module.WAREHOUSE_SCHEMA_PATH = damaged_schema_path
        disagreements = gate_module.collect_disagreements()
    finally:
        gate_module.WAREHOUSE_SCHEMA_PATH = original_schema_path

    assert any("home_postal_code" in message for message in disagreements)


def test_the_gate_detects_a_changed_maximum_length(tmp_path: Path) -> None:
    """A widened column must be reported even though nothing was removed."""
    gate_module = load_gate_module()

    with WAREHOUSE_SCHEMA_PATH.open(encoding="utf-8") as schema_file:
        declared_columns = json.load(schema_file)

    for column in declared_columns:
        if column["name"] == "student_given_name":
            column["maxLength"] = "255"

    damaged_schema_path = tmp_path / "widened_schema.json"
    damaged_schema_path.write_text(json.dumps(declared_columns), encoding="utf-8")

    original_schema_path = gate_module.WAREHOUSE_SCHEMA_PATH
    try:
        gate_module.WAREHOUSE_SCHEMA_PATH = damaged_schema_path
        disagreements = gate_module.collect_disagreements()
    finally:
        gate_module.WAREHOUSE_SCHEMA_PATH = original_schema_path

    assert any("student_given_name" in message for message in disagreements)


def test_the_gate_detects_an_unaccounted_column(tmp_path: Path) -> None:
    """A new column that nothing knows about must be reported."""
    gate_module = load_gate_module()

    with WAREHOUSE_SCHEMA_PATH.open(encoding="utf-8") as schema_file:
        declared_columns = json.load(schema_file)

    declared_columns.append(
        {
            "name": "undocumented_new_column",
            "type": "STRING",
            "mode": "NULLABLE",
            "description": "Added without updating the field contract.",
        }
    )

    damaged_schema_path = tmp_path / "extended_schema.json"
    damaged_schema_path.write_text(json.dumps(declared_columns), encoding="utf-8")

    original_schema_path = gate_module.WAREHOUSE_SCHEMA_PATH
    try:
        gate_module.WAREHOUSE_SCHEMA_PATH = damaged_schema_path
        disagreements = gate_module.collect_disagreements()
    finally:
        gate_module.WAREHOUSE_SCHEMA_PATH = original_schema_path

    assert any("undocumented_new_column" in message for message in disagreements)
