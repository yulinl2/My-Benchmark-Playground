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
| 2018 | `Applied_exam_2018.pdf` | ⬜ raw text only |
| 2019 | `Applied Exam 2019 packet/APPLIED_EXAM_2019_Jul25.pdf` (+ data) | ⬜ raw text only |
| 2020 | `Applied Exam 2020 packet/APPLIED_EXAM_2020.pdf` (+ data) | ⬜ raw text only |
| 2021 | `APPLIED_EXAM_2021.pdf` | ⬜ raw text only |
| 2022 | `APPLIED_EXAM_2022_final.pdf` | ⬜ raw text only |
| 2023 | `APPLIED_EXAM_2023_v2.pdf` | ⬜ raw text only |
| 2024 | `APPLIED_EXAM_2024_v2.pdf` | ⬜ raw text only |

### 2025 unified qualifying exam

| Component | Source PDF | Status |
| --------- | ---------- | ------ |
| Theory | `qe_2025_theory.pdf` | ✅ transcribed (6 problems, 4 parts) |
| Applied | `qe_2025_applied.pdf` | ⬜ raw text only |

> Note: the applied exams are packet-style (data-analysis prompts shipped with
> `.csv`/`.xlsx`/`.txt` datasets). They transcribe differently from the
> self-contained theory problems and may warrant a `data` field on their
> entries.

## Past MS exams

`Downloads/past-ms-exams-solution/` holds ~150 MS theory/applied exam and
solution PDFs spanning 1972–2025. These are a separate, larger transcription
effort and are **not yet started**.

## Notes on quality

- All transcribed entries currently have `verified: false`: the LaTeX was
  reconstructed from PyMuPDF text extraction and has **not** yet been checked
  line-by-line against the source PDFs. Set `verified: true` per entry after a
  human (or a careful visual PDF pass) confirms it.
- A couple of entries flag truncation/ambiguity in their `notes` field (e.g.
  `2022-summer-probability-q2` Part C) — resolve those against the PDF.
