# Findings: Generalizing the Separation in Breadth and Depth

> **⚠ Corrections from self-audit (`docs/05_self_audit.md`), finalized by the
> 75-run fresh-seed replication (`results/nl/sweep_replicated.json`):**
> (1) the `multihop_map t=32` "cliff" is **refuted** — 12/13 correct overall;
> (2) under LCS grading and replication, `selective_copy` and `sort_by_key`
> show **no real degradation** (LCS ≥ 0.93 at their largest sizes) and the only
> genuine degradation is `gather N=256` (LCS 0.74 ± 0.18). §3's single-seed
> positional table is **superseded** by RESULTS.md Tier-2c. Net: Haiku is
> at/near ceiling across the whole tested range — the softmax positive control
> is stronger than this document originally reported, and the "graceful
> degradation frontier" was mostly measurement artifact.

This document records what the program has actually established so far —
numerically (proved + run) and empirically on a commercial softmax model
(Haiku, via in-session sub-agents). It extends the original three tasks to a
**seven-family generator** (breadth) and a **scaling sweep to the degradation
frontier** (depth).

---

## 1. Breadth: the task family now spans seven self-contained generators

Every member is open-book on the prompt / closed-book on the world, has a
closed-form optimal attention pattern, and a single difficulty knob.

| Family | Knob | Optimal attention | Stresses |
|---|---|---|---|
| `gather` | N | permutation `P_π` (rank N) | high-rank routing |
| `mqar` | k | partial permutation (rank k) | associative recall |
| `chain` | L | composition of L pointer hops | indirection depth |
| `selective_copy` | N, keep-rate | partial permutation (rank = #kept) | filter-and-route |
| `sort_by_key` | N | argsort permutation (rank N) | global reorder |
| `kv_lastwrite` | n_keys | query → last write of key | recall with overwrites |
| `multihop_map` | t | t sequential one-hot lookups | deep composition |

Code: `src/nl/task_generator.py` (first three) + `src/nl/extra_tasks.py` (new
four). All graders self-test at 1.00 on the gold key.

---

## 2. Depth (numeric): multiple layers do not rescue linear attention

`src/numeric/depth_separation.py` (two-hop Gather, target `T = P₂P₁`, a rank-N
permutation):

- **Product of L rank-≤m row-stochastic maps stays rank ≤ m** (measured: rank
  8 → 8 → 5 → 1 for L = 1,2,4,8 at m=8). Stacking frozen linear layers cannot
  raise the rank ceiling, so the read-out handed to V is still rank ≤ m.
- **Two-hop routing:** a depth-2 softmax stack solves it to ~0 error at every N;
  a depth-2 frozen linear stack stays at/above the `1 − Hm/N` floor (rel. err
  0.88 → 1.00 for N = 16…128 at Hm=8). Adaptive (recomputing) layers are covered
  by the recurrent-state bound, Theorem II.

This is the executable form of the proposal's "even with multi-head, multi-layer"
clause: the limit is per-layer rank / fixed state, not depth.

---

## 3. Depth (NL): Haiku scaling sweep — the degradation fingerprint (P3)

27 instances, increasing difficulty, solved by **in-session Haiku sub-agents**
(prompt-only, each reads its own file), graded deterministically.
Source: `src/nl/sweep.py`; data: `results/nl/sweep_results.json`.

| Family | accuracy vs knob | reading |
|---|---|---|
| `mqar` (recall) | k16 **1.00**, k32 0.97–1.00, k64 **1.00**, k128 **1.00** (N up to 256) | flat — recall is easy for softmax even at 128 KV pairs |
| `chain` | L8 **1.00**, L16 **1.00**, L32 **1.00**, L64 **1.00** | flat — pointer indirection easy |
| `kv_lastwrite` | keys32 0.94, keys64 **1.00**, keys128 **1.00** (N up to 384) | flat — overwrite tracking easy |
| `gather` (permute) | N64 **1.00**, N128 0.59, N256 0.22 | **degrades with N** |
| `selective_copy` | N64 **1.00**, N128 0.81, N256 0.09 | **degrades with N** |
| `sort_by_key` | N32 0.81, N64 0.22, N128 0.02 | **degrades fastest** |
| `multihop_map` | t8 **1.00**, t16 **1.00**, t32 **0.00** | **cliff at deep composition** |

### Two qualitatively different regimes

1. **Recall-robust (softmax stays flat).** `mqar`, `chain`, `kv_lastwrite` remain
   ~perfect up to the largest difficulties tried (k=128 among 256 lines; 384-line
   overwrite logs). This is *precisely* the regime where the literature shows
   fixed-state linear/SSM models need state `∝ k` and provably fail (Zoology,
   Based) and where our Theorem II bites. **Sharpest separation:** softmax flat,
   fixed-state linear forced to collapse.

2. **High-rank-output-limited (even softmax degrades, but by `N`, gracefully).**
   `gather`/`sort_by_key`/`selective_copy` require emitting a length-`N`
   reordering (a rank-`N` permutation). Haiku degrades smoothly as `N` grows —
   *not* at a fixed small `N`. This is the **predicted fingerprint (P3)**:
   softmax's error rises with the budget needed, qualitatively unlike the linear
   `1 − Hm/N` floor that bites the instant `N > Hm`. The theory predicts a
   fixed-capacity linear model collapses *earlier and faster* on these same
   instances (Theorem I); confirming that gap is the Tier-3 cross-architecture
   experiment.

3. ~~**Deep composition cliff.**~~ **Withdrawn (self-audit).** The t=32 failure
   was a single instance; replication with fresh seeds gives 2/2 correct at
   t=32 (one solver even exploited the permutation's cycle structure). Pooled
   accuracy at t=32 is 2/3 — high variance, no cliff. See
   `results/nl/multihop_replication.json` and `docs/05_self_audit.md` (B3).

### Honest caveats

- `gather`/`sort`/`selective_copy` degradation in a *chat* model conflates
  attention with **output-generation/throughput** (long verbatim outputs, copy
  drift); the deterministic grader gives positional partial credit, so the
  numbers are a faithful lower bound on "got the routing right," not a clean
  attention-only measurement. Single seed for these — treat as trend, not point
  estimate. Recall-family results use 2 seeds where shown.
- This sweep is the **self-containedness audit + fingerprint**, not a test of
  linear attention (no commercial linear model exists). It establishes the
  precondition (tasks solvable by a random-access model) and the softmax
  degradation shape; the decisive separation is Tier 3.

---

## 4. What this adds to the original claim

- The separation is now a **generator over seven families**, not one example.
- The "multi-layer doesn't help" clause is **executable** (rank-of-product).
- On NL, the recall families give the **cleanest** target: softmax is empirically
  flat exactly where fixed-state models are provably forced to grow state — so a
  cross-architecture run there should show the widest, most attributable gap.
- The permutation-output families reveal a **softmax budget** too, which is the
  right place to look for the *largest absolute* numbers but the *noisiest*
  attribution.

## 5. Next (Tier 3, GPU)

Run `results/nl/sweep_spec.json` instances through open softmax vs. SSM/linear
checkpoints (Pythia/Llama vs. RWKV/Mamba/RetNet/Based/GLA) at matched parameters.
Prediction P4: on the **recall-robust** families the SSM/linear curves fall with
the knob while softmax stays flat; on the **permutation-output** families both
degrade but linear collapses at smaller `N` (the `1 − Hm/N` floor).
