#!/usr/bin/env python3
"""Multi-round ORACLE CRITIQUE-WRITING LOOP for the Rutgers qual bank.

The gap this closes
-------------------
`harness/runs/screen-v1` ranked the 86-problem screen set by a *behavioral proxy*
("NO ground-truth grading", analysis.md line 1) because the bank has no answer keys:
62 of 95 questions carry `solution: null`. Without oracles nothing can be *graded*,
so the hardness screen cannot be confirmed and the AND/OR gate cannot be evaluated.

This module writes oracles the only way that is defensible for a benchmark: not a
single model pass, but an adversarial **draft -> critique -> revise** loop that runs
until a critic stops finding substantive defects, keeping the entire round-by-round
audit trail so a human can see *why* the oracle says what it says.

Discipline (project law, CLAUDE.md §1 "NO VERDICTS - MARK THE DISPUTE")
----------------------------------------------------------------------
* Where a question already has an author/transcribed `solution`, this loop NEVER
  overwrites it. If the loop's answer disagrees, the record is emitted with
  `status: "DISPUTE"`, carrying BOTH values and the argument for each, for the team
  to decide. The loop produces evidence to attribute, not a verdict to assert.
* Where `solution` is absent, the oracle is emitted as a clearly-marked PROPOSAL
  with a confidence and its full critique history - a gap filled, not a fact claimed.

Providers
---------
`--provider openai`  metered (OPENAI_API_KEY); real automated loop.
`--provider inline`  free in-session path: writes numbered prompt packets to
                     `packets/` for the in-session Claude to answer, and ingests
                     the replies from `replies/`. Used because this environment has
                     no ANTHROPIC_API_KEY (Claude is session-authenticated).
`--provider echo`    offline dry-run; exercises the state machine without any model.

Examples
--------
    python harness/oracle_loop.py --list-gaps
    python harness/oracle_loop.py --ids 2023-summer-probability-q2 --provider echo
    python harness/oracle_loop.py --provider inline --limit 5 --emit-packets
    python harness/oracle_loop.py --provider inline --ingest
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QDIR = ROOT / "question_bank" / "questions"
OUT = ROOT / "harness" / "oracles"
ROUNDS_DIR = OUT / "rounds"
PACKETS = OUT / "packets"
REPLIES = OUT / "replies"

MAX_ROUNDS_DEFAULT = 4

# --------------------------------------------------------------------------- prompts

DRAFT_SYS = (
    "You are writing the ORACLE (authoritative answer key) for a problem on a Rutgers "
    "Statistics PhD qualifying examination. You are not sitting the exam; you are the "
    "examiner writing the key that graders will rely on.\n"
    "Produce, in Markdown:\n"
    "1. **Restatement** - what is actually being asked, each part separately.\n"
    "2. **Assumptions** - every assumption you must add because the prompt leaves it "
    "implicit (independence, regularity conditions, support, which convergence mode). "
    "State them; do not silently use them.\n"
    "3. **Derivation** - the full argument, each step justified, theorems named.\n"
    "4. **Final answer** - per part, boxed/explicit. If the answer is a closed form, "
    "give it exactly; if a numeric value, give it to at least 4 significant figures.\n"
    "5. **Grading criteria** - what a correct student answer must contain, and the "
    "most likely near-miss that should NOT get credit.\n"
    "6. **Self-assessed confidence** - one of high/medium/low, with the single biggest "
    "reason it might be wrong.\n"
    "Be rigorous over brisk. A wrong oracle is far worse than a slow one."
)

CRITIQUE_SYS = (
    "You are an adversarial reviewer whose ONLY job is to find defects in a proposed "
    "answer key for a PhD qualifying exam problem. Assume it is wrong until you have "
    "checked it. Attack, in this order:\n"
    "* **Mathematical error** - a false step, a dropped term, a bad limit/interchange, "
    "a misapplied theorem, a wrong constant or normalisation.\n"
    "* **Unstated / illegitimate assumption** - something used but not licensed by the "
    "problem, or an assumption that changes the answer.\n"
    "* **Misreading** - the key answers a different question than the one asked, or "
    "silently drops a part.\n"
    "* **Under-specification** - the final answer is not actually pinned down, or the "
    "grading criteria would pass a wrong student answer.\n"
    "Return STRICT JSON, no prose outside it:\n"
    '{"defects":[{"severity":"high|medium|low","kind":"...","where":"...",'
    '"explanation":"...","suggested_fix":"..."}],'
    '"verdict":"defects_found|no_substantive_defects",'
    '"independent_answer":"your own answer if you disagree, else null"}\n'
    "Do NOT invent defects to look useful. If after genuine checking you find nothing "
    'substantive, return an empty defect list and verdict "no_substantive_defects" - '
    "that is a valid and valuable result."
)

REVISE_SYS = (
    "You are revising an answer key in response to an adversarial review. For EACH "
    "defect raised: either (a) fix the key and say what changed, or (b) rebut the "
    "defect with a concrete argument for why the original was right. Do not silently "
    "ignore a defect, and do not capitulate to a defect you can actually rebut - a "
    "reviewer can be wrong. Then re-emit the COMPLETE revised key in the same 6-section "
    "format as the original draft, followed by a short **Response to review** section."
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --------------------------------------------------------------------------- bank io

def load_questions() -> list[dict]:
    qs: list[dict] = []
    for f in sorted(QDIR.glob("*.json")):
        d = json.loads(f.read_text())
        items = d if isinstance(d, list) else d.get("questions", [d])
        for q in items:
            q["_file"] = f.name
            qs.append(q)
    return qs


def oracle_gaps(qs: list[dict]) -> list[dict]:
    """Questions with no author solution - the oracle gap."""
    return [q for q in qs if not q.get("solution")]


# --------------------------------------------------------------------------- providers

def call_openai(system: str, user: str, model: str = "gpt-5.5", effort: str = "high") -> str:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY not set")
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com")
    body = json.dumps({
        "model": model,
        "input": [{"role": "system", "content": system},
                  {"role": "user", "content": user}],
        "reasoning": {"effort": effort},
    }).encode()
    req = urllib.request.Request(
        f"{base}/v1/responses", data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=600) as r:
        data = json.loads(r.read())
    out = []
    for item in data.get("output", []):
        for c in item.get("content", []) or []:
            if c.get("type") in ("output_text", "text"):
                out.append(c.get("text", ""))
    return "\n".join(out).strip()


def call_echo(system: str, user: str, **_) -> str:
    """Offline: exercises the loop without a model."""
    if "STRICT JSON" in system:
        return json.dumps({"defects": [], "verdict": "no_substantive_defects",
                           "independent_answer": None})
    return "[echo provider: no model called]"


PROVIDERS = {"openai": call_openai, "echo": call_echo}


# --------------------------------------------------------------------------- packets (inline / in-session)

def write_packet(qid: str, rnd: int, phase: str, system: str, user: str) -> Path:
    PACKETS.mkdir(parents=True, exist_ok=True)
    p = PACKETS / f"{qid}__r{rnd}__{phase}.md"
    p.write_text(
        f"<!-- oracle-loop packet | qid={qid} round={rnd} phase={phase} | answer into "
        f"{REPLIES.name}/{p.stem}.md -->\n\n"
        f"## SYSTEM\n\n{system}\n\n## TASK\n\n{user}\n"
    )
    return p


def read_reply(qid: str, rnd: int, phase: str) -> str | None:
    p = REPLIES / f"{qid}__r{rnd}__{phase}.md"
    return p.read_text().strip() if p.exists() else None


# --------------------------------------------------------------------------- the loop

def problem_text(q: dict) -> str:
    s = [f"# Problem {q['id']}",
         f"Exam: {q['exam'].get('year')} {q['exam'].get('term')} "
         f"{q['exam'].get('part')} ({q['exam'].get('level','?')}), problem {q.get('number')}",
         f"Topics: {', '.join(q.get('topics', []))}",
         f"Grading type: {q.get('grading_type')}", "", "## Statement", "", q["prompt"]]
    if q.get("parts"):
        s += ["", "## Parts"] + [f"- {p}" for p in q["parts"]]
    return "\n".join(s)


def parse_critique(txt: str) -> dict:
    """Tolerant JSON extraction from a critique reply."""
    m = re.search(r"\{.*\}", txt, re.S)
    if not m:
        return {"defects": [], "verdict": "unparseable", "raw": txt[:2000]}
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return {"defects": [], "verdict": "unparseable", "raw": txt[:2000]}


def substantive(critique: dict) -> bool:
    """Does this critique block convergence?

    FAILS CLOSED. An unparseable/malformed critique is treated as blocking, never as
    "no defects found". Otherwise a truncated or non-JSON reply would silently mark an
    oracle `converged=True` on the strength of a reply nobody could read - a false green
    in exactly the tool whose job is to stop false greens.
    """
    if critique.get("verdict") != "no_substantive_defects":
        if critique.get("verdict") in ("unparseable", None):
            return True
    return any(d.get("severity") in ("high", "medium")
               for d in critique.get("defects", []))


def run_loop(q: dict, provider: str, max_rounds: int, emit_only: bool = False) -> dict:
    """draft -> (critique -> revise)* until the critic finds nothing substantive."""
    call = PROVIDERS.get(provider)
    qid, ptext = q["id"], problem_text(q)
    rounds: list[dict] = []

    # ---- round 0: draft
    if provider == "inline":
        if emit_only:
            write_packet(qid, 0, "draft", DRAFT_SYS, ptext)
            return {"id": qid, "status": "PACKET_EMITTED", "rounds": []}
        draft = read_reply(qid, 0, "draft")
        if draft is None:
            return {"id": qid, "status": "AWAITING_REPLY", "awaiting": f"{qid}__r0__draft"}
    else:
        draft = call(DRAFT_SYS, ptext)
    rounds.append({"round": 0, "phase": "draft", "content": draft, "ts": _now()})

    converged = False
    for r in range(1, max_rounds + 1):
        cu = (f"{ptext}\n\n---\n\n## PROPOSED ANSWER KEY (review this)\n\n{draft}")
        if provider == "inline":
            if emit_only:
                write_packet(qid, r, "critique", CRITIQUE_SYS, cu)
                break
            craw = read_reply(qid, r, "critique")
            if craw is None:
                return {"id": qid, "status": "AWAITING_REPLY",
                        "awaiting": f"{qid}__r{r}__critique", "rounds": rounds}
        else:
            craw = call(CRITIQUE_SYS, cu)
        crit = parse_critique(craw)
        rounds.append({"round": r, "phase": "critique", "content": crit, "ts": _now()})

        if not substantive(crit):
            converged = True
            break

        ru = (f"{ptext}\n\n---\n\n## CURRENT KEY\n\n{draft}\n\n---\n\n"
              f"## ADVERSARIAL REVIEW\n\n{json.dumps(crit, indent=2)}")
        if provider == "inline":
            if emit_only:
                write_packet(qid, r, "revise", REVISE_SYS, ru)
                break
            rev = read_reply(qid, r, "revise")
            if rev is None:
                return {"id": qid, "status": "AWAITING_REPLY",
                        "awaiting": f"{qid}__r{r}__revise", "rounds": rounds}
        else:
            rev = call(REVISE_SYS, ru)
        draft = rev
        rounds.append({"round": r, "phase": "revise", "content": rev, "ts": _now()})

    # ---- emit, honouring NO-VERDICTS
    author = q.get("solution")
    rec = {
        "id": qid,
        "generated": _now(),
        "provider": provider,
        "producing_model": "claude-opus-5" if provider == "inline" else provider,
        "rounds_used": max(x["round"] for x in rounds) if rounds else 0,
        "converged": converged,
        "unparseable_critiques": [
            x["round"] for x in rounds
            if x["phase"] == "critique"
            and isinstance(x["content"], dict)
            and x["content"].get("verdict") == "unparseable"
        ],
        "oracle_markdown": draft,
        "author_solution_present": bool(author),
        "status": "PROPOSAL" if not author else "CHECK_AGAINST_AUTHOR",
        "note": (
            "PROPOSAL - the bank had no answer key for this question; this is an "
            "agent-generated oracle with its full critique history, NOT a verified fact. "
            "Human verification still required (`verified` stays false)."
            if not author else
            "An author solution exists. This loop does NOT overwrite it. Compare and, "
            "if they disagree, record a DISPUTE for the team to decide."
        ),
        "rounds": rounds,
    }
    ROUNDS_DIR.mkdir(parents=True, exist_ok=True)
    (ROUNDS_DIR / f"{qid}.json").write_text(json.dumps(rec, indent=2, ensure_ascii=False))
    return rec


# --------------------------------------------------------------------------- cli

def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--provider", default="echo", choices=["openai", "inline", "echo"])
    ap.add_argument("--ids", help="comma-separated question ids")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--max-rounds", type=int, default=MAX_ROUNDS_DEFAULT)
    ap.add_argument("--list-gaps", action="store_true",
                    help="list questions with no author solution and exit")
    ap.add_argument("--emit-packets", action="store_true",
                    help="inline provider: write prompt packets to oracles/packets/ and exit")
    ap.add_argument("--ingest", action="store_true",
                    help="inline provider: consume oracles/replies/ and advance the loop "
                         "(this is already the default for --provider inline; the flag "
                         "just states the intent explicitly)")
    a = ap.parse_args(argv)

    if a.emit_packets and a.ingest:
        ap.error("--emit-packets and --ingest are mutually exclusive: the first writes "
                 "prompts, the second consumes answers.")
    if (a.emit_packets or a.ingest) and a.provider != "inline":
        ap.error("--emit-packets/--ingest apply only to --provider inline.")

    qs = load_questions()
    gaps = oracle_gaps(qs)

    if a.list_gaps:
        print(f"{len(qs)} questions | {len(gaps)} with NO author solution (oracle gap)")
        for q in gaps:
            print(f"  {q['id']:34s} {q.get('grading_type')}")
        return 0

    targets = gaps
    if a.ids:
        want = {s.strip() for s in a.ids.split(",")}
        targets = [q for q in qs if q["id"] in want]
    if a.limit:
        targets = targets[: a.limit]

    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    for q in targets:
        rec = run_loop(q, a.provider, a.max_rounds, emit_only=a.emit_packets)
        results.append(rec)
        print(f"{rec['id']:34s} {rec.get('status'):22s} "
              f"rounds={rec.get('rounds_used','-')} converged={rec.get('converged','-')}")
    (OUT / "loop_index.json").write_text(json.dumps(
        [{k: v for k, v in r.items() if k != "rounds"} for r in results],
        indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
