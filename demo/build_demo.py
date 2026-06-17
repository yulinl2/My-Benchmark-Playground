#!/usr/bin/env python3
"""Build demo/data.js for the interactive results explorer.

Pools, per screened problem: the bank statement, the behavioral signals + scores
(analysis.json / analysis_theory.json), and every model response (GPT-5.5 + Haiku,
k=3) with its trajectory + tokens + cost. Embeds as a JS global so demo/index.html
runs from file:// with no server.

    python demo/build_demo.py --run harness/runs/screen-v1
"""
import argparse, json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GPT, HAIKU = "gpt-5.5", "claude-haiku-4-5-20251001"
THINK_CAP, TEXT_CAP = 5000, 9000


def cap(s, n):
    s = s or ""
    return s if len(s) <= n else s[:n] + f"\n\n…[truncated {len(s)-n} chars]"


def reason_tok(u):
    d = (u or {}).get("output_tokens_details") or {}
    return d.get("thinking_tokens") or d.get("reasoning_tokens") or 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", type=Path, default=ROOT / "harness" / "runs" / "screen-v1")
    ap.add_argument("--subagent-raw", type=Path, default=ROOT / "harness" / "runs" / "subagent-v1" / "raw")
    ap.add_argument("--out", type=Path, default=ROOT / "demo" / "data.js")
    args = ap.parse_args()

    bank = {json.loads(l)["id"]: json.loads(l)
            for l in (ROOT / "question_bank" / "bank.jsonl").read_text().splitlines() if l.strip()}
    overall = {r["qid"]: r for r in json.loads((args.run / "analysis.json").read_text())}
    theory = {r["qid"]: r for r in json.loads((args.run / "analysis_theory.json").read_text())}
    theory_rank = {qid: i + 1 for i, qid in enumerate(
        [r["qid"] for r in sorted(theory.values(), key=lambda x: x["tscore"], reverse=True)])}

    runs = defaultdict(lambda: defaultdict(list))
    rows = [json.loads(l) for l in (args.run / "results.jsonl").read_text().splitlines() if l.strip()]
    tot_cost = tot_in = tot_out = 0
    for r in rows:
        if r.get("error"):
            continue
        resp, u = r["response"], (r["response"]["usage"] or {})
        tot_cost += r.get("cost_usd") or 0
        tot_in += u.get("input_tokens") or 0
        tot_out += u.get("output_tokens") or 0
        runs[r["question_id"]][r["model"]].append({
            "rep": r.get("rep", 0),
            "output_tokens": u.get("output_tokens"),
            "reasoning_tokens": reason_tok(u),
            "cost_usd": r.get("cost_usd"),
            "stop_reason": resp.get("stop_reason"),
            "seconds": r.get("timing", {}).get("seconds"),
            "thinking": cap(resp.get("thinking"), THINK_CAP),
            "text": cap(resp.get("text"), TEXT_CAP),
        })

    problems = []
    for qid, ov in overall.items():
        b = bank[qid]
        is_theory = qid in theory
        problems.append({
            "id": qid, "exam": b.get("exam"), "topics": b.get("topics", []),
            "difficulty": b.get("difficulty"), "prompt": b.get("prompt"),
            "grading_type": b.get("grading_type"), "ai_audit": b.get("ai_audit"),
            "verified": b.get("verified", False),
            "parts": b.get("parts", []), "source": b.get("source"),
            "data": b.get("data", []),
            "is_theory": is_theory,
            "score": ov["score"],
            "tscore": theory[qid]["tscore"] if is_theory else None,
            "trank": theory_rank.get(qid),
            "signals": {k: ov[k] for k in ("f_reason", "f_out", "h_out", "f_trunc", "instab", "hedge")},
            "runs": {"gpt": sorted(runs[qid].get(GPT, []), key=lambda x: x["rep"]),
                     "haiku": sorted(runs[qid].get(HAIKU, []), key=lambda x: x["rep"])},
        })
    # Attach Claude sub-agent (Opus, closed-book) solutions where present.
    n_sub = 0
    for p in problems:
        md = args.subagent_raw / f"{p['id']}.md"
        if md.exists():
            n_sub += 1
            p["runs"]["subagent"] = [{
                "rep": 0, "output_tokens": None, "reasoning_tokens": None, "cost_usd": None,
                "stop_reason": "completed", "seconds": None, "thinking": "",
                "note": "Opus-tier Claude sub-agent · closed-book (no web) · session-billed · "
                        "final solution only (agent trajectory not captured)",
                "text": cap(md.read_text(), TEXT_CAP * 2)}]
    problems.sort(key=lambda p: (p["tscore"] if p["tscore"] is not None else -1e9), reverse=True)

    payload = {
        "built": datetime.now(timezone.utc).isoformat(),
        "run": args.run.name,
        "models": {"frontier": GPT, "floor": HAIKU, "subagent": "claude-subagent-opus"},
        "k": 3,
        "totals": {"problems": len(problems), "responses": len(rows),
                   "cost_usd": round(tot_cost, 2), "input_tokens": tot_in, "output_tokens": tot_out},
        "scoring": ("tscore = 1.0·z(gpt_reasoning) + 1.5·z(answer_instability) + "
                    "1.0·z(truncation) + 0.5·z(output_bulk), re-z-scored within theory. "
                    "Proxy hardness — NOT a correctness verdict."),
        "problems": problems,
    }
    args.out.write_text("window.DEMO = " + json.dumps(payload, ensure_ascii=False) + ";\n")
    mb = args.out.stat().st_size / 1e6
    print(f"wrote {args.out.relative_to(ROOT)} ({len(problems)} problems, {n_sub} with sub-agent, {mb:.1f} MB)")


if __name__ == "__main__":
    main()
