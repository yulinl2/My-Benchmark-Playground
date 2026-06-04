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

1. **Get the PDFs.** Log into the Rutgers SharePoint repo and download the exam
   (and solution) PDFs. Drop them in `exams/pdfs/`.
2. **Scaffold an exam.** Run `python scripts/new_exam.py 2019 fall probability`
   to create a transcription stub and an empty question file.
3. **Transcribe.** Fill in the Markdown file in `exams/transcribed/` and the
   structured entries in `question_bank/questions/`. (I — Claude — can do the
   transcription for you once the PDFs are in the repo.)
4. **Build & validate.** Run `python scripts/build_bank.py`. It validates every
   question against `schema.json`, checks for duplicate IDs, and regenerates
   `question_bank/bank.jsonl` plus a topic/coverage summary.

No external dependencies — everything uses the Python 3 standard library.

## A note on copyright

These exams are Rutgers course materials. By default `exams/pdfs/` is
git-ignored so you don't redistribute the original PDFs. Keep this bank for
personal/study use and respect the department's terms.
