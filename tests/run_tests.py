"""Full-coverage test suite for the research line. Pure stdlib + numpy.

Run:  python3 tests/run_tests.py            (exit 0 = all pass)

Sections:
  1. Generator contracts  — determinism, size honoring, and SELF-CONTAINEDNESS:
     an independent reference solver re-derives every answer from the prompt
     TEXT alone (never from the generator's internals).
  2. Grader properties    — gold scores 1.0; corruption is penalized; <answer>
     extraction; LCS grader is insertion-robust and bounded.
  3. Numeric theorems     — A* correctness, Eckart-Young floor, concrete map
     above floor, softmax -> 0, oracle head exactness, depth rank bound.
  4. Sweep specs          — unique ids, deterministic regeneration, replication
     seeds disjoint from originals.
"""
from __future__ import annotations
import os, re, sys, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src", "nl"))
sys.path.insert(0, os.path.join(ROOT, "src", "numeric"))

import numpy as np
import task_generator as T
import extra_tasks as E
import grading as G
import sweep as S
import tasks as NT
import attention as A
from rank_separation import best_rankr_error, concrete_rankr_gather_error, softmax_gather_error
from depth_separation import rank_of_product_demo, two_hop_errors

FAILURES = []


def check(name, fn):
    try:
        fn()
        print(f"  PASS  {name}")
    except Exception:
        print(f"  FAIL  {name}")
        FAILURES.append((name, traceback.format_exc()))


# ---------------------------------------------------------------- #
# 1. Reference solvers: answer from PROMPT TEXT ONLY.               #
# ---------------------------------------------------------------- #
def solve_gather(prompt):
    lines = dict(re.findall(r"\[(\d+)\] (\w+)", prompt))
    order = re.search(r"Output order \(line numbers\): ([\d, ]+)", prompt).group(1)
    return "\n".join(lines[i.strip()] for i in order.split(","))


def solve_mqar(prompt):
    facts = dict(re.findall(r"access code for (\w+) is (\w+)\.", prompt))
    qs = re.findall(r"\d+\. access code for (\w+)\?", prompt)
    return "\n".join(f"{i+1}. {facts[c]}" for i, c in enumerate(qs))


def solve_chain(prompt):
    env = dict(re.findall(r"Let (\w+) = (\w+)\.", prompt))
    cur = re.search(r"integer value of (\w+)\?", prompt).group(1)
    seen = set()
    while not cur.isdigit():
        assert cur not in seen, "cycle"
        seen.add(cur)
        cur = env[cur]
    return cur


def solve_selective_copy(prompt):
    return "\n".join(w for w, f in re.findall(r"\[\d+\] (\w+) -- (KEEP|DROP)", prompt)
                     if f == "KEEP")


def solve_sort_by_key(prompt):
    pairs = re.findall(r"^(\w+) : (\d+)$", prompt, re.M)
    return "\n".join(w for w, k in sorted(pairs, key=lambda p: int(p[1])))


def solve_kv_lastwrite(prompt):
    last = {}
    for k, v in re.findall(r"set (\w+) = (\w+)", prompt):
        last[k] = v
    qs = re.findall(r"\d+\. current value of (\w+)\?", prompt)
    return "\n".join(f"{i+1}. {last[k]}" for i, k in enumerate(qs))


def solve_multihop(prompt):
    f = dict(re.findall(r"(\w+) -> (\w+)", prompt))
    mo = re.search(r"Start at (\w+) and apply the mapping (\d+) times", prompt)
    cur, t = mo.group(1), int(mo.group(2))
    for _ in range(t):
        cur = f[cur]
    return cur


GENS = {
    "gather": (lambda s: T.gather_nl(12, seed=s), solve_gather),
    "mqar": (lambda s: T.mqar_nl(30, 8, seed=s), solve_mqar),
    "chain": (lambda s: T.chain_nl(24, 6, seed=s), solve_chain),
    "selective_copy": (lambda s: E.selective_copy_nl(16, 0.5, seed=s), solve_selective_copy),
    "sort_by_key": (lambda s: E.sort_by_key_nl(14, seed=s), solve_sort_by_key),
    "kv_lastwrite": (lambda s: E.kv_lastwrite_nl(40, 12, 6, seed=s), solve_kv_lastwrite),
    "multihop_map": (lambda s: E.multihop_map_nl(20, 7, seed=s), solve_multihop),
}


