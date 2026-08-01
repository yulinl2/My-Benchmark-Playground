"""Natural-language lifts of the numeric task family.

Each generator returns a dict with:
  - 'prompt'  : the text shown to a solver (open-book on the prompt, closed-book
                on the world: the answer is fully determined by the text);
  - 'answer'  : the hidden answer key (deterministic function of the prompt);
  - 'meta'    : difficulty parameters.

These share their answer key with the numeric instances by construction, so the
numeric and NL graders agree. Solvability requires faithful random access to the
context (what softmax attention provides); a fixed-state model must hold the whole
routing table in bounded memory, which fails as the difficulty knob grows.
"""
from __future__ import annotations
import argparse, json, random

WORDS = ("mango cedar violet quartz harbor lantern willow cobalt ember "
         "marble pewter saffron thicket clover bramble nectar gravel "
         "cinder tundra zephyr almond brisket cobweb dapple").split()
REAL_CITIES = ("Lisbon Cairo Oslo Tokyo Lima Accra Hanoi Quito Riga Doha Sofia "
               "Tunis Minsk Dakar Amman Bogota Manila Vienna Nassau Maputo"
               ).split()
BASE_NAMES = list("abcdefghijklmnopqrstuvwxyz")


def city_pool(n: int) -> list[str]:
    """>= n distinct city-like tokens (real ones first, then synthetic), so the
    requested instance size N is always honored deterministically."""
    pool = list(REAL_CITIES)
    i = 0
    while len(pool) < n:
        pool.append(f"Sector{i:04d}")
        i += 1
    return pool


def name_pool(n: int) -> list[str]:
    """>= n distinct variable names (single letters first, then synthetic)."""
    pool = list(BASE_NAMES)
    i = 0
    while len(pool) < n:
        pool.append(f"v{i:03d}")
        i += 1
    return pool


def _code(rng):
    return "".join(rng.choice(list("0123456789ABCDEFGHJKLMNPQRSTUVWXYZ"))
                   for _ in range(3))


def gather_nl(N: int, seed: int = 0) -> dict:
    """Reorder N labeled lines according to an explicit output order."""
    rng = random.Random(seed)
    items = [rng.choice(WORDS) for _ in range(N)]
    order = list(range(N)); rng.shuffle(order)          # 0-indexed sources
    lines = "\n".join(f"[{i+1}] {items[i]}" for i in range(N))
    order_1 = ", ".join(str(o + 1) for o in order)
    prompt = (
        "You are given a list of labeled lines and an output order.\n"
        f"Lines:\n{lines}\n\n"
        f"Output order (line numbers): {order_1}\n\n"
        "Task: print the CONTENTS of the lines in exactly the given output "
        "order, one word per line, nothing else.")
    answer = [items[o] for o in order]
    return {"task": "gather", "prompt": prompt,
            "answer": "\n".join(answer), "answer_list": answer,
            "meta": {"N": N, "seed": seed}}


def mqar_nl(N: int, k: int, seed: int = 0) -> dict:
    """In-context dictionary: N facts (k queried), then k questions."""
    rng = random.Random(seed)
    assert k <= N, "need at least k facts"
    pool = city_pool(N)                         # ensures >= N distinct cities
    cities = rng.sample(pool, k)
    codes = {c: _code(rng) for c in cities}
    # distractor facts to pad to exactly N total facts
    pad_cities = [c for c in pool if c not in cities]
    rng.shuffle(pad_cities)
    facts = [(c, codes[c]) for c in cities]
    for c in pad_cities[: N - k]:
        facts.append((c, _code(rng)))
    assert len(facts) == N, (len(facts), N)
    rng.shuffle(facts)
    fact_lines = "\n".join(f"- The access code for {c} is {code}."
                           for c, code in facts)
    q_cities = cities[:]; rng.shuffle(q_cities)
    questions = "\n".join(f"{i+1}. access code for {c}?"
                          for i, c in enumerate(q_cities))
    prompt = (
        "Use only the facts below.\n"
        f"Facts:\n{fact_lines}\n\n"
        f"Questions:\n{questions}\n\n"
        "Answer with one line per question as 'N. CODE', nothing else.")
    answer = "\n".join(f"{i+1}. {codes[c]}" for i, c in enumerate(q_cities))
    return {"task": "mqar", "prompt": prompt, "answer": answer,
            "answer_map": {c: codes[c] for c in q_cities},
            "meta": {"N": len(facts), "k": k, "seed": seed}}


def chain_nl(N: int, L: int, seed: int = 0) -> dict:
    """Variable-tracking: resolve a query var through an indirection chain of
    length L, among N total assignments (rest are distractors)."""
    rng = random.Random(seed)
    N = max(N, L + 1)
    pool = name_pool(N)                                 # ensures >= N names
    chain_vars = rng.sample(pool, L + 1)               # v0 -> v1 -> ... -> vL
    literal = rng.randint(10, 99)
    stmts = []
    # v0 = v1, v1 = v2, ..., v_{L-1} = vL, vL = literal
    for a, b in zip(chain_vars[:-1], chain_vars[1:]):
        stmts.append(f"Let {a} = {b}.")
    stmts.append(f"Let {chain_vars[-1]} = {literal}.")
    # distractors: assignments among other names to other literals
    others = [n for n in pool if n not in chain_vars]
    rng.shuffle(others)
    for n in others[: N - (L + 1)]:
        stmts.append(f"Let {n} = {rng.randint(10, 99)}.")
    assert len(stmts) == N, (len(stmts), N)
    rng.shuffle(stmts)
    body = "  ".join(stmts)
    query = chain_vars[0]
    prompt = (
        f"{body}\n\n"
        f"Question: What is the integer value of {query}? "
        "Answer with only the integer.")
    return {"task": "chain", "prompt": prompt, "answer": str(literal),
            "meta": {"N": max(N, L + 1), "L": L, "seed": seed}}


def build_suite():
    """The exact instance suite used for the Haiku sub-agent verification."""
    suite = []
    for N in (8, 16, 32):
        suite.append(gather_nl(N, seed=100 + N))
    for k in (4, 8, 16):
        suite.append(mqar_nl(N=40, k=k, seed=200 + k))
    for L in (3, 6, 10):
        suite.append(chain_nl(N=30, L=L, seed=300 + L))
    return suite


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--dump", action="store_true",
                    help="write the suite (prompts+keys) to results/nl/suite.json")
    args = ap.parse_args()
    if args.demo:
        for inst in (gather_nl(6, 1), mqar_nl(10, 3, 1), chain_nl(12, 4, 1)):
            print("=" * 70)
            print(f"[{inst['task']}] meta={inst['meta']}")
            print(inst["prompt"])
            print("--- answer key ---")
            print(inst["answer"])
    if args.dump:
        import os
        suite = build_suite()
        here = os.path.dirname(__file__)
        out = os.path.join(here, "..", "..", "results", "nl")
        os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, "suite.json"), "w", encoding="utf-8") as f:
            json.dump(suite, f, indent=2)
        print(f"wrote {len(suite)} instances to results/nl/suite.json")
