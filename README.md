# Rutgers Statistics PhD Qual — Question Bank

A curated, searchable question bank built from the **Rutgers Statistics
department's PhD qualifying exams**. This repo turns past exam PDFs into
structured, machine-readable question entries you can browse, filter by topic,
and study from.

## Why this repo exists

The Rutgers Statistics PhD qualifying exam is taken before the second year and
has two parts:

1. an **in-class written exam** on **mathematical statistics & probability theory**, and
2. a **take-home exam** on **applied statistics**.

The department's past exams and solutions are hosted on an **authenticated
Rutgers SharePoint** site (`rutgersconnect.sharepoint.com/sites/stat-ms_phd_past_exams`),
which means they **cannot be auto-scraped** — they require a Rutgers NetID
login. The workflow below is built around that reality: you supply the PDFs,
and the tooling here helps you transcribe and curate them into a question bank.

See [`docs/qual_format.md`](docs/qual_format.md) for everything publicly known
about the exam's structure and topics.

## Repository layout

```
.
├── exams/
│   ├── pdfs/            # drop raw exam/solution PDFs here (git-ignored by default)
│   └── transcribed/     # human-readable Markdown transcriptions, one file per exam
├── question_bank/
│   ├── schema.json      # JSON Schema for a single question entry
│   ├── questions/       # curated questions, one JSON file per exam (the source of truth)
│   └── bank.jsonl       # generated: all questions concatenated (do not edit by hand)
├── scripts/
│   ├── new_exam.py      # scaffold a transcription + question file for a new exam
│   └── build_bank.py    # validate question files and (re)build bank.jsonl + stats
└── docs/
    └── qual_format.md   # public info on exam format, topics, study notes
```

## Workflow

The source PDFs (downloaded from the Rutgers SharePoint) live in
`Downloads/past-PhD exams/` and `Downloads/past-ms-exams-solution/`.

1. **Extract text.** `pip install pymupdf`, then run
   `python scripts/extract_pdf_text.py`. This writes a faithful Unicode text
   dump of every PhD exam to `exams/transcribed/_raw/` (committed, so the
   transcription is auditable).
2. **Transcribe into structured entries.** Convert each problem into a question
   object in `question_bank/questions/<year>_<term>_<part>.json` (LaTeX in the
   `prompt`/`parts` fields). See `docs/transcription_status.md` for what's done
   and what's pending.
3. **Build & validate.** Run `python scripts/build_bank.py`. It validates every
   question against `schema.json`, checks for duplicate IDs, and regenerates
   `question_bank/bank.jsonl` plus a topic/coverage summary.

`scripts/new_exam.py <year> <term> <part>` scaffolds an empty transcription +
question file if you'd rather start from a template.

The three exam strands map to the `part` field as: **probability** →
`probability`, **statistical inference** → `math-stat`, **applied (take-home)**
→ `applied`.

Only `extract_pdf_text.py` needs a dependency (PyMuPDF); everything else uses the
Python 3 standard library.

## A note on copyright

These exams are Rutgers course materials. By default `exams/pdfs/` is
git-ignored so you don't redistribute the original PDFs. Keep this bank for
personal/study use and respect the department's terms.
