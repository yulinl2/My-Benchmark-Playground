"""Breadth: additional self-contained long-context task families.

Each is open-book on the prompt / closed-book on the world: the answer is a
deterministic function of the text, and the optimal solution requires a
high-rank / random-access attention pattern (a permutation, a partial
permutation, or a composition of pointer hops) that a fixed-state linear-
attention model cannot realize as the difficulty knob grows (Theorems I-II).

Generators return the standard instance dict:
  {task, prompt, answer, <task-specific key>, meta}
shared with src/nl/task_generator.py and graded by src/nl/grading.py.
"""
from __future__ import annotations
import argparse, random
from task_generator import WORDS, city_pool, name_pool, _code


# ------------------------------------------------------------------ #
# 1. selective_copy: filter-and-copy by an in-context KEEP/DROP flag. #
#    Optimal attention: output slot -> j-th KEPT position             #
#    (a partial permutation, rank = #kept).                           #
# ------------------------------------------------------------------ #
def selective_copy_nl(N: int, keep_rate: float = 0.5, seed: int = 0) -> dict:
    rng = random.Random(seed)
    items = [rng.choice(WORDS) for _ in range(N)]
    flags = [rng.random() < keep_rate for _ in range(N)]
    if not any(flags):                       # guarantee >=1 kept
        flags[rng.randrange(N)] = True
    lines = "\n".join(f"[{i+1}] {items[i]} -- {'KEEP' if flags[i] else 'DROP'}"
                      for i in range(N))
    prompt = (
        "Below are labeled items, each marked KEEP or DROP.\n"
        f"{lines}\n\n"
        "Task: output the words marked KEEP, in their original order, one per "
        "line, nothing else.")
    answer = [items[i] for i in range(N) if flags[i]]
    return {"task": "selective_copy", "prompt": prompt,
            "answer": "\n".join(answer), "answer_list": answer,
            "meta": {"N": N, "kept": len(answer), "seed": seed}}


# ------------------------------------------------------------------ #
# 2. sort_by_key: reorder items by an in-context numeric key.         #
#    Optimal attention: the argsort permutation (rank N).             #
# ------------------------------------------------------------------ #
def sort_by_key_nl(N: int, seed: int = 0) -> dict:
    rng = random.Random(seed)
    items = [rng.choice(WORDS) for _ in range(N)]
    keys = rng.sample(range(1000, 1000 + 9000), N)   # distinct -> unique order
    lines = "\n".join(f"{items[i]} : {keys[i]}" for i in range(N))
    prompt = (
        "Each line is 'word : key'.\n"
        f"{lines}\n\n"
        "Task: output the words sorted by key in ASCENDING order, one per "
        "line, nothing else.")
    order = sorted(range(N), key=lambda i: keys[i])
    answer = [items[i] for i in order]
    return {"task": "sort_by_key", "prompt": prompt,
            "answer": "\n".join(answer), "answer_list": answer,
            "meta": {"N": N, "seed": seed}}


# ------------------------------------------------------------------ #
# 3. kv_lastwrite: last-write-wins dictionary (recall with overwrites)#
#    Keys are reassigned; the answer is the LAST value per queried    #
#    key. A fixed-state model must track the latest value per key.    #
#    Optimal attention: query -> last occurrence of its key.          #
# ------------------------------------------------------------------ #
def kv_lastwrite_nl(N: int, n_keys: int, n_queries: int, seed: int = 0) -> dict:
    rng = random.Random(seed)
    assert n_keys <= N and n_queries <= n_keys
    keys = city_pool(n_keys)[:n_keys]      # exactly n_keys distinct names
    last = {}
    log = []
    # ensure every key written at least once
    order = list(range(n_keys))
    rng.shuffle(order)
    for idx in range(N):
        k = keys[order[idx]] if idx < n_keys else keys[rng.randrange(n_keys)]
        v = _code(rng)
        last[k] = v
        log.append((k, v))
    log_lines = "\n".join(f"set {k} = {v}" for k, v in log)
    q_keys = rng.sample(keys, n_queries)
    questions = "\n".join(f"{i+1}. current value of {k}?"
                          for i, k in enumerate(q_keys))
    prompt = (
        "This is a log of assignments; a later 'set' OVERRIDES an earlier one "
        "for the same name. Use only this log.\n"
        f"{log_lines}\n\n"
        f"Questions (give the CURRENT value):\n{questions}\n\n"
        "Answer one line per question as 'N. VALUE', nothing else.")
    answer = "\n".join(f"{i+1}. {last[k]}" for i, k in enumerate(q_keys))
    return {"task": "kv_lastwrite", "prompt": prompt, "answer": answer,
            "answer_map": {k: last[k] for k in q_keys},
            "meta": {"N": N, "n_keys": n_keys, "n_queries": n_queries,
                     "seed": seed}}


# ------------------------------------------------------------------ #
# 4. multihop_map: apply an in-context permutation map f, t times.    #
#    Optimal attention: t sequential one-hot lookups (pointer hops).  #
# ------------------------------------------------------------------ #
def multihop_map_nl(domain: int, t: int, seed: int = 0) -> dict:
    rng = random.Random(seed)
    names = name_pool(domain)[:domain]      # exactly `domain` distinct names
    perm = names[:]
    rng.shuffle(perm)
    f = {names[i]: perm[i] for i in range(domain)}       # bijection on domain
    pairs = list(f.items())
    rng.shuffle(pairs)
    table = "; ".join(f"{a} -> {b}" for a, b in pairs)
    start = rng.choice(names)
    cur = start
    for _ in range(t):
        cur = f[cur]
    prompt = (
        f"Mapping (each name maps to exactly one name): {table}.\n\n"
        f"Start at {start} and apply the mapping {t} times. "
        "Answer with only the final name.")
    return {"task": "multihop_map", "prompt": prompt, "answer": cur,
            "meta": {"domain": domain, "t": t, "seed": seed}}


GENERATORS = {
    "selective_copy": lambda **kw: selective_copy_nl(**kw),
    "sort_by_key": lambda **kw: sort_by_key_nl(**kw),
    "kv_lastwrite": lambda **kw: kv_lastwrite_nl(**kw),
    "multihop_map": lambda **kw: multihop_map_nl(**kw),
}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
    ap.parse_args()
    demos = [selective_copy_nl(8, 0.5, 1), sort_by_key_nl(6, 1),
             kv_lastwrite_nl(12, 5, 3, 1), multihop_map_nl(10, 4, 1)]
    for inst in demos:
        print("=" * 70)
        print(f"[{inst['task']}] meta={inst['meta']}")
        print(inst["prompt"])
        print("--- answer key ---")
        print(inst["answer"])
