"""Numeric task generators with closed-form optimal attention maps.

Every instance is self-contained: the optimal output y* is a deterministic
function of the input, and the optimal attention matrix A* is returned so that
attention-pattern realizability can be measured directly.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass
class Instance:
    V: np.ndarray          # (N, d_v) value stream
    E: np.ndarray          # (N, D) input embeddings (carry the routing spec)
    Y_star: np.ndarray     # (N, d_v) optimal output
    A_star: np.ndarray     # (N, N) optimal attention matrix
    pi: np.ndarray         # the routing (permutation / matching) as index array


def gather(N: int, d_v: int = 16, seed: int = 0) -> Instance:
    """Gather(N): y*_i = v_{pi(i)}, A* = P_pi (a permutation matrix, rank N).

    Input embedding for position i carries: a one-hot of its OWN index (so it can
    serve as a key) and a one-hot of its SOURCE pointer pi(i) (so it can serve as
    a query). Thus the optimal softmax logits q_i . k_j = [j == pi(i)] are
    realizable by a linear read of E; the routing is fully present in the input.
    """
    rng = np.random.default_rng(seed)
    V = rng.standard_normal((N, d_v))
    pi = rng.permutation(N)
    I = np.eye(N)
    own = I                      # key side: position identity
    ptr = I[pi]                  # query side: one-hot of the source pointer
    E = np.concatenate([own, ptr], axis=1)   # (N, 2N)
    P = np.zeros((N, N))
    P[np.arange(N), pi] = 1.0    # P_pi: row i selects source pi(i)
    Y_star = P @ V
    return Instance(V=V, E=E, Y_star=Y_star, A_star=P, pi=pi)


def oracle_qk(inst: Instance):
    """Oracle (Q, K) that make softmax logits exactly the permutation pattern.

    q_i = one-hot(pi(i)), k_j = one-hot(j)  ->  q_i . k_j = [j == pi(i)].
    Used to exhibit weights for which softmax attention achieves A ~ P_pi.
    N is inferred from the embedding E = [own (N) | ptr (N)].
    """
    N = inst.E.shape[1] // 2
    K = inst.E[:, :N]            # own-index one-hots
    Q = inst.E[:, N:]            # source-pointer one-hots
    return Q, K


def mqar(N: int, k: int, d_v: int = 16, seed: int = 0) -> Instance:
    """Multi-query associative recall. Optimal attention = partial permutation
    matching each of k queries to the unique position of its key (rank k)."""
    rng = np.random.default_rng(seed)
    assert 2 * k <= N, "need room for k (key,val) slots and k query slots"
    V = rng.standard_normal((N, d_v))
    key_pos = rng.choice(N - k, size=k, replace=False)   # where keys live
    query_pos = np.arange(N - k, N)                       # queries at the tail
    perm = rng.permutation(k)                             # query j -> key perm[j]
    P = np.zeros((N, N))
    pi = np.full(N, -1)
    for j in range(k):
        qp = query_pos[j]
        kp = key_pos[perm[j]]
        P[qp, kp] = 1.0
        pi[qp] = kp
    Y_star = P @ V
    # Embedding: each query carries a one-hot pointer to its matching key slot;
    # each key carries its own position one-hot. (Self-contained matching.)
    own = np.eye(N)
    ptr = np.zeros((N, N))
    for qp in query_pos:
        ptr[qp, pi[qp]] = 1.0
    E = np.concatenate([own, ptr], axis=1)
    return Instance(V=V, E=E, Y_star=Y_star, A_star=P, pi=pi)


if __name__ == "__main__":
    inst = gather(8, seed=1)
    from attention import matrix_rank
    print("Gather(8): A* rank =", matrix_rank(inst.A_star), "(expect 8)")
    assert np.allclose(inst.Y_star, inst.A_star @ inst.V)
    m = mqar(12, 4, seed=1)
    print("MQAR(12,4): A* rank =", matrix_rank(m.A_star), "(expect 4)")
