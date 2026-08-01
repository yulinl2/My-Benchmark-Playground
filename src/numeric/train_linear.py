"""Audit remediation B1: train an ACTUAL linear-attention head on Gather(N).

Closes docs/05_self_audit.md item 3. Unlike train.py (whose 'linear' curve is a
constructed rank truncation), this trains a real kernelized head end-to-end:

    phi(x) = elu(x) + 1  (Katharopoulos et al.),   Phi_Q = phi(E W_Q), same for K
    A = row-normalize( Phi_Q Phi_K^T ),  W_Q, W_K in R^{2N x m} learned by Adam
    loss = cross-entropy of each attention row against its target pi(i),

trained on fresh permutations each step, evaluated on held-out permutations —
the identical protocol used for the softmax head.

WHAT THE THEORY DOES AND DOES NOT PREDICT (be precise; see audit A1/B1):
  * Output/soft metrics ARE rank-bounded: ||A - P||_F^2 / N >= 1 - m/N and the
    gather output error ||AV - PV||/||PV|| >= sqrt(1 - m/N) in expectation,
    for ANY rank-<=m head, trained or not (Eckart-Young; A is V-independent
    because E carries only routing one-hots).
  * Argmax accuracy is NOT obviously rank-bounded: rows of a rank-m matrix can
    in principle place their argmax on any permutation (convex-hull argument),
    so a trained head could route correctly by argmax while its actual output
    AV remains provably corrupted. This experiment measures both.
"""
from __future__ import annotations
import json, os
import numpy as np


def phi(z):
    return np.where(z > 0, z + 1.0, np.exp(z))


def dphi(z):
    return np.where(z > 0, 1.0, np.exp(z))


def make_batch(N, B, seed):
    """Batched Gather(N) embeddings E (B,N,2N) and targets pi (B,N)."""
    rng = np.random.default_rng(seed)
    pis = rng.permuted(np.tile(np.arange(N), (B, 1)), axis=1)
    I = np.eye(N)
    own = np.broadcast_to(I, (B, N, N))
    ptr = I[pis]                              # (B,N,N) one-hots of pi(i)
    return np.concatenate([own, ptr], axis=2), pis


def forward(E, Wq, Wk):
    Zq = E @ Wq                       # (B,N,m) pre-activations
    Zk = E @ Wk
    Pq, Pk = phi(Zq), phi(Zk)
    S = np.einsum('bnm,bkm->bnk', Pq, Pk) + 1e-9   # (B,N,N), entries > 0
    A = S / S.sum(-1, keepdims=True)
    return Zq, Zk, Pq, Pk, S, A


def train_linear_head(N, m, steps=2500, B=64, lr=1e-2, seed=0):
    rng = np.random.default_rng(seed)
    D = 2 * N
    Wq = 0.5 * rng.standard_normal((D, m)) / np.sqrt(D)
    Wk = 0.5 * rng.standard_normal((D, m)) / np.sqrt(D)
    # Adam state
    mom = {k: np.zeros_like(v) for k, v in dict(q=Wq, k=Wk).items()}
    vel = {k: np.zeros_like(v) for k, v in dict(q=Wq, k=Wk).items()}
    b1, b2, eps = 0.9, 0.999, 1e-8
    for step in range(1, steps + 1):
        lr_t = lr * (0.1 + 0.9 * 0.5 * (1 + np.cos(np.pi * step / steps)))
        E, pis = make_batch(N, B, seed=100_000 * (seed + 1) + step)
        Zq, Zk, Pq, Pk, S, A = forward(E, Wq, Wk)
        Bn = np.arange(B)[:, None]
        Nn = np.arange(N)[None, :]
        # dCE/dS_ij = 1/rowsum - delta_{j=pi(i)}/S_{i,pi(i)}, averaged over B*N rows
        G = 1.0 / S.sum(-1, keepdims=True) * np.ones_like(S)
        G[Bn, Nn, pis] -= 1.0 / S[Bn, Nn, pis]
        G /= (B * N)
        dPq = np.einsum('bnk,bkm->bnm', G, Pk)
        dPk = np.einsum('bnk,bnm->bkm', G, Pq)
        gWq = np.einsum('bnd,bnm->dm', E, dPq * dphi(Zq))
        gWk = np.einsum('bnd,bnm->dm', E, dPk * dphi(Zk))
        for key, W, g in (('q', Wq, gWq), ('k', Wk, gWk)):
            mom[key] = b1 * mom[key] + (1 - b1) * g
            vel[key] = b2 * vel[key] + (1 - b2) * g * g
            mh = mom[key] / (1 - b1 ** step)
            vh = vel[key] / (1 - b2 ** step)
            W -= lr_t * mh / (np.sqrt(vh) + eps)
    return Wq, Wk


