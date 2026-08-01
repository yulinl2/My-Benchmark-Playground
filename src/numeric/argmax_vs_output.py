"""Audit follow-up (docs/05, B1/A1): argmax routing is rank-free; value routing
is rank-bound. A constructive proposition, verified numerically.

CONSTRUCTION (m = 4, independent of N). Put the N keys on a circle,
theta_j = 2*pi*j/N, with NONNEGATIVE features

  phi_K(j)    = [(1+cos t_j)/2, (1-cos t_j)/2, (1+sin t_j)/2, (1-sin t_j)/2]
  phi_Q(i)    = same at t_{pi(i)}

Then s_ij = phi_Q(i) . phi_K(j) = 1 + cos(t_{pi(i)} - t_j)/2 > 0, which is
uniquely maximized at j = pi(i). Hence for EVERY N and EVERY permutation pi, a
rank-<=4 linear-attention matrix routes PERFECTLY by argmax. But its rows are
nearly flat: on-target mass = 1.5/N -> 0, so the actual output AV is provably
garbage — relative gather error >= sqrt(1 - 4/N) -> 1 (Theorem I applies to the
output, not the argmax).

MORAL: prediction P2 must be split. A fixed-capacity linear head can LEARN
WHERE TO LOOK (argmax accuracy is not rank-limited — so argmax-accuracy tables
cannot demonstrate the separation), but it cannot MOVE THE INFORMATION (the
value-mixing output is rank-limited — this is the separation). The right
metric for every linear-vs-softmax comparison in this repo is output error /
on-target mass, never argmax accuracy alone.
"""
from __future__ import annotations
import json, os
import numpy as np


def circle_features(angles):
    c, s = np.cos(angles), np.sin(angles)
    return np.stack([(1 + c) / 2, (1 - c) / 2, (1 + s) / 2, (1 - s) / 2], axis=1)


def build_attention(N, pi):
    t = 2 * np.pi * np.arange(N) / N
    K = circle_features(t)              # (N,4) nonnegative
    Q = circle_features(t[pi])          # (N,4) nonnegative
    S = Q @ K.T                          # = 1 + cos(t_pi(i) - t_j)/2 > 0
    return S / S.sum(1, keepdims=True)


def main():
    rng = np.random.default_rng(0)
    out = {"m": 4, "rows": []}
    print(f"{'N':>5} {'argmax_acc':>10} {'on_tgt_mass':>11} {'1.5/N':>7} "
          f"{'out_rel_err':>11} {'floor sqrt(1-4/N)':>18}")
    for N in [8, 16, 64, 256, 1024]:
        pi = rng.permutation(N)
        A = build_attention(N, pi)
        P = np.zeros((N, N)); P[np.arange(N), pi] = 1.0
        V = rng.standard_normal((N, 16))
        acc = float((A.argmax(1) == pi).mean())
        mass = float(A[np.arange(N), pi].mean())
        err = float(np.linalg.norm(A @ V - P @ V) / np.linalg.norm(P @ V))
        floor = float(np.sqrt(max(0.0, 1 - 4 / N)))
        out["rows"].append(dict(N=N, argmax_acc=acc, on_target_mass=mass,
                                output_rel_err=err, floor=floor))
        print(f"{N:>5} {acc:>10.3f} {mass:>11.4f} {1.5/N:>7.4f} "
              f"{err:>11.4f} {floor:>18.4f}")
    here = os.path.dirname(__file__)
    res = os.path.join(here, "..", "..", "results", "numeric")
    os.makedirs(res, exist_ok=True)
    with open(os.path.join(res, "argmax_vs_output.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print("\nwrote results/numeric/argmax_vs_output.json")
    print("Verdict: perfect argmax routing at rank 4 for every N, while the "
          "output error rides the Theorem-I floor to 1. Argmax accuracy is the "
          "wrong metric for the separation; output error is the right one.")


if __name__ == "__main__":
    main()
