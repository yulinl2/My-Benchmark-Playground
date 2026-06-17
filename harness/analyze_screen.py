#!/usr/bin/env python3
"""Behavioral candidate analysis for a screen run (NO ground-truth grading).

Reads a run dir's per-call records and ranks problems by *proxy*-hardness signals
that don't require knowing the correct answer:

  - effort      : frontier (GPT-5.5) reasoning-token mean — how hard it worked.
  - instability : 1 - self-consistency of the frontier's final answer across the
                  k reps (number-set agreement; a frontier that can't reproduce
                  its own answer is likely struggling).
  - truncation  : fraction of frontier reps that hit the output cap.
  - bulk        : combined output length across both models (overall difficulty).
  - hedging     : uncertainty markers in the frontier's answers.

Each signal is z-scored across problems and combined. Higher score = stronger
candidate (frontier works hard, is inconsistent, runs long). This is a SHORTLIST
heuristic to focus human review + later grading — not a correctness verdict.

    python harness/analyze_screen.py --run harness/runs/screen-v1
"""
import argparse, json, re, statistics as st
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRONTIER = "gpt-5.5"
FLOOR = "claude-haiku-4-5-20251001"
HEDGE = re.compile(r"\b(not sure|unsure|i can'?t|cannot determine|tricky|reconsider|"
                   r"i think|might be|approximately|unclear|not certain|stuck|"
                   r"this is hard|difficult)\b", re.I)
NUM = re.compile(r"-?\d+(?:\.\d+)?(?:/\d+)?")


def reason_tokens(u):
    d = (u or {}).get("output_tokens_details") or {}
    return d.get("thinking_tokens") or d.get("reasoning_tokens") or 0


def num_set(text):
    # numbers in the last ~600 chars (the conclusion region)
    return set(NUM.findall((text or "")[-600:]))


def jaccard(a, b):
    if not a and not b: return 1.0
    if not a or not b: return 0.0
    return len(a & b) / len(a | b)


def self_consistency(texts):
    sets = [num_set(t) for t in texts]
    sets = [s for s in sets if s]
    if len(sets) < 2: return None   # no numeric answers to compare
    pairs = [jaccard(sets[i], sets[j]) for i in range(len(sets)) for j in range(i + 1, len(sets))]
    return st.mean(pairs)


def zscores(vals):
    xs = [v for v in vals if v is not None]
    if len(xs) < 2: return [0.0 for _ in vals]
    m, s = st.mean(xs), st.pstdev(xs) or 1.0
    return [((v - m) / s if v is not None else 0.0) for v in vals]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", type=Path, required=True)
    ap.add_argument("--top", type=int, default=25)
    args = ap.parse_args()
    rows = [json.loads(l) for l in (args.run / "results.jsonl").read_text().splitlines() if l.strip()]

    byq = defaultdict(lambda: defaultdict(list))
    meta = {}
    for r in rows:
        if r.get("error"): continue
        byq[r["question_id"]][r["model"]].append(r)
        meta[r["question_id"]] = r.get("exam", {})

    recs = []
    for qid, models in byq.items():
        f = models.get(FRONTIER, []); h = models.get(FLOOR, [])
        f_resp = [x["response"] for x in f]; h_resp = [x["response"] for x in h]
        f_reason = st.mean([reason_tokens(x["usage"]) for x in f_resp]) if f_resp else 0
        f_out = st.mean([x["usage"]["output_tokens"] for x in f_resp]) if f_resp else 0
        h_out = st.mean([x["usage"]["output_tokens"] for x in h_resp]) if h_resp else 0
        f_trunc = (sum(1 for x in f_resp if x.get("stop_reason") in ("max_tokens", "incomplete"))
                   / len(f_resp)) if f_resp else 0
        cons = self_consistency([x["text"] for x in f_resp])
        instab = (1 - cons) if cons is not None else None
        hedge = st.mean([len(HEDGE.findall(x["text"] or "")) for x in f_resp]) if f_resp else 0
        recs.append(dict(qid=qid, part=meta[qid].get("part"), level=meta[qid].get("level", "phd"),
                         f_reason=f_reason, f_out=f_out, h_out=h_out, f_trunc=f_trunc,
                         instab=instab, hedge=hedge))

    z_reason = zscores([r["f_reason"] for r in recs])
    z_instab = zscores([r["instab"] for r in recs])
    z_trunc = zscores([r["f_trunc"] for r in recs])
    z_bulk = zscores([r["f_out"] + r["h_out"] for r in recs])
    z_hedge = zscores([r["hedge"] for r in recs])
    for i, r in enumerate(recs):
        r["score"] = round(1.0 * z_reason[i] + 1.5 * z_instab[i] + 1.0 * z_trunc[i]
                           + 0.5 * z_bulk[i] + 0.5 * z_hedge[i], 3)
    recs.sort(key=lambda r: r["score"], reverse=True)

    lines = ["# Candidate shortlist — behavioral proxy (NO ground-truth grading)",
             f"\nRun: `{args.run.name}` · {len(recs)} problems · frontier=`{FRONTIER}`, floor=`{FLOOR}`, k=3.",
             "\nScore = 1.0·z(reasoning) + 1.5·z(answer-instability) + 1.0·z(truncation) "
             "+ 0.5·z(output-bulk) + 0.5·z(hedging). Higher = stronger candidate. "
             "`instab` is blank when the frontier's answers had no comparable numbers (proof-style — judge later).",
             "\n| rank | score | qid | part | lvl | gpt_reason | gpt_out | hk_out | trunc | instab | hedge |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(recs, 1):
        ins = f"{r['instab']:.2f}" if r["instab"] is not None else "—"
        lines.append(f"| {i} | {r['score']:.2f} | {r['qid']} | {r['part']} | {r['level']} | "
                     f"{r['f_reason']:.0f} | {r['f_out']:.0f} | {r['h_out']:.0f} | "
                     f"{r['f_trunc']:.2f} | {ins} | {r['hedge']:.1f} |")
    (args.run / "analysis.md").write_text("\n".join(lines) + "\n")
    (args.run / "analysis.json").write_text(json.dumps(recs, indent=2) + "\n")
    print("\n".join(lines[:5 + args.top]))
    print(f"\n[wrote {args.run/'analysis.md'} and analysis.json]")


if __name__ == "__main__":
    main()
