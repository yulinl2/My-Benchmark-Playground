#!/usr/bin/env python3
"""Apply exported audit decisions back into the question bank.

Reads an `audit-decisions.json` exported from audit/index.html and updates the
per-question files in question_bank/questions/*.json:
  - status "verified"  -> verified = true
  - status "fix"       -> verified = false  (kept flagged; see notes)
  - grading_type        -> set when provided
  - notes               -> merged idempotently under an "[audit]" marker

Then rebuilds bank.jsonl. Usage:

    python audit/apply_audit.py audit-decisions.json            # apply
    python audit/apply_audit.py audit-decisions.json --dry-run  # preview only
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QDIR = ROOT / "question_bank" / "questions"
MARK = "\n\n[audit] "


def merge_note(existing: str, audit: str) -> str:
    base = existing or ""
    if "\n\n[audit]" in base:
        base = base[: base.index("\n\n[audit]")].rstrip()
    audit = (audit or "").strip()
    return (base + (MARK + audit if audit else "")).strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("decisions", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    decisions = json.loads(args.decisions.read_text()).get("decisions", {})
    if not decisions:
        print("no decisions found in file"); return 1

    changed = 0
    for fp in sorted(QDIR.glob("*.json")):
        rows = json.loads(fp.read_text())
        dirty = False
        for q in rows:
            d = decisions.get(q["id"])
            if not d:
                continue
            before = json.dumps(q, sort_keys=True)
            if d.get("status") == "verified":
                q["verified"] = True
            elif d.get("status") == "fix":
                q["verified"] = False
            if d.get("ai_audit") in ("pass", "fix"):
                q["ai_audit"] = d["ai_audit"]
            if d.get("grading_type"):
                q["grading_type"] = d["grading_type"]
            if d.get("notes"):
                q["notes"] = merge_note(q.get("notes", ""), d["notes"])
            if json.dumps(q, sort_keys=True) != before:
                dirty = True; changed += 1
                print(f"  {'would update' if args.dry_run else 'updated'}: {q['id']}"
                      f" (ai_audit={q.get('ai_audit','—')}, grading_type={q.get('grading_type','—')})")
        if dirty and not args.dry_run:
            fp.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n")

    print(f"{'would change' if args.dry_run else 'changed'} {changed} question(s)")
    if changed and not args.dry_run:
        print("rebuilding bank…")
        subprocess.run([sys.executable, str(ROOT / "scripts" / "build_bank.py")], check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
