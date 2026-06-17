#!/usr/bin/env python3
"""Collection harness: run models over the question bank and save full
responses + reasoning trajectories, with per-call cost.

Collection only — no grading (that's a separate concern; see harness/README.md).
Supports both providers:
  - Anthropic (claude-*): extended thinking via `thinking.budget_tokens`.
  - OpenAI   (gpt-*):      reasoning via the Responses API `reasoning.effort`.

Pure standard library (urllib). Reads ANTHROPIC_API_KEY / ANTHROPIC_BASE_URL and
OPENAI_API_KEY / OPENAI_BASE_URL.

Examples
--------
    python harness/run_models.py --dry-run --limit 3
    python harness/run_models.py --models claude-haiku-4-5-20251001
    python harness/run_models.py --models gpt-5.5 --reasoning-effort high
    python harness/run_models.py --models claude-opus-4-7,gpt-5.5 \
        --ids 2019-summer-probability-q1 --thinking-budget 12000 --max-tokens 20000
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
ANTHROPIC_VERSION = "2023-06-01"

SYSTEM_PROMPT = (
    "You are sitting a PhD-level qualifying examination in statistics. "
    "Solve the problem rigorously and completely. Show your work and reasoning, "
    "justify each step, and clearly state your final answer(s). If the problem has "
    "multiple parts, answer every part, labeled. If you invoke a known theorem, name it."
)

# (input $/M, output $/M). Output covers reasoning/thinking tokens (billed as output).
# GPT-5.5 is a placeholder price per the reference; verify before trusting costs.
PRICES = {
    "claude-opus-4-8": (15, 75), "claude-opus-4-7": (15, 75), "claude-opus-4-6": (15, 75),
    "claude-sonnet-4-6": (3, 15),
    "claude-haiku-4-5": (1, 5), "claude-haiku-4-5-20251001": (1, 5),
    "gpt-5.5": (5, 15),
}

# One --effort knob drives all three thinking APIs:
#   GPT-5.x        -> reasoning.effort
#   Opus/Sonnet    -> thinking.type=adaptive + output_config.effort
#   Haiku (no adaptive support) -> thinking.type=enabled + budget_tokens (mapped)
EFFORT_BUDGET = {"minimal": 0, "low": 4000, "medium": 8000, "high": 12000}


def claude_supports_adaptive(model: str) -> bool:
    return ("opus" in model) or ("sonnet" in model)


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def provider_of(model: str) -> str:
    return "openai" if model.startswith(("gpt", "o1", "o3", "o4")) else "anthropic"


def price_cost(model: str, usage: dict):
    p = PRICES.get(model)
    if not p or p[0] is None:
        return None
    it = usage.get("input_tokens", 0) or 0
    ot = usage.get("output_tokens", 0) or 0
    return round(it / 1e6 * p[0] + ot / 1e6 * p[1], 5)


def build_user_prompt(q: dict) -> str:
    lines: list[str] = []
    ex = q.get("exam", {})
    tag = f"{ex.get('year','?')} {ex.get('term','')} {ex.get('level','phd')} {ex.get('part','')}".strip()
    lines.append(f"[{tag} — problem {q.get('number','?')}]")
    lines.append("")
    lines.append(q["prompt"].strip())
    for p in (q.get("parts") or []):
        lines.append(str(p).strip())
    data = q.get("data") or []
    if data:
        lines.append("")
        lines.append("Note: this problem references dataset file(s) NOT provided: "
                     + "; ".join(data) + ". Describe the analysis you would perform.")
    return "\n".join(lines)


# --------------------------------------------------------------- providers ----
def call_anthropic(model, system, user, max_tokens, effort, timeout) -> dict:
    base = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com").rstrip("/")
    key = os.environ["ANTHROPIC_API_KEY"]
    body = {"model": model, "max_tokens": max_tokens, "system": system,
            "messages": [{"role": "user", "content": user}]}
    if claude_supports_adaptive(model):
        body["thinking"] = {"type": "adaptive"}
        body["output_config"] = {"effort": effort}
    else:  # haiku etc.: legacy budgeted thinking
        budget = EFFORT_BUDGET.get(effort, 8000)
        if budget > 0:
            body["thinking"] = {"type": "enabled", "budget_tokens": budget}
    req = urllib.request.Request(
        f"{base}/v1/messages", data=json.dumps(body).encode(),
        headers={"content-type": "application/json", "x-api-key": key,
                 "anthropic-version": ANTHROPIC_VERSION}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        resp = json.loads(r.read().decode())
    thinking, text = [], []
    for b in resp.get("content", []):
        if b.get("type") == "thinking":
            thinking.append(b.get("thinking", ""))
        elif b.get("type") == "redacted_thinking":
            thinking.append("[redacted_thinking]")
        elif b.get("type") == "text":
            text.append(b.get("text", ""))
    return {"id": resp.get("id"), "model": resp.get("model"),
            "stop_reason": resp.get("stop_reason"), "usage": resp.get("usage", {}),
            "thinking": "\n".join(thinking), "text": "\n".join(text),
            "raw_output": resp.get("content", [])}


def call_openai(model, system, user, max_tokens, effort, timeout) -> dict:
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    key = os.environ["OPENAI_API_KEY"]
    body = {"model": model, "instructions": system, "input": user,
            "max_output_tokens": max_tokens}
    if effort:
        body["reasoning"] = {"effort": effort, "summary": "auto"}
    req = urllib.request.Request(
        f"{base}/responses", data=json.dumps(body).encode(),
        headers={"content-type": "application/json",
                 "authorization": f"Bearer {key}"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        resp = json.loads(r.read().decode())
    thinking, text = [], []
    for item in resp.get("output", []):
        if item.get("type") == "reasoning":
            for s in item.get("summary", []) or []:
                thinking.append(s.get("text", ""))
        elif item.get("type") == "message":
            for c in item.get("content", []) or []:
                if c.get("type") == "output_text":
                    text.append(c.get("text", ""))
    u = resp.get("usage", {}) or {}
    usage = {"input_tokens": u.get("input_tokens"), "output_tokens": u.get("output_tokens"),
             "output_tokens_details": u.get("output_tokens_details")}
    return {"id": resp.get("id"), "model": resp.get("model"),
            "stop_reason": resp.get("status"), "usage": usage,
            "thinking": "\n".join(thinking), "text": "\n".join(text),
            "raw_output": resp.get("output", [])}


def run_one(q, model, rep, args, out_dir, lock) -> dict:
    qid = q["id"]
    prov = provider_of(model)
    suffix = f"__r{rep}" if args.k > 1 else ""
    dest = out_dir / model.replace("/", "_") / f"{qid}{suffix}.json"
    if dest.exists() and not args.overwrite:
        return {"qid": qid, "model": model, "status": "skipped"}

    user = build_user_prompt(q)
    mode = {"effort": args.effort}
    record = {"question_id": qid, "model": model, "provider": prov, "rep": rep,
              "exam": q.get("exam"),
              "request": {"system": SYSTEM_PROMPT, "user": user,
                          "max_tokens": args.max_tokens, "mode": mode},
              "response": None, "cost_usd": None,
              "timing": {"started": iso_now()}, "error": None}

    if args.dry_run:
        record["response"] = {"note": "dry-run"}
        record["timing"]["ended"] = iso_now()
        _write(dest, record, out_dir, lock)
        return {"qid": qid, "model": model, "status": "dry-run"}

    t0, last_err = time.time(), None
    for attempt in range(args.retries + 1):
        try:
            if prov == "anthropic":
                out = call_anthropic(model, SYSTEM_PROMPT, user, args.max_tokens,
                                     args.effort, args.timeout)
            else:
                out = call_openai(model, SYSTEM_PROMPT, user, args.max_tokens,
                                  args.effort, args.timeout)
            record["response"] = out
            record["cost_usd"] = price_cost(model, out.get("usage", {}))
            break
        except urllib.error.HTTPError as e:
            last_err = f"HTTP {e.code}: {e.read().decode('utf-8','replace')[:400]}"
            if e.code in (429, 500, 502, 503, 529) and attempt < args.retries:
                time.sleep(2 ** attempt); continue
            break
        except Exception as e:  # noqa: BLE001
            last_err = f"{type(e).__name__}: {e}"
            if attempt < args.retries:
                time.sleep(2 ** attempt); continue
            break

    record["timing"]["ended"] = iso_now()
    record["timing"]["seconds"] = round(time.time() - t0, 2)
    if record["response"] is None:
        record["error"] = last_err
    _write(dest, record, out_dir, lock)
    return {"qid": qid, "model": model,
            "status": "ok" if record["error"] is None else "error",
            "error": record["error"], "seconds": record["timing"].get("seconds"),
            "cost": record["cost_usd"]}


def _write(dest, record, out_dir, lock):
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    with lock:
        with (out_dir / "results.jsonl").open("a") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_bank(path): return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def filter_bank(rows, args):
    out, ids = [], (set(args.ids.split(",")) if args.ids else None)
    for r in rows:
        ex = r.get("exam", {})
        if ids and r["id"] not in ids: continue
        if args.filter_level and ex.get("level", "phd") != args.filter_level: continue
        if args.filter_part and ex.get("part") != args.filter_part: continue
        if args.filter_year and str(ex.get("year")) != str(args.filter_year): continue
        if args.skip_data and r.get("data"): continue
        out.append(r)
    return out[: args.limit] if args.limit else out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--models", default="claude-sonnet-4-6")
    ap.add_argument("--bank", type=Path, default=DEFAULT_BANK)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--k", type=int, default=1, help="repetitions per (model,question) for pass@k / 0-of-k")
    ap.add_argument("--max-tokens", type=int, default=16000)
    ap.add_argument("--effort", choices=["minimal", "low", "medium", "high"], default="high",
                    help="unified reasoning effort across providers (GPT reasoning.effort; "
                         "Opus/Sonnet adaptive output_config.effort; Haiku mapped to a thinking budget)")
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--retries", type=int, default=3)
    ap.add_argument("--filter-level", choices=["phd", "ms"])
    ap.add_argument("--filter-part")
    ap.add_argument("--filter-year")
    ap.add_argument("--ids")
    ap.add_argument("--skip-data", action="store_true", help="exclude dataset-dependent problems")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    rows = filter_bank(load_bank(args.bank), args)
    models = [m.strip() for m in args.models.split(",") if m.strip()]
    run_id = args.run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = args.out / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "manifest.json").write_text(json.dumps({
        "run_id": run_id, "created": iso_now(), "models": models, "n_questions": len(rows),
        "max_tokens": args.max_tokens, "effort": args.effort, "k": args.k, "dry_run": args.dry_run,
        "question_ids": [r["id"] for r in rows]}, indent=2) + "\n")

    tasks = [(q, m, rep) for m in models for q in rows for rep in range(args.k)]
    print(f"run {run_id}: {len(rows)} q x {len(models)} model(s) x k={args.k} = {len(tasks)} call(s) -> {out_dir}", flush=True)
    lock = threading.Lock()
    counts, total_cost = {"ok": 0, "error": 0, "skipped": 0, "dry-run": 0}, 0.0
    with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        for fut in as_completed([ex.submit(run_one, q, m, rep, args, out_dir, lock) for q, m, rep in tasks]):
            r = fut.result()
            counts[r["status"]] = counts.get(r["status"], 0) + 1
            if r.get("cost"): total_cost += r["cost"]
            done = sum(counts.values())
            extra = f" ${r['cost']:.3f}" if r.get("cost") else ""
            extra += f" ({r['error']})" if r.get("error") else ""
            print(f"[{done}/{len(tasks)}] {r['status']:7} {r['model']} {r['qid']}"
                  f"{(' %.0fs' % r['seconds']) if r.get('seconds') else ''}{extra}", flush=True)
    counts["total_cost_usd"] = round(total_cost, 4)
    print(f"done: {counts}", flush=True)
    (out_dir / "summary.json").write_text(json.dumps(counts, indent=2) + "\n")
    return 1 if counts.get("error") else 0


if __name__ == "__main__":
    sys.exit(main())
