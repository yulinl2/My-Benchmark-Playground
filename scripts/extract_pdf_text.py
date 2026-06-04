#!/usr/bin/env python3
"""Extract raw text from the Rutgers PhD qual exam PDFs.

Reads every PDF under ``Downloads/past-PhD exams/`` and writes a faithful
plain-text dump (Unicode math preserved) to ``exams/transcribed/_raw/``.
These raw dumps are the source material for the curated question entries in
``question_bank/questions/`` and are committed so the transcription is
reproducible and auditable.

Requires PyMuPDF (``pip install pymupdf``). Usage:

    python scripts/extract_pdf_text.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "Downloads" / "past-PhD exams"
OUT = ROOT / "exams" / "transcribed" / "_raw"


def main() -> int:
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("error: PyMuPDF not installed. Run: pip install pymupdf", file=sys.stderr)
        return 1

    if not SRC.exists():
        print(f"error: {SRC.relative_to(ROOT)} not found.", file=sys.stderr)
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    pdfs = sorted(SRC.rglob("*.pdf"))
    if not pdfs:
        print(f"No PDFs found under {SRC.relative_to(ROOT)}/.")
        return 0

    for pdf in pdfs:
        doc = fitz.open(pdf)
        chunks = []
        for i, page in enumerate(doc):
            chunks.append(f"\n----- page {i + 1} -----\n{page.get_text()}")
        doc.close()
        out_path = OUT / (pdf.stem + ".txt")
        out_path.write_text("".join(chunks), encoding="utf-8")
        print(f"{pdf.stem}: {len(chunks)} page(s) -> {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
