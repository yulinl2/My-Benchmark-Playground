# audit — human review interface for the question bank

A self-contained interface to review each transcribed question against its
source PDF, mark it **verified** / **needs-fix**, classify its **grading type**,
and record corrections — the gate before the quals can be contributed.

## Use it

```bash
python audit/build_audit.py     # bank.jsonl -> audit/data.js
```

Then open `audit/index.html` in a browser (works from `file://` — no server).
For each question you see the rendered prompt + parts, the official solution
(MS only), and a link to the **source PDF + page** to check against.

- Mark **✓ verified / ✗ needs-fix** (keys <kbd>v</kbd> / <kbd>x</kbd>), pick a
  **grading type** (exact-match · numeric · proof-rubric · data-analysis), and
  type **notes/corrections**.
- Navigate with <kbd>j</kbd>/<kbd>k</kbd>; filter by status / level / part / id.
- Progress is saved to your browser's `localStorage` as you go.
- Click **Export decisions** to download `audit-decisions.json`.

## Apply decisions back to the bank

```bash
python audit/apply_audit.py audit-decisions.json --dry-run   # preview
python audit/apply_audit.py audit-decisions.json             # apply + rebuild
```

This sets `verified`, `grading_type`, and merges your notes (idempotently, under
an `[audit]` marker) into `question_bank/questions/*.json`, then rebuilds
`bank.jsonl`.

## Loop

`build_audit.py` → review in `index.html` → **Export** → `apply_audit.py` →
commit. Re-run `build_audit.py` after any bank change to refresh the interface.

Math renders via KaTeX from a CDN (needs internet in the browser). `data.js` is
generated and git-ignored; the bank is the source of truth.