def train_best_of(N, m, seeds=(0, 1, 2), **kw):
    """P2 is a claim about a capability CAP, so the fair statistic is the best
    trained head over independent seeds (single-seed results can reflect local
    optima, e.g. feature collisions observed at m=N)."""
    best, best_ev = None, None
    for s in seeds:
        Wq, Wk = train_linear_head(N, m, seed=1000 * s + N + m, **kw)
        ev = evaluate(N, m, Wq, Wk)
        if best_ev is None or ev["argmax_acc"] > best_ev["argmax_acc"]:
            best, best_ev = (Wq, Wk), ev
    return best, best_ev


def evaluate(N, m, Wq, Wk, trials=128, d_v=16, seed=777):
    rng = np.random.default_rng(seed)
    accs, masses, frobs, outerrs = [], [], [], []
    for i in range(trials):
        E, pis = make_batch(N, 1, seed=999_000 + i)
        _, _, _, _, _, A = forward(E, Wq, Wk)
        A, pi = A[0], pis[0]
        P = np.zeros((N, N)); P[np.arange(N), pi] = 1.0
        V = rng.standard_normal((N, d_v))
        accs.append(float((A.argmax(1) == pi).mean()))
        masses.append(float(A[np.arange(N), pi].mean()))
        frobs.append(float(((A - P) ** 2).sum() / N))
        outerrs.append(float(np.linalg.norm(A @ V - P @ V) / np.linalg.norm(P @ V)))
    return dict(argmax_acc=float(np.mean(accs)),
                on_target_mass=float(np.mean(masses)),
                frob_err2_over_N=float(np.mean(frobs)),
                output_rel_err=float(np.mean(outerrs)))


def main():
    out = {"protocol": "elu+1 linear attention, W_Q/W_K trained by Adam on CE "
                       "over fresh permutations; held-out eval; floors are "
                       "Eckart-Young (soft metrics only)", "rows": []}
    print(f"{'N':>4} {'m':>4} {'argmax_acc':>10} {'on_tgt_mass':>11} "
          f"{'frob²/N':>8} {'floor':>6} {'out_err':>8} {'floor':>6}")
    for m in (2, 8, 32):
        for N in (8, 16, 32, 64):
            _, ev = train_best_of(N, m)
            f_frob = max(0.0, 1.0 - m / N)
            f_out = float(np.sqrt(f_frob))
            row = dict(N=N, m=m, **ev, floor_frob=f_frob, floor_out=f_out)
            out["rows"].append(row)
            print(f"{N:>4} {m:>4} {ev['argmax_acc']:>10.3f} "
                  f"{ev['on_target_mass']:>11.3f} {ev['frob_err2_over_N']:>8.3f} "
                  f"{f_frob:>6.3f} {ev['output_rel_err']:>8.3f} {f_out:>6.3f}")
    here = os.path.dirname(__file__)
    res = os.path.join(here, "..", "..", "results", "numeric")
    os.makedirs(res, exist_ok=True)
    with open(os.path.join(res, "trained_linear.json"), "w",
              encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print("\nwrote results/numeric/trained_linear.json")
    print("Read soft metrics against their floors (must sit at/above); argmax "
          "accuracy is unbounded by rank and is the honest test of P2.")


if __name__ == "__main__":
    main()
