"""Habot Connect FZCO - Hiring Project.

Position: Junior Cloud and Development Operations Engineer.
Candidate Full Name: Anuradha.
Candidate Electronic Mail Address: anuu.21092004@gmail.com.

File purpose: generate the schema mapping workbook from the field contract.

Poka-Yoke rationale for this file
---------------------------------
The workbook is generated, never typed. A mapping document that a person
maintains by hand is a fourth copy of the schema, and a fourth copy is a fourth
thing that can fall out of step with the other three. Because this script reads
the same field contract that the serializer and the warehouse comparison read,
the workbook cannot describe a field that does not exist or state a limit that
is not enforced.

Every worksheet has wrap text enabled on every cell, as the project brief
requires, and every heading and value is written in full words.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
APPLICATION_SOURCE_ROOT = REPOSITORY_ROOT / "task-03-schema-mapping-and-data-validation"
OUTPUT_PATH = (
    REPOSITORY_ROOT / "schema-mapping" / "student_onboarding_schema_mapping.xlsx"
)

sys.path.insert(0, str(APPLICATION_SOURCE_ROOT))

from dcyn_library import (  # noqa: E402
    FIELD_CONTRACTS,
    WAREHOUSE_ONLY_COLUMN_NAMES,
    DeconstructedYesNoEvaluator,
)
from dcyn_library.field_contract import (  # noqa: E402
    MAXIMUM_STUDENT_AGE_IN_COMPLETE_YEARS,
    MAXIMUM_SUBMISSION_AGE_IN_DAYS,
    MINIMUM_STUDENT_AGE_IN_COMPLETE_YEARS,
    PERMITTED_LEARNING_SUPPORT_CATEGORIES,
    PERMITTED_LOCAL_AUTHORITY_NAMES,
    PERMITTED_SESSION_LANGUAGES,
)

CANDIDATE_FULL_NAME = "Anuradha"
CANDIDATE_EMAIL_ADDRESS = "anuu.21092004@gmail.com"

WORKBOOK_FONT_NAME = "Arial"
HEADING_FILL = PatternFill("solid", fgColor="1F3864")
HEADING_FONT = Font(name=WORKBOOK_FONT_NAME, size=10, bold=True, color="FFFFFF")
BODY_FONT = Font(name=WORKBOOK_FONT_NAME, size=10)
TITLE_FONT = Font(name=WORKBOOK_FONT_NAME, size=12, bold=True, color="1F3864")
WRAPPED_ALIGNMENT = Alignment(wrap_text=True, vertical="top", horizontal="left")
THIN_BORDER = Border(
    left=Side(style="thin", color="BFBFBF"),
    right=Side(style="thin", color="BFBFBF"),
    top=Side(style="thin", color="BFBFBF"),
    bottom=Side(style="thin", color="BFBFBF"),
)


def write_table(
    worksheet,
    title: str,
    explanation: str,
    headings: List[str],
    rows: List[List[str]],
    column_widths: List[int],
) -> None:
    """Write one titled, fully wrapped table onto a worksheet."""
    worksheet["A1"] = title
    worksheet["A1"].font = TITLE_FONT
    worksheet["A2"] = explanation
    worksheet["A2"].font = BODY_FONT

    heading_row_index = 4
    for column_index, heading in enumerate(headings, start=1):
        cell = worksheet.cell(row=heading_row_index, column=column_index)
        cell.value = heading
        cell.font = HEADING_FONT
        cell.fill = HEADING_FILL
        cell.border = THIN_BORDER

    for row_offset, row_values in enumerate(rows, start=heading_row_index + 1):
        for column_index, value in enumerate(row_values, start=1):
            cell = worksheet.cell(row=row_offset, column=column_index)
            cell.value = value
            cell.font = BODY_FONT
            cell.border = THIN_BORDER

    for column_index, width in enumerate(column_widths, start=1):
        worksheet.column_dimensions[get_column_letter(column_index)].width = width

    # The project brief requires wrap text on every worksheet used for data or
    # schema mapping. It is applied to every cell in the used range rather than
    # to the table alone, so that a cell added later inherits it.
    for row in worksheet.iter_rows(
        min_row=1,
        max_row=worksheet.max_row,
        min_col=1,
        max_col=max(len(headings), 1),
    ):
        for cell in row:
            cell.alignment = WRAPPED_ALIGNMENT

    worksheet.row_dimensions[1].height = 20
    worksheet.row_dimensions[2].height = 32
    worksheet.freeze_panes = worksheet.cell(row=heading_row_index + 1, column=1)


def describe_limits(contract) -> str:
    """Return every limit of one field, written out in full words."""
    stated_limits: List[str] = []

    if contract.maximum_character_length is not None:
        stated_limits.append(
            "Maximum length is "
            + str(contract.maximum_character_length)
            + " characters."
        )
    if contract.minimum_permitted_number is not None:
        stated_limits.append(
            "Minimum permitted number is "
            + str(contract.minimum_permitted_number)
            + "."
        )
    if contract.maximum_permitted_number is not None:
        stated_limits.append(
            "Maximum permitted number is "
            + str(contract.maximum_permitted_number)
            + "."
        )
    if contract.permitted_values is not None:
        stated_limits.append(
            "Restricted to "
            + str(len(contract.permitted_values))
            + " permitted values, listed on the worksheet named Permitted "
            + "Value Lists."
        )
    if contract.regular_expression_explanation is not None:
        stated_limits.append(
            "Required form is: " + contract.regular_expression_explanation
        )
    if contract.warehouse_data_type == "BOOLEAN":
        stated_limits.append("Must be stated as either true or false.")

    return " ".join(stated_limits)


def build_workbook() -> Workbook:
    """Assemble every worksheet of the schema mapping workbook."""
    workbook = Workbook()

    # -------------------------------------------------------------------------
    read_me_sheet = workbook.active
    read_me_sheet.title = "Read Me First"

    evaluator = DeconstructedYesNoEvaluator()
    read_me_rows = [
        ["Candidate full name", CANDIDATE_FULL_NAME],
        ["Candidate electronic mail address", CANDIDATE_EMAIL_ADDRESS],
        [
            "Position applied for",
            "Junior Cloud and Development Operations Engineer, "
            "Google Cloud Platform with Django and React",
        ],
        ["Organisation", "Habot Connect FZCO, Dubai"],
        [
            "What this workbook contains",
            "The complete mapping from the student onboarding payload that the "
            "Django REST Framework application accepts, through the "
            "deconstructed yes or no validation library, into the BigQuery "
            "table in the enforced analytics layer.",
        ],
        [
            "How this workbook was produced",
            "It was generated by the script named "
            "build_schema_mapping_workbook.py, which reads the same field "
            "contract that the application serializer and the warehouse "
            "comparison read. It was not typed by hand. A mapping document "
            "maintained by hand is an additional copy of the schema, and an "
            "additional copy is an additional thing that can fall out of step.",
        ],
        [
            "How to regenerate it",
            "Run the command: python3 scripts/build_schema_mapping_workbook.py",
        ],
        [
            "Number of payload fields described",
            "=COUNTA('Field To Column Mapping'!A5:A100)",
        ],
        [
            "Number of validation rules described",
            "=COUNTA('Validation Rule Register'!A5:A200)",
        ],
        [
            "Number of columns written only by the transformation stage",
            str(len(WAREHOUSE_ONLY_COLUMN_NAMES)),
        ],
        [
            "Number of rules the validation library applies in total",
            str(evaluator.rule_count),
        ],
    ]
    write_table(
        read_me_sheet,
        "Student Onboarding Schema Mapping",
        "Read this worksheet before the others. Every worksheet in this "
        "workbook has wrap text enabled and uses full words throughout, with "
        "no abbreviation and no placeholder.",
        ["Item", "Description"],
        read_me_rows,
        [52, 96],
    )

    # -------------------------------------------------------------------------
    mapping_sheet = workbook.create_sheet("Field To Column Mapping")
    mapping_rows = []
    for contract in FIELD_CONTRACTS:
        mapping_rows.append(
            [
                contract.payload_field_name,
                "Mandatory" if contract.value_is_mandatory else "Optional",
                describe_limits(contract),
                contract.warehouse_column_name,
                contract.warehouse_data_type,
                contract.warehouse_mode,
                (
                    "Withheld from the reporting view"
                    if contract.is_direct_identifier
                    else "Present in the reporting view"
                ),
                contract.field_description,
            ]
        )

    for column_name in WAREHOUSE_ONLY_COLUMN_NAMES:
        mapping_rows.append(
            [
                "Not present in the payload",
                "Written by the transformation stage",
                "Populated by the transformation stage after the validation "
                "library has answered every rule.",
                column_name,
                "Varies by column. See the warehouse schema file.",
                "REQUIRED",
                (
                    "Present in the reporting view"
                    if column_name == "validation_outcome_is_accepted"
                    else "Withheld from the reporting view"
                ),
                "Written by the transformation stage so that every accepted "
                "row can be traced back to the exact evidence on which it was "
                "accepted.",
            ]
        )

    write_table(
        mapping_sheet,
        "Field To Column Mapping",
        "One row for each field of the student onboarding payload, followed by "
        "the columns that only the transformation stage writes. The limits "
        "stated here are the limits that the application actually enforces, "
        "because both are read from one field contract.",
        [
            "Payload field name",
            "Whether the value is mandatory",
            "Limits enforced on the value",
            "Warehouse column name",
            "Warehouse data type",
            "Warehouse mode",
            "Treatment in the reporting view",
            "Description",
        ],
        mapping_rows,
        [34, 22, 62, 34, 22, 16, 26, 56],
    )

    # -------------------------------------------------------------------------
    rule_sheet = workbook.create_sheet("Validation Rule Register")
    rule_rows = []
    evaluation = evaluator.evaluate({})
    for answer in evaluation.rule_answers:
        rule_category = answer.rule_identifier.split(".")[0]
        rule_rows.append(
            [
                answer.rule_identifier,
                rule_category,
                answer.rule_question,
                "Yes or no. There is no other possible answer.",
            ]
        )

    write_table(
        rule_sheet,
        "Validation Rule Register",
        "Every rule that the deconstructed yes or no validation library "
        "applies to a submission. A submission is accepted only when every one "
        "of these rules answers yes. There is no weighting, no threshold and "
        "no override, so no reviewer is ever asked to form a judgement.",
        [
            "Rule identifier",
            "Rule category",
            "The question that the rule answers",
            "Possible answers",
        ],
        rule_rows,
        [40, 20, 98, 40],
    )

    # -------------------------------------------------------------------------
    permitted_values_sheet = workbook.create_sheet("Permitted Value Lists")
    permitted_value_rows = []
    for value in PERMITTED_LEARNING_SUPPORT_CATEGORIES:
        permitted_value_rows.append(["learning_support_category", value])
    for value in PERMITTED_SESSION_LANGUAGES:
        permitted_value_rows.append(["preferred_session_language", value])
    for value in PERMITTED_LOCAL_AUTHORITY_NAMES:
        permitted_value_rows.append(["assigned_local_authority_name", value])

    write_table(
        permitted_values_sheet,
        "Permitted Value Lists",
        "The complete set of values that each restricted field accepts. A "
        "value outside these lists is refused by the serializer and by the "
        "validation library, and can therefore never reach the warehouse.",
        ["Payload field name", "Permitted value"],
        permitted_value_rows,
        [40, 64],
    )

    # -------------------------------------------------------------------------
    data_flow_sheet = workbook.create_sheet("Data Flow And Access")
    data_flow_rows = [
        [
            "Stage one. Submission",
            "The parent or guardian submits the onboarding form.",
            "The Django REST Framework serializer applies every field limit and "
            "then applies the deconstructed yes or no validation library.",
            "Not applicable",
            "A submission that fails any rule is refused at this point and is "
            "never written anywhere.",
        ],
        [
            "Stage two. Raw landing, named D0 Raw Landing",
            "The accepted payload is written as an object into the Google "
            "Cloud Storage bucket named "
            "habotconnect-d0-raw-landing-staging.",
            "The bucket enforces uniform bucket level access, prevents public "
            "access, and encrypts every object with a customer managed key "
            "that rotates every ninety days.",
            "onboarding-ingestion-writer",
            "This identity may create an object beneath the student onboarding "
            "path and may do nothing else. It cannot read what it has written "
            "and it cannot list the bucket.",
        ],
        [
            "Stage three. Transformation",
            "The transformation stage reads the object, applies the same "
            "validation library a second time, and appends the row.",
            "The same library runs at submission and at load, so the answer "
            "the parent receives and the answer the warehouse applies cannot "
            "differ.",
            "onboarding-transform-runner",
            "This identity may read the landing path and may append to the "
            "enforced table. It cannot delete data.",
        ],
        [
            "Stage four. Enforced layer, named D1 Staged and Enforced",
            "The row is written into the BigQuery table named "
            "student_onboarding_submissions.",
            "The table is partitioned by day on the submission timestamp, "
            "clustered by local authority and support category, and requires a "
            "partition filter on every query.",
            "Not applicable",
            "A native row access policy filters rows by the local authority "
            "that the querying analyst is entitled to.",
        ],
        [
            "Stage five. Reporting",
            "The reporting layer queries the authorised view named "
            "student_onboarding_submissions_reporting_view.",
            "The view excludes every direct identifier of the child and of the "
            "parent or guardian.",
            "support-analytics-reader",
            "This identity holds no permission at all on the underlying table. "
            "The authorised view is its only route to the data, which is what "
            "makes the row level filter impossible to bypass.",
        ],
    ]

    write_table(
        data_flow_sheet,
        "Data Flow And Access",
        "The path that one submission takes, and the identity that acts at "
        "each stage. No identity spans two stages, which is what allows every "
        "permission to be granted at the narrowest possible scope.",
        [
            "Stage",
            "What happens",
            "The control that applies",
            "The identity that acts",
            "Why the control is structural rather than advisory",
        ],
        data_flow_rows,
        [34, 52, 60, 34, 60],
    )

    # -------------------------------------------------------------------------
    assumptions_sheet = workbook.create_sheet("Stated Assumptions")
    assumptions_rows = [
        [
            "Region",
            "europe-west2, which is London",
            "The platform supports learning support assistants working with "
            "children resident in the United Kingdom, so the personal data of "
            "those children is held in the United Kingdom. The region variable "
            "carries a validation rule that refuses any other region.",
        ],
        [
            "Student age range",
            "From "
            + str(MINIMUM_STUDENT_AGE_IN_COMPLETE_YEARS)
            + " to "
            + str(MAXIMUM_STUDENT_AGE_IN_COMPLETE_YEARS)
            + " complete years",
            "This is the age range served by the national curriculum year "
            "groups one to thirteen that the platform supports.",
        ],
        [
            "Submission freshness window",
            str(MAXIMUM_SUBMISSION_AGE_IN_DAYS) + " days",
            "A submission timestamp older than this window, or later than the "
            "instant of evaluation, indicates either a clock problem or a "
            "replayed payload. Both are refused.",
        ],
        [
            "Raw landing retention",
            "30 days",
            "Raw personal data is deleted automatically once it has been "
            "promoted to the enforced layer, so that nobody has to remember to "
            "clean it up.",
        ],
        [
            "Encryption key rotation",
            "Every 90 days",
            "The variable carries a validation rule that refuses a longer "
            "rotation period.",
        ],
        [
            "Local authority list",
            "Eight named local authorities",
            "These are the authorities that the staging estate is configured "
            "for. Adding one is an edit to the field contract, which the build "
            "gate then propagates to every consumer.",
        ],
    ]

    write_table(
        assumptions_sheet,
        "Stated Assumptions",
        "Every assumption made in this submission, stated openly with the "
        "reason for it. An assumption that is not written down is an "
        "assumption that the next engineer has to rediscover.",
        ["Assumption", "Value chosen", "Reason for the choice"],
        assumptions_rows,
        [38, 40, 92],
    )

    return workbook


def main() -> int:
    """Build the workbook and report where it was written."""
    workbook = build_workbook()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(OUTPUT_PATH)

    print("Workbook written to " + str(OUTPUT_PATH))
    print("Worksheets: " + ", ".join(workbook.sheetnames))
    print(
        "Two summary cells on the first worksheet are formulas. Open the "
        "workbook once in a spreadsheet application so that their values are "
        "cached, or leave them to calculate on open."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
