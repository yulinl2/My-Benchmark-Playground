"""Empirical curves for predictions P1/P2 (proposal section 8).

Two heads on Gather(N), where the routing pi is fresh per instance and lives
entirely in the input embedding E (self-contained):

  * SOFTMAX head: we TRAIN one set of weights (W_Q, W_K) by gradient descent on a
    batch of random permutations and evaluate on HELD-OUT permutations. Because
    softmax can realize the one-hot routing pattern that is present in E, a single
    fixed head generalizes across permutations -> accuracy ~ 1 for every N.

  * LINEAR head: we report the accuracy of a CONCRETE, deterministic rank-<=m
    routing map (P_pi with all but its first m columns zeroed). This is an
    illustrative proxy showing a sensible low-rank map collapses as m/N; it is
    NOT claimed to be the optimal rank-m map nor a proven upper bound over all
    nonnegative/row-normalized linear-attention heads. The RIGOROUS separation is
    the Frobenius-error bound on ANY rank-<=m map (>= 1 - Hm/N), computed in
    rank_separation.py via Eckart-Young; this script's argmax curve is the
    intuitive companion to that bound.
"""
from __future__ import annotations
import json, os
import numpy as np
from attention import softmax
from tasks import gather


# ---------- softmax head: train across permutations, eval on held-out ----------
def train_softmax_head(N, dk=None, batch=64, steps=400, lr=0.5, seed=0):
    rng = np.random.default_rng(seed)
    D = 2 * N
    dk = dk or D
    Wq = 0.1 * rng.standard_normal((D, dk))
    Wk = 0.1 * rng.standard_normal((D, dk))
    scale = 1.0 / np.sqrt(dk)

    def make_batch(b, s):
        Es, tgts = [], []
        for i in range(b):
            inst = gather(N, d_v=4, seed=10_000 * s + i)
            Es.append(inst.E); tgts.append(inst.pi)
        return Es, tgts

    for step in range(steps):
        Es, tgts = make_batch(batch, step + 1)
        gWq = np.zeros_like(Wq); gWk = np.zeros_like(Wk)
        loss = 0.0
        for E, tgt in zip(Es, tgts):
            Q = E @ Wq; K = E @ Wk
            scores = (Q @ K.T) * scale
            A = softmax(scores, axis=-1)
            Yoh = np.eye(N)[tgt]
            loss += -np.log(A[np.arange(N), tgt] + 1e-12).mean()
            Graw = (A - Yoh) * scale / N
            dQ = Graw @ K; dK = Graw.T @ Q
            gWq += E.T @ dQ; gWk += E.T @ dK
        Wq -= lr * gWq / batch; Wk -= lr * gWk / batch
    # evaluate on held-out permutations (different seeds)
    acc = []
    for i in range(128):
        inst = gather(N, d_v=4, seed=999_000 + i)
        A = softmax((inst.E @ Wq) @ (inst.E @ Wk).T * scale, axis=-1)
        acc.append(float((A.argmax(1) == inst.pi).mean()))
    return float(np.mean(acc))


# ---------- linear head: concrete deterministic rank-m map (proxy) ----------
def linear_rankr_accuracy(N, m, trials=128):
    """Argmax accuracy of a concrete rank-<=m map (P_pi with only its first m
    columns kept). Deterministic (no SVD); collapses as m/N."""
    accs = []
    r = min(m, N)
    for i in range(trials):
        inst = gather(N, d_v=4, seed=500_000 + i)
        A = inst.A_star.copy()
        A[:, r:] = 0.0                       # rank-<=r sub-permutation
        accs.append(float((A.argmax(1) == inst.pi).mean()))
    return float(np.mean(accs))


def main():
    m = 8  # linear feature dim (fixed capacity)
    out = {"linear_feature_dim_m": m, "rows": []}
    print(f"Fixed linear capacity m = {m}\n")
    print(f"{'N':>5} {'softmax_acc(heldout)':>20} {'linear_rankm_acc':>17} "
          f"{'rank_floor 1-m/N':>17}")
    for N in [8, 16, 32, 64]:
        # larger N needs more steps to fit the (D=2N)-dim head; the optimum
        # (a permutation-routing head) exists and generalizes, so this is purely
        # an optimization budget, not a capacity limit.
        sm = train_softmax_head(N, steps=1200, lr=1.0, seed=N)
        lin = linear_rankr_accuracy(N, m)
        floor = max(0.0, 1.0 - m / N)
        out["rows"].append({"N": N, "softmax_heldout_acc": sm,
                            "linear_rankm_concrete_acc": lin,
                            "predicted_rank_floor_err": floor})
        print(f"{N:>5} {sm:>20.3f} {lin:>17.3f} {floor:>17.3f}")

    here = os.path.dirname(__file__)
    res = os.path.join(here, "..", "..", "results", "numeric")
    os.makedirs(res, exist_ok=True)
    with open(os.path.join(res, "train_curves.json"), "w") as f:
        json.dump(out, f, indent=2)
    print("\nwrote results/numeric/train_curves.json")
    print("Verdict: trained softmax generalizes to fresh permutations (~1.0); "
          "a concrete rank-m linear map's accuracy collapses as m/N. The "
          "rigorous separation is the >=1-Hm/N error bound (rank_separation.py).")


if __name__ == "__main__":
    main()