def test_generators():
    for name, (gen, solver) in GENS.items():
        def determinism(gen=gen):
            a, b = gen(3), gen(3)
            assert a["prompt"] == b["prompt"] and a["answer"] == b["answer"]
        check(f"gen/{name}: deterministic under fixed seed", determinism)

        def distinct(gen=gen):
            assert gen(1)["prompt"] != gen(2)["prompt"]
        check(f"gen/{name}: distinct across seeds", distinct)

        def self_contained(gen=gen, solver=solver, name=name):
            for s in range(12):
                inst = gen(s)
                derived = solver(inst["prompt"])
                assert derived == inst["answer"], (
                    f"seed {s}: reference solver got {derived!r}, "
                    f"generator claims {inst['answer']!r}")
        check(f"gen/{name}: SELF-CONTAINED (reference solver == answer key, 12 seeds)",
              self_contained)

    def sizes():
        assert T.mqar_nl(40, 4, seed=0)["meta"]["N"] == 40
        assert len(re.findall(r"access code for", T.mqar_nl(40, 4, 0)["prompt"])) == 44  # 40 facts + 4 questions
        assert len(re.findall(r"Let \w+ =", T.chain_nl(30, 3, 0)["prompt"])) == 30
        assert len(re.findall(r"set \w+ =", E.kv_lastwrite_nl(96, 32, 16, 0)["prompt"])) == 96
    check("gen/sizes: requested N honored exactly", sizes)


# ---------------------------------------------------------------- #
# 2. Grader properties                                              #
# ---------------------------------------------------------------- #
def test_graders():
    def gold_perfect():
        for name, (gen, _) in GENS.items():
            inst = gen(0)
            assert G.grade("<answer>" + inst["answer"] + "</answer>", inst) == 1.0, name
            assert G.grade(inst["answer"], inst) == 1.0, name + " (no tags)"
    check("grade/*: gold answer scores 1.0 (with and without <answer> tags)", gold_perfect)

    def prose_wrap():
        inst = T.mqar_nl(20, 4, seed=1)
        out = "Sure! Here you go:\n<answer>\n" + inst["answer"] + "\n</answer>\nHope that helps."
        assert G.grade(out, inst) == 1.0
    check("grade/mqar: robust to surrounding prose", prose_wrap)

    def corruption():
        inst = T.gather_nl(10, seed=2)
        words = inst["answer_list"][:]
        words[0] = "wrongword"
        assert G.grade("\n".join(words), inst) == 0.9
    check("grade/gather: one wrong line costs exactly 1/N", corruption)

    def chain_wrong():
        inst = T.chain_nl(20, 4, seed=3)
        wrong = str((int(inst["answer"]) + 1) % 100)
        assert G.grade(wrong, inst) == 0.0
    check("grade/chain: wrong integer scores 0", chain_wrong)

    def lcs_props():
        inst = T.gather_nl(10, seed=4)
        gold = inst["answer_list"]
        # one inserted line early: positional collapses, LCS barely moves
        inserted = "\n".join([gold[0], "sneaky"] + gold[1:])
        pos = G.grade(inserted, inst)
        lcs = G.grade_seq_lcs(inserted, inst)
        assert lcs == 1.0, "LCS should ignore one insertion"
        assert pos < 0.3, "positional should collapse after insertion"
        assert G.grade_seq_lcs("", inst) == 0.0
        assert G.grade_seq_lcs("\n".join(gold), inst) == 1.0
    check("grade/lcs: insertion-robust, bounded, gold=1", lcs_props)


