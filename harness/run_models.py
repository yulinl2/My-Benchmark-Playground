#!/usr/bin/env python3
"""Collection harness: run models over the question bank and save full
responses + reasoning trajectories.

This harness ONLY collects model outputs. It does not grade them — grading and
the eval are deliberately separate (see harness/README.md). For each
(model, question) it captures the final answer text, the extended-thinking
trajectory, token usage, stop reason, and timing.

Pure standard library (urllib). Respects ANTHROPIC_API_KEY and ANTHROPIC_BASE_URL.

Examples
--------
    # Smoke test: one cheap model, 1 question, see it work
    python harness/run_models.py --models claude-haiku-4-5-20251001 --limit 1

    # Full background collection for one model (resumable)
    python harness/run_models.py --models claude-sonnet-4-6

    # Multiple models, only the probability questions
    python harness/run_models.py --models claude-sonnet-4-6,claude-opus-4-8 --filter-part probability

    # Build prompts without calling the API (no key needed)
    python harness/run_models.py --dry-run --limit 3
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import threading
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BANK = ROOT / "question_bank" / "bank.jsonl"
DEFAULT_OUT = ROOT / "harness" / "runs"
API_VERSION = "2023-06-01"

SYSTEM_PROMPT = (
    "You are sitting a PhD-level qualifying examination in statistics. "
    "Solve the problem rigorously and completely. Show your work and reasoning, "
    "justify each step, and clearly state your final answer(s). If the problem has "
    "multiple parts, answer every part, labeled. If you invoke a known theorem, name it."
)


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_user_prompt(q: dict) -> str:
    """Render a bank question into a single self-contained prompt string."""
    lines: list[str] = []
    ex = q.get("exam", {})
    tag = f"{ex.get('year','?')} {ex.get('term','')} {ex.get('level','phd')} {ex.get('part','')}".strip()
    lines.append(f"[{tag} — problem {q.get('number','?')}]")
    lines.append("")
    lines.append(q["prompt"].strip())
    parts = q.get("parts") or []
    if parts:
        lines.append("")
        for p in parts:
            lines.append(str(p).strip())
    data = q.get("data") or []
    if data:
        lines.append("")
        lines.append(
            "Note: this problem references dataset file(s) that are NOT provided to you: "
            + "; ".join(data)
            + ". Describe the analysis you would perform and the expected form of the results."
        )
    return "\n".join(lines)


def call_anthropic(model: str, system: str, user: str, max_tokens: int,
                   thinking_budget: int, timeout: int) -> dict:
    """One non-streaming Messages API call. Returns the parsed JSON response."""
    base = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com").rstrip("/")
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set.")
    body: dict = {
        "model": model,
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }
    if thinking_budget and thinking_budget > 0:
        body["thinking"] = {"type": "enabled", "budget_tokens": thinking_budget}
        # extended thinking requires the default temperature; do not set one.
    req = urllib.request.Request(
        f"{base}/v1/messages",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "x-api-key": key,
            "anthropic-version": API_VERSION,
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def split_content(resp: dict) -> tuple[str, str, list]:
    """Pull (thinking trajectory, answer text, raw blocks) out of a response."""
    thinking_parts, text_parts = [], []
    blocks = resp.get("content", []) or []
    for b in blocks:
        t = b.get("type")
        if t == "thinking":
            thinking_parts.append(b.get("thinking", ""))
        elif t == "redacted_thinking":
            thinking_parts.append("[redacted_thinking]")
        elif t == "text":
            text_parts.append(b.get("text", ""))
    return "\n".join(thinking_parts), "\n".join(text_parts), blocks


def run_one(q: dict, model: str, args, out_dir: Path, lock: threading.Lock) -> dict:
    qid = q["id"]
    dest = out_dir / model.replace("/", "_") / f"{qid}.json"
    if dest.exists() and not args.overwrite:
        return {"qid": qid, "model": model, "status": "skipped"}

    user = build_user_prompt(q)
    record = {
        "question_id": qid,
        "model": model,
        "exam": q.get("exam"),
        "request": {
            "system": SYSTEM_PROMPT,
            "user": user,
            "max_tokens": args.max_tokens,
            "thinking_budget": args.thinking_budget,
        },
        "response": None,
        "timing": {"started": iso_now()},
        "error": None,
    }
    if args.dry_run:
        record["response"] = {"note": "dry-run; no API call made"}
        record["timing"]["ended"] = iso_now()
        _write(dest, record, out_dir, lock)
        return {"qid": qid, "model": model, "status": "dry-run"}

    t0 = time.time()
    last_err = None
    for attempt in range(args.retries + 1):
        try:
            resp = call_anthropic(model, SYSTEM_PROMPT, user, args.max_tokens,
                                  args.thinking_budget, args.timeout)
            thinking, text, blocks = split_content(resp)
            record["response"] = {
                "id": resp.get("id"),
                "model": resp.get("model"),
                "stop_reason": resp.get("stop_reason"),
                "usage": resp.get("usage"),
                "thinking": thinking,   # the trajectory
                "text": text,           # the final answer
                "content_blocks": blocks,
            }
            break
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:500]
            last_err = f"HTTP {e.code}: {detail}"
            if e.code in (429, 500, 503, 529) and attempt < args.retries:
                time.sleep(2 ** attempt)
                continue
            break
        except Exception as e:  # noqa: BLE001 - record any failure, keep going
            last_err = f"{type(e).__name__}: {e}"
            if attempt < args.retries:
                time.sleep(2 ** attempt)
                continue
            break

    record["timing"]["ended"] = iso_now()
    record["timing"]["seconds"] = round(time.time() - t0, 2)
    if record["response"] is None:
        record["error"] = last_err
    _write(dest, record, out_dir, lock)
    status = "ok" if record["error"] is None else "error"
    return {"qid": qid, "model": model, "status": status, "error": record["error"],
            "seconds": record["timing"].get("seconds")}


def _write(dest: Path, record: dict, out_dir: Path, lock: threading.Lock) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    with lock:
        with (out_dir / "results.jsonl").open("a") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_bank(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def filter_bank(rows: list[dict], args) -> list[dict]:
    out = []
    ids = set(args.ids.split(",")) if args.ids else None
    for r in rows:
        ex = r.get("exam", {})
        if ids and r["id"] not in ids:
            continue
        if args.filter_level and ex.get("level", "phd") != args.filter_level:
            continue
        if args.filter_part and ex.get("part") != args.filter_part:
            continue
        if args.filter_year and str(ex.get("year")) != str(args.filter_year):
            continue
        out.append(r)
    if args.limit:
        out = out[: args.limit]
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--models", default="claude-sonnet-4-6",
                    help="comma-separated model ids")
    ap.add_argument("--bank", type=Path, default=DEFAULT_BANK)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--run-id", default=None,
                    help="subdir under --out (default: timestamp)")
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--max-tokens", type=int, default=16000)
    ap.add_argument("--thinking-budget", type=int, default=8000,
                    help="extended-thinking budget; 0 disables thinking")
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--retries", type=int, default=3)
    ap.add_argument("--filter-level", choices=["phd", "ms"])
    ap.add_argument("--filter-part")
    ap.add_argument("--filter-year")
    ap.add_argument("--ids", help="comma-separated question ids")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--overwrite", action="store_true",
                    help="re-run even if an output file exists")
    ap.add_argument("--dry-run", action="store_true",
                    help="build prompts and write stubs; no API calls")
    args = ap.parse_args()

    rows = filter_bank(load_bank(args.bank), args)
    models = [m.strip() for m in args.models.split(",") if m.strip()]
    run_id = args.run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = args.out / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "run_id": run_id, "created": iso_now(), "models": models,
        "n_questions": len(rows), "bank": str(args.bank),
        "max_tokens": args.max_tokens, "thinking_budget": args.thinking_budget,
        "dry_run": args.dry_run,
        "question_ids": [r["id"] for r in rows],
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    tasks = [(q, m) for m in models for q in rows]
    print(f"run {run_id}: {len(rows)} question(s) x {len(models)} model(s) = "
          f"{len(tasks)} call(s) -> {out_dir}", flush=True)

    lock = threading.Lock()
    counts = {"ok": 0, "error": 0, "skipped": 0, "dry-run": 0}
    with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        futs = [ex.submit(run_one, q, m, args, out_dir, lock) for q, m in tasks]
        for fut in as_completed(futs):
            r = fut.result()
            counts[r["status"]] = counts.get(r["status"], 0) + 1
            done = sum(counts.values())
            extra = f" ({r['error']})" if r.get("error") else ""
            print(f"[{done}/{len(tasks)}] {r['status']:7} {r['model']} {r['qid']}"
                  f"{(' %.0fs' % r['seconds']) if r.get('seconds') else ''}{extra}",
                  flush=True)

    print(f"done: {counts}", flush=True)
    (out_dir / "summary.json").write_text(json.dumps(counts, indent=2) + "\n")
    return 1 if counts.get("error") else 0


if __name__ == "__main__":
    sys.exit(main())
