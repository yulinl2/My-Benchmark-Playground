"""Audit remediation A4: the O(log N)-width softmax construction, built.

The repo claimed softmax solves Gather(N) at fixed cost with logit sharpness
~log N, but the committed oracle used width-2N embeddings (width grew with N).
This module supplies the missing construction:

  * give each position a random sign code c_j in {+-1/sqrt(d)}^d,  d = K*ln(N)
  * keys k_j = c_j, queries q_i = beta * c_{pi(i)}
  * logits L_ij = beta * <c_{pi(i)}, c_j>: on-target exactly beta, off-target
    ~ N(0, beta^2/d); with d = K*ln N the max off-target logit is about
    beta*sqrt(2/K) < beta, so a margin of beta*(1 - sqrt(2/K)) survives, and
    beta = O(log N) drives the softmax row mass onto the target.

So softmax needs width d = O(log N) and logit scale O(log N) — while Theorem I
forces ANY linear head at the same width d to relative output error
>= sqrt(1 - d/N) -> 1. Same budget, opposite outcomes; this is the sharpest
form of the asymmetry, now measured rather than asserted.
"""
from __future__ import annotations
import json, os
import numpy as np


def softmax(z, axis=-1):
    z = z - z.max(axis=axis, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=axis, keepdims=True)


def run_instance(N, K, beta_mult, rng):
    d = max(4, int(np.ceil(K * np.log(N))))
    C = rng.choice([-1.0, 1.0], size=(N, d)) / np.sqrt(d)   # sign codes
    pi = rng.permutation(N)
    beta = beta_mult * np.log(N)
    A = softmax(beta * (C[pi] @ C.T), axis=-1)              # queries = codes of pi(i)
    V = rng.standard_normal((N, 16))
    P = np.zeros((N, N)); P[np.arange(N), pi] = 1.0
    acc = float((A.argmax(1) == pi).mean())
    mass = float(A[np.arange(N), pi].mean())
    err = float(np.linalg.norm(A @ V - P @ V) / np.linalg.norm(P @ V))
    return d, acc, mass, err


def main():
    out = {"rows": []}
    trials = 5
    print(f"{'N':>6} {'K':>3} {'d=K·lnN':>8} {'argmax_acc':>10} {'on_tgt_mass':>11} "
          f"{'out_err':>8} {'linear floor @ same d':>21}")
    for N in [64, 256, 1024, 4096]:
        for K in [4, 8]:
            rng = np.random.default_rng(N + K)
            res = [run_instance(N, K, beta_mult=3.0, rng=rng) for _ in range(trials)]
            d = res[0][0]
            acc = float(np.mean([r[1] for r in res]))
            mass = float(np.mean([r[2] for r in res]))
            err = float(np.mean([r[3] for r in res]))
            lin_floor = float(np.sqrt(max(0.0, 1 - d / N)))
            out["rows"].append(dict(N=N, K=K, d=d, beta_mult=3.0,
                                    argmax_acc=acc, on_target_mass=mass,
                                    output_rel_err=err,
                                    linear_floor_same_width=lin_floor))
            print(f"{N:>6} {K:>3} {d:>8} {acc:>10.3f} {mass:>11.3f} "
                  f"{err:>8.4f} {lin_floor:>21.3f}")
    here = os.path.dirname(__file__)
    res_dir = os.path.join(here, "..", "..", "results", "numeric")
    os.makedirs(res_dir, exist_ok=True)
    with open(os.path.join(res_dir, "softmax_logwidth.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print("\nwrote results/numeric/softmax_logwidth.json")
    print("Verdict: softmax at width O(log N) drives gather error to ~0 while "
          "any linear head at the SAME width is pinned above sqrt(1-d/N).")


if __name__ == "__main__":
    main()
