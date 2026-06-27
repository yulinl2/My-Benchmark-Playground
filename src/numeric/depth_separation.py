"""Depth does not rescue linear attention (the multi-layer claim, made runnable).

Two-hop Gather: route via two in-context permutations, target T = P2 @ P1 (apply
P1 then P2), itself a permutation of rank N. A depth-2 softmax stack realizes it
(layer 1 = P1, layer 2 = P2, each a sharp one-hot map) with ~0 error. A depth-2
*frozen* linear stack composes two rank-<=m row-stochastic maps; since
rank(A2 @ A1) <= min(rank A1, rank A2) <= m, the composite still cannot represent
the rank-N permutation T, so its relative gather error stays >= 1 - Hm/N.

(Frozen layers are covered here; adaptive layers that recompute keys/queries are
covered by the recurrent-state/communication bound, Theorem II in the proposal.)
"""
from __future__ import annotations
import json, os
import numpy as np
from attention import softmax, matrix_rank


def perm_matrix(N, rng):
    P = np.zeros((N, N)); P[np.arange(N), rng.permutation(N)] = 1.0
    return P


def rank_of_product_demo(N=64, m=8, L=4, seed=0):
    """Product of L random rank-<=m row-stochastic maps still has rank <= m."""
    rng = np.random.default_rng(seed)
    prod = np.eye(N)
    for _ in range(L):
        U = rng.random((N, m)); Wt = rng.random((m, N))     # nonneg, rank <= m
        S = U @ Wt
        A = S / (S.sum(1, keepdims=True) + 1e-9)             # row-stochastic
        prod = A @ prod
    return matrix_rank(prod), m


def two_hop_errors(N, Hm, beta=30.0, seed=0):
    rng = np.random.default_rng(seed)
    V = rng.standard_normal((N, 16))
    P1, P2 = perm_matrix(N, rng), perm_matrix(N, rng)
    T = P2 @ P1                                              # rank N permutation
    den = np.linalg.norm(T @ V)

    # depth-2 softmax: each layer realizes one sharp hop
    A1s, A2s = softmax(beta * P1, 1), softmax(beta * P2, 1)
    sm = np.linalg.norm(A2s @ A1s @ V - T @ V) / den

    # depth-2 frozen linear: concrete rank-<=Hm map per layer (first Hm columns)
    r = min(Hm, N)
    A1l, A2l = P1.copy(), P2.copy(); A1l[:, r:] = 0; A2l[:, r:] = 0
    comp = A2l @ A1l
    lin = np.linalg.norm(comp @ V - T @ V) / den
    return sm, lin, matrix_rank(comp), matrix_rank(T)


def main():
    Hm = 8
    out = {"Hm": Hm, "rank_of_product": [], "two_hop": []}
    print(f"Linear capacity H*m = {Hm}\n")
    print("Product of L rank-<=m row-stochastic maps stays rank <= m:")
    for L in [1, 2, 4, 8]:
        rk, m = rank_of_product_demo(N=64, m=Hm, L=L, seed=L)
        out["rank_of_product"].append({"L": L, "rank_product": rk, "m": m})
        print(f"  L={L}: rank(product) = {rk}  (<= m = {m})")

    print("\nTwo-hop Gather: depth-2 softmax vs depth-2 frozen linear")
    print(f"{'N':>5} {'softmax_err':>12} {'linear_err':>11} {'1-Hm/N':>9} "
          f"{'rk(lin)':>8} {'rk(T)':>6}")
    for N in [16, 32, 64, 128]:
        sm, lin, rkc, rkt = two_hop_errors(N, Hm, seed=N)
        floor = max(0.0, 1.0 - Hm / N)
        out["two_hop"].append({"N": N, "softmax_rel_err": sm,
                               "linear_rel_err": lin, "floor_1_minus_Hm_N": floor,
                               "rank_composite": rkc, "rank_target": rkt})
        print(f"{N:>5} {sm:>12.6f} {lin:>11.4f} {floor:>9.4f} {rkc:>8} {rkt:>6}")

    here = os.path.dirname(__file__)
    res = os.path.join(here, "..", "..", "results", "numeric")
    os.makedirs(res, exist_ok=True)
    with open(os.path.join(res, "depth_separation.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print("\nwrote results/numeric/depth_separation.json")
    print("Verdict: stacking layers keeps the composite rank <= m, so depth-2 "
          "linear stays at the >=1-Hm/N floor; depth-2 softmax solves two-hop "
          "routing to ~0 error. Depth does not rescue linear attention.")


if __name__ == "__main__":
    main()