# ---------------------------------------------------------------- #
# 3. Numeric theorems                                               #
# ---------------------------------------------------------------- #
def test_numeric():
    def a_star():
        for N in (8, 24):
            inst = NT.gather(N, seed=N)
            assert np.allclose(inst.Y_star, inst.A_star @ inst.V)
            assert A.matrix_rank(inst.A_star) == N
        m = NT.mqar(24, 6, seed=1)
        assert A.matrix_rank(m.A_star) == 6
    check("num/tasks: Y* = A*V, rank(A*) exact (gather=N, mqar=k)", a_star)

    def ey_floor():
        for N, r in ((16, 8), (64, 8), (128, 16)):
            inst = NT.gather(N, seed=N)
            got = best_rankr_error(inst.A_star, r)
            assert abs(got - (N - r) / N) < 1e-9, (N, r, got)
    check("num/rank: Eckart-Young floor == 1 - r/N to 1e-9", ey_floor)

    def concrete_above_floor():
        inst = NT.gather(64, d_v=16, seed=7)
        err = concrete_rankr_gather_error(inst.A_star, inst.V, 8)
        floor = (64 - 8) / 64
        assert err ** 2 >= floor - 1e-9
    check("num/rank: concrete rank-m map sits at/above the floor", concrete_above_floor)

    def softmax_to_zero():
        inst = NT.gather(64, d_v=16, seed=7)
        e10 = softmax_gather_error(inst.A_star, inst.V, 10.0)
        e30 = softmax_gather_error(inst.A_star, inst.V, 30.0)
        assert e30 < e10 and e30 < 1e-4
    check("num/rank: softmax error monotone in beta and -> 0", softmax_to_zero)

    def oracle_exact():
        inst = NT.gather(32, seed=5)
        Q, K = NT.oracle_qk(inst)
        Amat = A.softmax_attention_matrix(Q * 40.0, K, scale=1.0)
        assert (Amat.argmax(1) == inst.pi).all()
    check("num/oracle: softmax head with oracle Q,K routes exactly pi", oracle_exact)

    def depth_bound():
        for L in (1, 2, 4, 8):
            rk, m = rank_of_product_demo(N=48, m=6, L=L, seed=L)
            assert rk <= m, (L, rk, m)
        sm, lin, rkc, rkt = two_hop_errors(64, 8, seed=64)
        assert sm < 1e-4 and lin >= (1 - 8 / 64) ** 0.5 - 1e-6 and rkc <= 8 and rkt == 64
    check("num/depth: product rank <= m for L in 1..8; two-hop separation holds", depth_bound)


# ---------------------------------------------------------------- #
# 4. Sweep specs                                                    #
# ---------------------------------------------------------------- #
def test_specs():
    def unique_ids():
        ids = [e["id"] for e in S.build_spec()]
        rids = [e["id"] for e in S.build_replication_spec()]
        assert len(ids) == len(set(ids))
        assert len(rids) == len(set(rids))
        assert not (set(ids) & set(rids))
    check("spec: ids unique within and across original/replication", unique_ids)

    def regen_deterministic():
        for e in S.build_spec()[:6]:
            assert S.instance_for(e)["prompt"] == S.instance_for(e)["prompt"]
    check("spec: instance regeneration deterministic", regen_deterministic)

    def replication_seeds_disjoint():
        orig = {(e["task"], e["label"], e["kwargs"]["seed"]) for e in S.build_spec()}
        for e in S.build_replication_spec():
            key = (e["task"], e["label"], e["kwargs"]["seed"])
            assert key not in orig, key
    check("spec: replication (task,label,seed) disjoint from originals", replication_seeds_disjoint)


if __name__ == "__main__":
    print("== 1. generator contracts ==")
    test_generators()
    print("== 2. grader properties ==")
    test_graders()
    print("== 3. numeric theorems ==")
    test_numeric()
    print("== 4. sweep specs ==")
    test_specs()
    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILURE(S):")
        for name, tb in FAILURES:
            print("---", name)
            print(tb)
        sys.exit(1)
    print("ALL TESTS PASSED")
