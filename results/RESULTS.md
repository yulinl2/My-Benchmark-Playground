# Results (captured in this branch)

## Tier 1 — Numeric (numpy)

### Separation Theorem I — `rank_separation.json`
For `Gather(N)`, optimal attention `A* = P_pi` has `rank = N`. A fixed linear head
with capacity `H*m = 8` is rank-bounded, so its relative gather error has a floor
`= 1 - Hm/N` (Eckart–Young). Softmax (logits `= beta*P_pi`) drives error to 0.

`EckartYoung` is the rigorous lower bound on *any* rank-≤Hm map (singular-values
only → deterministic); `concrete rel.err` is one deterministic rank-≤Hm map
(P_pi with all but its first Hm columns zeroed, no SVD) — an achievable point
that necessarily sits at or above the floor.

| N | rank(A*) | Eckart–Young rel.err² (=1−Hm/N) | concrete rank-Hm rel.err | softmax (β=30) |
|---|---|---|---|---|
| 8 | 8 | 0.000 | 0.000 | 0.000000 |
| 16 | 16 | 0.500 | 0.707 | 0.000000 |
| 32 | 32 | 0.750 | 0.875 | 0.000000 |
| 64 | 64 | 0.875 | 0.933 | 0.000000 |
| 128 | 128 | 0.938 | 0.967 | 0.000000 |
| 256 | 256 | 0.969 | 0.983 | 0.000000 |

Softmax error vs temperature (N=64): β=1 → 0.96, β=3 → 0.76, β=10 → 0.003,
β≥30 → 0.000. The one-hot routing is realized once logits are sharp enough
(sharpness budget grows only like `log N`).

### Predictions P1/P2 — `train_curves.json`
A single TRAINED softmax head (weights fixed after training) generalizes to
held-out permutations; a CONCRETE deterministic rank-`m` map (an illustrative
proxy, *not* a proven upper bound over all linear heads) collapses as `m/N`. The
rigorous separation is the Frobenius-error bound above; this argmax curve is its
intuitive companion.

| N | softmax acc (held-out perms) | linear rank-m (concrete) acc | predicted floor 1−m/N |
|---|---|---|---|
| 8 | 1.000 | 1.000 | 0.000 |
| 16 | 1.000 | 0.500 | 0.500 |
| 32 | 1.000 | 0.250 | 0.750 |
| 64 | 1.000 | 0.125 | 0.875 |

Concrete rank-m accuracy `= m/N`; softmax stays at 1.0. **Separation confirmed.**

## Tier 2 — NL self-containedness audit on Haiku — `haiku_verification.json`

Nine NL instances solved by **in-session Haiku sub-agents** (Max-plan, no tools,
prompt-only), graded deterministically:

| Task | difficulties | accuracy |
|---|---|---|
| gather | N ∈ {8,16,32} | **1.00** |
| mqar | N=40, k ∈ {4,8,16} | **1.00** |
| chain | N=30, L ∈ {3,6,10} | **1.00** |

Interpretation: the NL lifts are genuinely solvable from the prompt alone by a
random-access (softmax) model — the precondition for the architectural separation
to be attributable to *architecture*, not missing knowledge. (Haiku raw responses
in `haiku_responses.json`.) This is a positive control, **not** a test of linear
attention; the decisive cross-architecture run on open SSM/linear checkpoints is
Tier 3 in `docs/02_experimental_plan.md`.

## Reproduce
```bash
python3 src/numeric/rank_separation.py
python3 src/numeric/train.py
python3 src/nl/task_generator.py --dump        # regenerate the suite
python3 src/nl/run_haiku_verification.py        # grade recorded Haiku responses
```
