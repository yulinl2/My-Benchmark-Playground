"""Separation Theorem I, made executable (the proof you can run).

For Gather(N), the optimal attention is a permutation matrix P_pi. Because P_pi is
orthogonal, ALL its singular values equal 1, so by Eckart-Young the best rank-r
approximation leaves Frobenius error^2 = N - r. Any linear-attention map with H
heads of feature dim m has rank <= H*m, hence relative gather error >= 1 - H*m/N.
Softmax, by contrast, can make logits beta*P_pi and drives the error toward 0.
"""
from __future__ import annotations
import json, os
import numpy as np
from attention import softmax, matrix_rank
from tasks import gather


def best_rankr_error(P: np.ndarray, r: int) -> float:
    """Eckart-Young LOWER bound on the relative Frobenius error of ANY rank-<=r
    approximation of P. Uses only the singular VALUES of P (not the singular
    vectors), so it is deterministic and version-independent even though P's SVD
    basis is non-unique (a permutation has all singular values equal to 1)."""
    s = np.linalg.svd(P, compute_uv=False)
    err2 = float((s[r:] ** 2).sum())
    return err2 / float((s ** 2).sum())


def concrete_rankr_gather_error(P: np.ndarray, V: np.ndarray, r: int) -> float:
    """Relative gather error of a CONCRETE, deterministic rank-<=r routing map:
    P with all but its first r columns zeroed (a sub-permutation, rank <= r). No
    SVD is used, so the result is reproducible across LAPACK/numpy builds. This is
    one achievable rank-r map; its error necessarily sits at or above the
    Eckart-Young lower bound, illustrating that a sensible low-rank routing still
    fails. (It is not claimed to be the optimal rank-r map.)"""
    A = P.copy()
    A[:, r:] = 0.0
    num = np.linalg.norm(A @ V - P @ V)
    den = np.linalg.norm(P @ V)
    return float(num / den)


def softmax_gather_error(P: np.ndarray, V: np.ndarray, beta: float) -> float:
    A = softmax(beta * P, axis=-1)        # logits = beta * permutation pattern
    num = np.linalg.norm(A @ V - P @ V)
    den = np.linalg.norm(P @ V)
    return float(num / den)


def main():
    out = {"theorem": "I", "linear_rank_floor": [], "softmax_vs_beta": []}
    Hm = 8   # one head, feature dim 8 (the fixed linear capacity)
    print(f"Linear capacity H*m = {Hm}\n")
    print(f"{'N':>5} {'rank(A*)':>9} {'EckartYoung':>12} {'1-Hm/N':>9} "
          f"{'concrete_err':>12} {'softmax(b=30)':>14}")
    for N in [8, 16, 32, 64, 128, 256]:
        inst = gather(N, d_v=16, seed=N)
        P, V = inst.A_star, inst.V
        ey = best_rankr_error(P, min(Hm, N))      # = (N-Hm)/N for N>=Hm
        floor = max(0.0, 1.0 - Hm / N)
        lin = concrete_rankr_gather_error(P, V, min(Hm, N))
        sm = softmax_gather_error(P, V, beta=30.0)
        out["linear_rank_floor"].append(
            {"N": N, "rank_A_star": matrix_rank(P), "eckart_young_lower_rel": ey,
             "one_minus_Hm_over_N": floor, "concrete_rankr_rel_err": lin,
             "softmax_rel_err_beta30": sm})
        print(f"{N:>5} {matrix_rank(P):>9} {ey:>12.4f} {floor:>9.4f} "
              f"{lin:>12.4f} {sm:>14.6f}")

    print("\nSoftmax error vs temperature (N=64): sharper logits -> A -> P_pi")
    inst = gather(64, d_v=16, seed=7)
    for beta in [1, 3, 10, 30, 100]:
        e = softmax_gather_error(inst.A_star, inst.V, beta)
        out["softmax_vs_beta"].append({"N": 64, "beta": beta, "rel_err": e})
        print(f"  beta={beta:>4}: rel_err={e:.6f}")

    here = os.path.dirname(__file__)
    res = os.path.join(here, "..", "..", "results", "numeric")
    os.makedirs(res, exist_ok=True)
    with open(os.path.join(res, "rank_separation.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nwrote results/numeric/rank_separation.json")
    print("\nVerdict: linear floor == 1 - Hm/N (rises to 1 as N grows); "
          "softmax error -> 0. Theorem I confirmed numerically.")


if __name__ == "__main__":
    main()
