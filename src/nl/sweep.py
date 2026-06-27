"""Scaling sweep harness: push each task family up the difficulty knob and find
where a commercial softmax model (Haiku) starts to degrade (prediction P3).

Usage:
  python3 sweep.py --emit DIR    # write per-instance prompt files + sweep_spec
  python3 sweep.py --grade FILE  # grade a responses JSON -> sweep_results.json

The orchestrator dispatches one Haiku sub-agent per instance (each reads its own
prompt file, uses only that text), collects <answer> blocks into the responses
JSON, then grades here. Prompts are regenerated deterministically from the spec
(task + kwargs + seed), so only the compact spec and the results are committed.
"""
from __future__ import annotations
import argparse, json, os
import task_generator as T
import extra_tasks as E
from grading import grade

GEN = {
    "gather": lambda kw: T.gather_nl(N=kw["N"], seed=kw["seed"]),
    "mqar": lambda kw: T.mqar_nl(N=kw["N"], k=kw["k"], seed=kw["seed"]),
    "chain": lambda kw: T.chain_nl(N=kw["N"], L=kw["L"], seed=kw["seed"]),
    "selective_copy": lambda kw: E.selective_copy_nl(
        N=kw["N"], keep_rate=kw.get("keep_rate", 0.5), seed=kw["seed"]),
    "sort_by_key": lambda kw: E.sort_by_key_nl(N=kw["N"], seed=kw["seed"]),
    "kv_lastwrite": lambda kw: E.kv_lastwrite_nl(
        N=kw["N"], n_keys=kw["n_keys"], n_queries=kw["n_queries"],
        seed=kw["seed"]),
    "multihop_map": lambda kw: E.multihop_map_nl(
        domain=kw["domain"], t=kw["t"], seed=kw["seed"]),
}


def build_spec():
    """(id, task, kwargs, difficulty-label) across families and difficulty."""
    spec = []

    def add(task, label, **kw):
        kw.setdefault("seed", 0)
        spec.append({"id": f"{task}__{label}__s{kw['seed']}",
                     "task": task, "label": label, "kwargs": kw})

    # recall family: number of KV pairs k is the knob (Zoology/Based axis)
    for k in (16, 32, 64, 128):
        for s in (0, 1):
            add("mqar", f"k{k}", N=max(160, 2 * k), k=k, seed=s)
    # pointer-chain depth
    for L in (8, 16, 32, 64):
        add("chain", f"L{L}", N=max(96, 2 * L), L=L, seed=0)
    # permutation routing length
    for N in (64, 128, 256):
        add("gather", f"N{N}", N=N, seed=0)
    # filter-and-copy
    for N in (64, 128, 256):
        add("selective_copy", f"N{N}", N=N, keep_rate=0.5, seed=0)
    # sort by key
    for N in (32, 64, 128):
        add("sort_by_key", f"N{N}", N=N, seed=0)
    # last-write-wins recall
    for nk in (32, 64, 128):
        add("kv_lastwrite", f"keys{nk}", N=3 * nk, n_keys=nk, n_queries=16,
            seed=0)
    # multi-hop composition
    for t in (8, 16, 32):
        add("multihop_map", f"t{t}", domain=48, t=t, seed=0)
    return spec


def instance_for(entry):
    return GEN[entry["task"]](entry["kwargs"])


def emit(dirpath):
    os.makedirs(dirpath, exist_ok=True)
    spec = build_spec()
    out_spec = []
    for e in spec:
        inst = instance_for(e)
        with open(os.path.join(dirpath, e["id"] + ".txt"), "w",
                  encoding="utf-8") as f:
            f.write(inst["prompt"])
        out_spec.append({"id": e["id"], "task": e["task"], "label": e["label"],
                         "kwargs": e["kwargs"], "meta": inst["meta"]})
    here = os.path.dirname(__file__)
    res = os.path.join(here, "..", "..", "results", "nl")
    os.makedirs(res, exist_ok=True)
    with open(os.path.join(res, "sweep_spec.json"), "w", encoding="utf-8") as f:
        json.dump(out_spec, f, indent=2)
    print(f"emitted {len(spec)} prompt files to {dirpath}")
    print(f"wrote results/nl/sweep_spec.json")
    for e in out_spec:
        print(f"  {e['id']:34} meta={e['meta']}")


def grade_dir(answers_dir):
    """Grade from a directory of per-instance answer files (<id>.txt), each
    written by its Haiku sub-agent. Missing files score 0 (and are flagged)."""
    rows = []
    for e in build_spec():
        inst = instance_for(e)               # regenerate -> hidden answer key
        path = os.path.join(answers_dir, e["id"] + ".txt")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                resp = f.read()
            score = grade(resp, inst)
        else:
            score = 0.0
        rows.append({"id": e["id"], "task": e["task"], "label": e["label"],
                     "meta": inst["meta"], "score": score})
    rows.sort(key=lambda x: (x["task"], x["label"]))
    here = os.path.dirname(__file__)
    dst = os.path.join(here, "..", "..", "results", "nl", "sweep_results.json")
    with open(dst, "w", encoding="utf-8") as f:
        json.dump({"model": "claude-haiku (in-session sub-agent)", "rows": rows},
                  f, indent=2)
    for x in rows:
        print(f"  {x['task']:15} {x['label']:8} acc={x['score']:.3f}  "
              f"meta={x['meta']}")
    print(f"\nwrote results/nl/sweep_results.json ({len(rows)} instances)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit")
    ap.add_argument("--grade-dir")
    a = ap.parse_args()
    if a.emit:
        emit(a.emit)
    if a.grade_dir:
        grade_dir(a.grade_dir)
