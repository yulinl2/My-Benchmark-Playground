"""Softmax vs. linear (kernelized) attention primitives, in numpy.

These are the two operators compared throughout the project. The only structural
difference we exploit:

  * softmax attention's score matrix can be full rank (N) and arbitrarily peaked,
    so it can approximate any row-stochastic matrix, including any permutation;
  * linear attention's (unnormalized) score matrix S = phi(Q) phi(K)^T has
    rank <= m (the feature dimension), and normalization by row sums preserves
    that rank bound. This is the lever behind Separation Theorem I.
"""
from __future__ import annotations
import numpy as np


def softmax(z: np.ndarray, axis: int = -1) -> np.ndarray:
    z = z - z.max(axis=axis, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=axis, keepdims=True)


def softmax_attention(Q: np.ndarray, K: np.ndarray, V: np.ndarray,
                      scale: float | None = None) -> np.ndarray:
    """O = softmax(QK^T * scale) V."""
    if scale is None:
        scale = 1.0 / np.sqrt(Q.shape[-1])
    A = softmax(Q @ K.T * scale, axis=-1)
    return A @ V


def softmax_attention_matrix(Q: np.ndarray, K: np.ndarray,
                             scale: float | None = None) -> np.ndarray:
    if scale is None:
        scale = 1.0 / np.sqrt(Q.shape[-1])
    return softmax(Q @ K.T * scale, axis=-1)


def feature_map(x: np.ndarray, kind: str = "elu") -> np.ndarray:
    """Positive feature map phi for linear attention (keeps scores nonnegative)."""
    if kind == "elu":          # elu(x)+1, the Katharopoulos et al. default
        return np.where(x > 0, x + 1.0, np.exp(x))
    if kind == "relu":
        return np.maximum(x, 0.0) + 1e-6
    if kind == "exp":          # exp features (low-rank softmax approximation)
        return np.exp(x - x.max(axis=-1, keepdims=True))
    raise ValueError(kind)


def linear_attention_matrix(Q: np.ndarray, K: np.ndarray,
                            kind: str = "elu") -> np.ndarray:
    """Row-normalized linear-attention matrix. rank(unnormalized) <= phi-dim."""
    PhiQ = feature_map(Q, kind)             # (N, m)
    PhiK = feature_map(K, kind)             # (N, m)
    S = PhiQ @ PhiK.T                        # (N, N), rank <= m
    denom = S.sum(axis=-1, keepdims=True) + 1e-9
    return S / denom


def linear_attention(Q: np.ndarray, K: np.ndarray, V: np.ndarray,
                     kind: str = "elu") -> np.ndarray:
    return linear_attention_matrix(Q, K, kind) @ V


def matrix_rank(A: np.ndarray, tol: float = 1e-8) -> int:
    s = np.linalg.svd(A, compute_uv=False)
    return int((s > tol * s[0]).sum()) if s[0] > 0 else 0
