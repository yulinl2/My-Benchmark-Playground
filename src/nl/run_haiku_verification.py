"""Tier-2 verification: NL self-containedness audit on a commercial softmax model.

WHAT THIS TESTS (and what it does NOT):
  * It DOES confirm the NL lifts are solvable from the prompt alone by a strong
    random-access (softmax) model -> the precondition for the architectural
    separation to be meaningful, and it fingerprints how softmax degrades (by
    context budget, not by routing rank).
  * It does NOT test linear attention: no commercial linear-attention model
    exists. The decisive cross-architecture test (open SSM/linear checkpoints) is
    Tier 3 in docs/02_experimental_plan.md.

HOW THE LIVE RUN IS DRIVEN:
  The orchestrator session calls its `Agent` tool with a Haiku-backed solver,
  once per instance (parallel), passing SOLVER_TEMPLATE.format(prompt=...). The
  solver gets ONLY the instance text (no tools, no web). Returned <answer> blocks
  are graded here and aggregated to results/nl/haiku_verification.json. We keep
  model calls out of this script (no API keys in the repo); this module provides
  the deterministic, reproducible grader + aggregation over recorded responses.
"""
from __future__ import annotations
import json, os, sys
from collections import defaultdict
from grading import grade

SOLVER_TEMPLATE = (
    "You are a careful solver. Use ONLY the information in the PROMPT below. "
    "Do not use outside knowledge. Put your final answer between <answer> and "
    "</answer> exactly in the requested format.\n\nPROMPT:\n{prompt}")


def aggregate(records: list[dict]) -> dict:
    """records: [{task, meta, response, ...}] -> per-task accuracy table."""
    here = os.path.dirname(__file__)
    with open(os.path.join(here, "..", "..", "results", "nl", "suite.json"),
              encoding="utf-8") as f:
        suite = json.load(f)
    by_key = {(s["task"], json.dumps(s["meta"], sort_keys=True)): s
              for s in suite}
    rows, buckets = [], defaultdict(list)
    for r in records:
        key = (r["task"], json.dumps(r["meta"], sort_keys=True))
        if key not in by_key:
            raise KeyError(
                f"recorded response {key} has no matching instance in "
                f"suite.json; regenerate the suite (task_generator.py --dump) "
                f"and re-run the solver so responses and suite stay in sync.")
        inst = by_key[key]
        score = grade(r["response"], inst)
        rows.append({"task": r["task"], "meta": r["meta"], "score": score})
        buckets[r["task"]].append(score)
    summary = {t: sum(v) / len(v) for t, v in buckets.items()}
    return {"model": "claude-haiku (in-session sub-agent)",
            "rows": rows, "per_task_accuracy": summary}


if __name__ == "__main__":
    # Grade a recorded responses file: {records:[{task,meta,response}]}.
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(__file__), "..", "..", "results", "nl",
        "haiku_responses.json")
    with open(path, encoding="utf-8") as f:
        records = json.load(f)["records"]
    out = aggregate(records)
    here = os.path.dirname(__file__)
    dst = os.path.join(here, "..", "..", "results", "nl",
                       "haiku_verification.json")
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out["per_task_accuracy"], indent=2))
    print(f"wrote {dst}")
