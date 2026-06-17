#!/usr/bin/env python3
"""Scaffold a transcription stub + empty question file for one exam.

Usage:
    python scripts/new_exam.py <year> <term> <part>

Example:
    python scripts/new_exam.py 2019 fall probability

Creates (without overwriting existing files):
    exams/transcribed/2019_fall_probability.md
    question_bank/questions/2019_fall_probability.json   (an empty JSON array)

Pure standard library.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "exams" / "transcribed" / "TEMPLATE.md"

VALID_TERMS = {"spring", "summer", "fall", "winter", "unknown"}
VALID_PARTS = {"probability", "math-stat", "applied", "other"}


def main() -> int:
    if len(sys.argv) != 4:
        print(__doc__)
        return 2
    year, term, part = sys.argv[1], sys.argv[2].lower(), sys.argv[3].lower()

    if not (year.isdigit() and 1990 <= int(year) <= 2100):
        print(f"error: year '{year}' should be a 4-digit year (1990-2100)")
        return 2
    if term not in VALID_TERMS:
        print(f"error: term '{term}' must be one of {sorted(VALID_TERMS)}")
        return 2
    if part not in VALID_PARTS:
        print(f"error: part '{part}' must be one of {sorted(VALID_PARTS)}")
        return 2

    slug = f"{year}_{term}_{part}"
    md_path = ROOT / "exams" / "transcribed" / f"{slug}.md"
    json_path = ROOT / "question_bank" / "questions" / f"{slug}.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)

    created = []
    if md_path.exists():
        print(f"skip (exists): {md_path.relative_to(ROOT)}")
    else:
        body = TEMPLATE.read_text()
        body = (body.replace("{YEAR}", year)
                    .replace("{TERM}", term)
                    .replace("{PART}", part))
        md_path.write_text(body)
        created.append(md_path)

    if json_path.exists():
        print(f"skip (exists): {json_path.relative_to(ROOT)}")
    else:
        json_path.write_text("[]\n")
        created.append(json_path)

    for p in created:
        print(f"created: {p.relative_to(ROOT)}")
    if created:
        print(f"\nNext: transcribe the PDF into the two files above, then run "
              f"`python scripts/build_bank.py`.\n"
              f"Id convention for entries in {json_path.name}: "
              f"{year}-{term}-{part}-q<number>")
    return 0


if __name__ == "__main__":
    sys.exit(main())
