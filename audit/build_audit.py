#!/usr/bin/env python3
"""Generate audit/data.js from question_bank/bank.jsonl.

Embeds the bank as a JS global so audit/index.html works straight from the
filesystem (file://) with no server / no CORS. Re-run whenever the bank changes:

    python audit/build_audit.py
"""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BANK = ROOT / "question_bank" / "bank.jsonl"
OUT = ROOT / "audit" / "data.js"


def main() -> int:
    rows = [json.loads(l) for l in BANK.read_text().splitlines() if l.strip()]
    for q in rows:
        pdf = (q.get("source") or {}).get("pdf")
        # index.html lives in audit/, PDFs are repo-relative -> prefix with ../
        q["pdf_href"] = ("../" + pdf) if pdf else None
    payload = {
        "built": datetime.now(timezone.utc).isoformat(),
        "count": len(rows),
        "questions": rows,
    }
    OUT.write_text("window.BANK = " + json.dumps(payload, ensure_ascii=False) + ";\n")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(rows)} questions)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
