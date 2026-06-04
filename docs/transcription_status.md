# Transcription status

Tracks which Rutgers Statistics PhD qual exams have been transcribed from the
source PDFs (in `Downloads/past-PhD exams/`) into curated question entries
(`question_bank/questions/`). Raw extracted text for every exam lives in
`exams/transcribed/_raw/`.

Strands: **probability** and **statistical inference** are the in-class written
exams (`probability` / `math-stat`); **applied** is the take-home exam.

## PhD qualifying exams

### Probability (`part: probability`)

| Year | Source PDF | Status |
| ---- | ---------- | ------ |
| 2018 | `probability_exam_2018.pdf` | ✅ transcribed (2 problems) |
| 2019 | `probability_exam_2019.pdf` | ✅ transcribed (2 problems) |
| 2020 | `probability_exam_2020.pdf` | ✅ transcribed (2 problems) |
| 2021 | `probability_exam_2021.pdf` | ✅ transcribed (2 problems) |
| 2022 | `probability_exam_2022_final.pdf` | ✅ transcribed (2 problems) |
| 2023 | `probability_exam_2023_v3.pdf` | ✅ transcribed (6 exercises/problems) |
| 2024 | `probability_exam_2024_v1.pdf` | ✅ transcribed (4 problems) |

### Statistical inference (`part: math-stat`)

| Year | Source PDF | Status |
| ---- | ---------- | ------ |
| 2018 | `Inference_exam_2018.pdf` | ✅ transcribed (2 problems) |
| 2019 | `inference_exam_2019.pdf` | ✅ transcribed (2 problems) |
| 2020 | `inference_exam_2020.pdf` | ✅ transcribed (2 problems) |
| 2021 | `inference_exam_2021.pdf` | ✅ transcribed (2 problems) |
| 2022 | `inference_exam_2022_final.pdf` | ✅ transcribed (2 problems) |
| 2023 | `inference_exam_2023_v2.pdf` | ✅ transcribed (2 problems) |
| 2024 | `inference_exam_2024_v1.pdf` | ✅ transcribed (5 problems) |

### Applied take-home (`part: applied`)

| Year | Source PDF | Status |
| ---- | ---------- | ------ |
| 2018 | `Applied_exam_2018.pdf` | ✅ transcribed (2 problems) |
| 2019 | `Applied Exam 2019 packet/...Jul25.pdf` (+ data ✓) | ✅ transcribed (2 problems) |
| 2020 | `Applied Exam 2020 packet/...2020.pdf` (+ data ✓) | ✅ transcribed (2 problems) |
| 2021 | `APPLIED_EXAM_2021.pdf` | ✅ transcribed (3 problems) |
| 2022 | `APPLIED_EXAM_2022_final.pdf` | ✅ transcribed (3 problems) |
| 2023 | `APPLIED_EXAM_2023_v2.pdf` | ✅ transcribed (2 problems) |
| 2024 | `APPLIED_EXAM_2024_v2.pdf` | ✅ transcribed (2 problems) |

### 2025 unified qualifying exam

| Component | Source PDF | Status |
| --------- | ---------- | ------ |
| Theory | `qe_2025_theory.pdf` | ✅ transcribed (6 problems, 4 parts) |
| Applied | `qe_2025_applied.pdf` | ✅ transcribed (3 problems) |

> Note: the applied exams are packet-style (data-analysis prompts shipped with
> `.csv`/`.xlsx`/`.txt` datasets). They transcribe differently from the
> self-contained theory problems and may warrant a `data` field on their
> entries.

## Past MS exams

`Downloads/past-ms-exams-solution/` holds **161** MS theory/applied exam and
solution PDFs spanning 1972–2025. Raw text for every PDF with a text layer has
been extracted to `exams/transcribed/_raw_ms/`. The archive splits as:

- **111 PDFs have an extractable text layer** (machine-readable). However there
  is heavy duplication — the `ms<year>.<mm>.pXpa.pdf` files are the same exams as
  the named `T_*` (theory) and `A-*`/`Applied*` (applied) files, and several
  `*_Q & A.pdf` files repeat. The distinct readable MS exams number roughly ~45.
- **50 PDFs are fully scanned images** (0 extractable characters) — almost all
  the 1972–2009 exams plus a few solution scans. These require **OCR** (e.g. a
  visual PDF pass) before they can be transcribed.

**Status: recent Q&A exams transcribed (33 questions, with worked solutions).**
The six most recent comprehensive exams that ship with answer keys are in the
bank, tagged `exam.level: "ms"`:

| Exam | Source PDF | Status |
| ---- | ---------- | ------ |
| Fall 2019   | `Comprehensive Exam Fall 2019 Solutions.pdf` | ✅ 3 problems (1/2/4 are images — skipped) |
| Dec 2022    | `ms22Dec Q & A.pdf` | ✅ 6 problems + solutions |
| March 2023  | `ms23Mar Q & A.pdf` | ✅ 6 problems + solutions |
| Dec 2023    | `ms23Dec Q & A.pdf` | ✅ 6 problems + solutions |
| March 2024  | `ms24Mar Q & A.pdf` | ✅ 6 problems + solutions |
| Fall 2024   | `ms 24 Dec Q & A.pdf` | ✅ 6 problems + solutions |
| Spring 2025 | `MS Exam Spring 25 Q & A.pdf` | ⬜ scanned (no text layer) |
| March 2020  | `March 2020 MS Exam.pdf` | ⬜ no answer key; Q1–2 missing from scan |

Remaining MS backlog (not yet transcribed):
1. The older readable theory/applied papers (2008–2017, `ms<year>.<mm>.pXpa`
   and the `T_*`/`A-*` duplicates) — de-duplicate to ~40 distinct exams.
2. OCR the 50 fully-scanned exams (1972–2009 + a few solution scans).

The MS exams use a different format (separate Theory and Applied papers, often
with solutions). When transcribed they should set `part` to `math-stat` (theory)
or `applied`, and may use the `solution` field where the PDF includes answers.

## Notes on quality

- All transcribed entries currently have `verified: false`: the LaTeX was
  reconstructed from PyMuPDF text extraction and has **not** yet been checked
  line-by-line against the source PDFs. Set `verified: true` per entry after a
  human (or a careful visual PDF pass) confirms it.
- A couple of entries flag truncation/ambiguity in their `notes` field (e.g.
  `2022-summer-probability-q2` Part C) — resolve those against the PDF.
