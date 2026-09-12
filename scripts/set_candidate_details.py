"""Habot Connect FZCO - Hiring Project.

Position: Junior Cloud and Development Operations Engineer.
Candidate Full Name: Anuradha.
Candidate Electronic Mail Address: anuu.21092004@gmail.com.

File purpose: stamp the candidate name, electronic mail address and telephone
number into the header of every file in the submission.

The project brief requires the answer document and the code files to be clearly
labelled with the full name and contact information of the candidate at the top.
This script does that in one pass rather than leaving it to be done by hand file
by file, which is how one file ends up without a header.

Usage:

    python3 scripts/set_candidate_details.py \\
        --full-name "Your Full Name" \\
        --email-address "you@example.com" \\
        --telephone-number "+91 90000 00000"

The telephone number is optional. When it is supplied, a telephone line is added
immediately beneath the electronic mail address line in every file that has one,
and when it is omitted no telephone line is written. Run the script again with a
different value to change it; running twice does not produce two lines.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import List

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent

CURRENT_FULL_NAME = "Anuradha"
CURRENT_EMAIL_ADDRESS = "anuu.21092004@gmail.com"

SEARCHED_SUFFIXES = {
    ".py",
    ".tf",
    ".tfvars",
    ".yml",
    ".yaml",
    ".toml",
    ".cfg",
    ".hcl",
    ".md",
    ".sh",
    ".js",
    ".txt",
}

SKIPPED_DIRECTORY_NAMES = {
    ".git",
    ".terraform",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
}


def collect_files() -> List[Path]:
    """Return every file in the submission that may carry a header."""
    collected: List[Path] = []
    for path in REPOSITORY_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIPPED_DIRECTORY_NAMES for part in path.parts):
            continue
        if path.suffix.lower() not in SEARCHED_SUFFIXES:
            continue
        collected.append(path)
    return sorted(collected)


def rewrite_one_file(
    path: Path,
    full_name: str,
    email_address: str,
    telephone_number: str,
) -> bool:
    """Rewrite the header of one file. Return whether anything changed."""
    original_text = path.read_text(encoding="utf-8")
    updated_text = original_text

    updated_text = updated_text.replace(CURRENT_FULL_NAME, full_name)
    updated_text = updated_text.replace(CURRENT_EMAIL_ADDRESS, email_address)

    # Remove any telephone line written by a previous run, so that running the
    # script twice cannot leave two of them.
    updated_text = re.sub(
        r"^.{0,4}Candidate Telephone Number: .*\n",
        "",
        updated_text,
        flags=re.MULTILINE,
    )
    updated_text = re.sub(
        r"^\*\*Candidate telephone number:\*\* .*\n",
        "",
        updated_text,
        flags=re.MULTILINE,
    )

    if telephone_number:
        updated_text = re.sub(
            r"^(?P<prefix>.{0,4})Candidate Electronic Mail Address: (?P<address>.*)$",
            lambda match: (
                match.group("prefix")
                + "Candidate Electronic Mail Address: "
                + match.group("address")
                + "\n"
                + match.group("prefix")
                + "Candidate Telephone Number: "
                + telephone_number
            ),
            updated_text,
            flags=re.MULTILINE,
        )
        updated_text = re.sub(
            r"^\*\*Candidate electronic mail address:\*\* (?P<address>.*)$",
            lambda match: (
                "**Candidate electronic mail address:** "
                + match.group("address")
                + "\n**Candidate telephone number:** "
                + telephone_number
            ),
            updated_text,
            flags=re.MULTILINE,
        )

    if updated_text == original_text:
        return False

    path.write_text(updated_text, encoding="utf-8")
    return True


def main() -> int:
    """Parse the arguments and rewrite every header."""
    parser = argparse.ArgumentParser(
        description="Stamp candidate details into every file header."
    )
    parser.add_argument("--full-name", required=True)
    parser.add_argument("--email-address", required=True)
    parser.add_argument("--telephone-number", default="")
    arguments = parser.parse_args()

    changed_count = 0
    for path in collect_files():
        if path.name == "set_candidate_details.py":
            continue
        if rewrite_one_file(
            path,
            arguments.full_name,
            arguments.email_address,
            arguments.telephone_number,
        ):
            changed_count += 1

    print("Files updated: " + str(changed_count))
    print("")
    print("Regenerate the two generated deliverables so that they carry the")
    print("same details:")
    print("  python3 scripts/build_schema_mapping_workbook.py")
    print("  cd presentation && node build_presentation.js")
    return 0


if __name__ == "__main__":
    sys.exit(main())
