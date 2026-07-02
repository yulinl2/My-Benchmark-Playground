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


def build_replication_spec():
    """Audit item 6 (docs/05 B2/B3/B4): fresh-seed replication of the cells
    used in claims. Headline cells get 10 fresh seeds; supporting cells get 4
    (pooled with the original seed-0 run -> n=5); the headline recall cell
    (mqar k128) gets 3 more (pooled n=5). Seeds are disjoint from the original
    sweep (which used seed 0, and 0/1 for mqar)."""
    spec = []

    def add(task, label, seeds, **kw):
        for s in seeds:
            k = dict(kw); k["seed"] = s
            spec.append({"id": f"{task}__{label}__r{s}", "task": task,
                         "label": label, "kwargs": k})

    HEAD = range(1, 11)      # 10 fresh seeds for headline cells
    SUPP = range(1, 5)       # 4 fresh seeds for supporting cells
    add("gather", "N64", SUPP, N=64)
    add("gather", "N128", SUPP, N=128)
    add("gather", "N256", HEAD, N=256)
    add("sort_by_key", "N32", SUPP, N=32)
    add("sort_by_key", "N64", SUPP, N=64)
    add("sort_by_key", "N128", HEAD, N=128)
    add("selective_copy", "N64", SUPP, N=64, keep_rate=0.5)
    add("selective_copy", "N128", SUPP, N=128, keep_rate=0.5)
    add("selective_copy", "N256", HEAD, N=256, keep_rate=0.5)
    add("multihop_map", "t8", SUPP, domain=48, t=8)
    add("multihop_map", "t16", SUPP, domain=48, t=16)
    add("multihop_map", "t32", HEAD, domain=48, t=32)
    add("mqar", "k128", range(2, 5), N=256, k=128)
    return spec


def emit_replication(dirpath):
    os.makedirs(dirpath, exist_ok=True)
    spec = build_replication_spec()
    for e in spec:
        inst = instance_for(e)
        with open(os.path.join(dirpath, e["id"] + ".txt"), "w",
                  encoding="utf-8") as f:
            f.write(inst["prompt"])
    print(f"emitted {len(spec)} replication prompts to {dirpath}")


def grade_replication(answers_dir):
    """Grade replication answers; sequence tasks scored BOTH ways (positional +
    LCS, audit B2). Writes per-cell mean/sd/n to sweep_replicated.json."""
    from grading import grade_seq_lcs
    from collections import defaultdict
    import statistics
    SEQ = {"gather", "sort_by_key", "selective_copy"}
    rows, cells = [], defaultdict(list)
    missing = 0
    for e in build_replication_spec():
        path = os.path.join(answers_dir, e["id"] + ".txt")
        if not os.path.exists(path):
            missing += 1
            continue
        inst = instance_for(e)
        with open(path, encoding="utf-8") as f:
            resp = f.read()
        pos = grade(resp, inst)
        lcs = grade_seq_lcs(resp, inst) if e["task"] in SEQ else None
        rows.append({"id": e["id"], "task": e["task"], "label": e["label"],
                     "seed": e["kwargs"]["seed"], "positional": pos,
                     "lcs": lcs})
        cells[(e["task"], e["label"])].append((pos, lcs))
    summary = []
    for (task, label), vals in sorted(cells.items()):
        pos = [v[0] for v in vals]
        entry = {"task": task, "label": label, "n_fresh_seeds": len(vals),
                 "positional_mean": statistics.mean(pos),
                 "positional_sd": statistics.pstdev(pos)}
        if vals[0][1] is not None:
            lcs = [v[1] for v in vals]
            entry["lcs_mean"] = statistics.mean(lcs)
            entry["lcs_sd"] = statistics.pstdev(lcs)
        summary.append(entry)
        line = (f"  {task:15} {label:6} n={len(vals):>2} "
                f"pos={entry['positional_mean']:.3f}±{entry['positional_sd']:.3f}")
        if "lcs_mean" in entry:
            line += f"  lcs={entry['lcs_mean']:.3f}±{entry['lcs_sd']:.3f}"
        print(line)
    here = os.path.dirname(__file__)
    dst = os.path.join(here, "..", "..", "results", "nl",
                       "sweep_replicated.json")
    with open(dst, "w", encoding="utf-8") as f:
        json.dump({"model": "claude-haiku (in-session sub-agent)",
                   "note": "fresh-seed replication of claim cells (audit item "
                           "6); sequence tasks scored positionally AND by LCS",
                   "rows": rows, "cells": summary}, f, indent=1)
    if missing:
        print(f"  ({missing} answers missing — those cells incomplete)")
    print(f"wrote results/nl/sweep_replicated.json ({len(rows)} runs)")


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
    ap.add_argument("--emit-rep")
    ap.add_argument("--grade-rep-dir")
    a = ap.parse_args()
    if a.emit:
        emit(a.emit)
    if a.grade_dir:
        grade_dir(a.grade_dir)
    if a.emit_rep:
        emit_replication(a.emit_rep)
    if a.grade_rep_dir:
        grade_replication(a.grade_rep_dir)
