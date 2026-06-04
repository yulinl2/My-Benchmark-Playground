#!/usr/bin/env python3
"""Validate curated question files and (re)build the question bank.

Reads every ``question_bank/questions/*.json`` file (each a JSON array of
question objects), validates each entry against ``question_bank/schema.json``,
checks that ids are unique, then writes ``question_bank/bank.jsonl`` (one
question per line) and prints a coverage summary.

Files whose names start with ``_`` (e.g. ``_example.json``) are treated as
illustrative samples: they are validated but excluded from ``bank.jsonl``.

Pure standard library. Usage:

    python scripts/build_bank.py            # build + summary
    python scripts/build_bank.py --check    # validate only, no write (CI-friendly)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_DIR = ROOT / "question_bank" / "questions"
SCHEMA_PATH = ROOT / "question_bank" / "schema.json"
BANK_PATH = ROOT / "question_bank" / "bank.jsonl"


# --------------------------------------------------------------------------- #
# Minimal JSON-Schema validator (covers the subset used by schema.json).
# --------------------------------------------------------------------------- #
def _type_ok(value, types) -> bool:
    if isinstance(types, str):
        types = [types]
    mapping = {
        "object": dict,
        "array": list,
        "string": str,
        "integer": int,
        "number": (int, float),
        "boolean": bool,
        "null": type(None),
    }
    for t in types:
        if t == "null" and value is None:
            return True
        if t == "integer" and isinstance(value, bool):
            return False  # bool is a subclass of int; don't count it
        py = mapping.get(t)
        if py and isinstance(value, py) and not (t != "boolean" and isinstance(value, bool)):
            return True
    return False


def validate(value, schema, path, errors):
    if "type" in schema and not _type_ok(value, schema["type"]):
        errors.append(f"{path}: expected type {schema['type']}, got {type(value).__name__}")
        return  # further checks unreliable once the type is wrong

    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} not in allowed values {schema['enum']}")

    if isinstance(value, str):
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(f"{path}: {value!r} does not match pattern {schema['pattern']}")
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append(f"{path}: string shorter than minLength {schema['minLength']}")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: {value} < minimum {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path}: {value} > maximum {schema['maximum']}")

    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"{path}: array has fewer than minItems {schema['minItems']}")
        if "items" in schema:
            for i, item in enumerate(value):
                validate(item, schema["items"], f"{path}[{i}]", errors)

    if isinstance(value, dict):
        props = schema.get("properties", {})
        for req in schema.get("required", []):
            if req not in value:
                errors.append(f"{path}: missing required property '{req}'")
        if schema.get("additionalProperties") is False:
            for key in value:
                if key not in props:
                    errors.append(f"{path}: unexpected property '{key}'")
        for key, subschema in props.items():
            if key in value:
                validate(value[key], subschema, f"{path}.{key}", errors)


# --------------------------------------------------------------------------- #
def load_question_files():
    if not QUESTIONS_DIR.exists():
        return []
    return sorted(QUESTIONS_DIR.glob("*.json"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate only; do not write bank.jsonl")
    args = parser.parse_args()

    schema = json.loads(SCHEMA_PATH.read_text())
    files = load_question_files()
    if not files:
        print(f"No question files found in {QUESTIONS_DIR.relative_to(ROOT)}/ yet.")
        print("Add the PDFs to exams/pdfs/ and run scripts/new_exam.py to get started.")
        return 0

    errors: list[str] = []
    ids: dict[str, str] = {}
    bank: list[dict] = []
    sample_count = 0

    for fp in files:
        is_sample = fp.name.startswith("_")
        try:
            data = json.loads(fp.read_text())
        except json.JSONDecodeError as exc:
            errors.append(f"{fp.name}: invalid JSON ({exc})")
            continue
        if not isinstance(data, list):
            errors.append(f"{fp.name}: top-level value must be a JSON array of questions")
            continue
        for i, q in enumerate(data):
            loc = f"{fp.name}[{i}]"
            validate(q, schema, loc, errors)
            qid = q.get("id") if isinstance(q, dict) else None
            if qid:
                if qid in ids:
                    errors.append(f"{loc}: duplicate id '{qid}' (also in {ids[qid]})")
                else:
                    ids[qid] = fp.name
            if is_sample:
                sample_count += 1
            else:
                bank.append(q)

    if errors:
        print(f"✗ Validation failed with {len(errors)} error(s):\n")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"✓ Validated {len(ids)} question(s) across {len(files)} file(s) "
          f"({sample_count} sample, {len(bank)} curated).")

    if not args.check:
        bank.sort(key=lambda q: q["id"])
        with BANK_PATH.open("w") as fh:
            for q in bank:
                fh.write(json.dumps(q, ensure_ascii=False) + "\n")
        print(f"✓ Wrote {len(bank)} question(s) to {BANK_PATH.relative_to(ROOT)}")

    # Coverage summary (curated questions only).
    if bank:
        by_level = Counter(q["exam"].get("level", "phd") for q in bank)
        by_part = Counter(q["exam"]["part"] for q in bank)
        by_year = Counter(q["exam"]["year"] for q in bank)
        topics = Counter(t for q in bank for t in q["topics"])
        verified = sum(1 for q in bank if q.get("verified"))
        print("\nCoverage")
        print("--------")
        print("  by level: " + ", ".join(f"{k}={v}" for k, v in sorted(by_level.items())))
        print("  by part:  " + ", ".join(f"{k}={v}" for k, v in sorted(by_part.items())))
        print("  by year:  " + ", ".join(f"{k}={v}" for k, v in sorted(by_year.items())))
        print(f"  verified: {verified}/{len(bank)}")
        print("  top topics: " + ", ".join(f"{k}({v})" for k, v in topics.most_common(10)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
