# Self-Audit: Adversarial Pass Over the Research Content

**Scope:** everything substantive in this branch — the two theorems, the numeric
experiments, the seven-task generator, the Haiku sweep, and the novelty claims.
**Method:** re-derivation of every proof step; re-grading of the raw sweep
outputs with an alignment-robust scorer; fresh replication runs for the most
surprising sweep cell; literature re-check. Findings are ranked by severity.
Corrections have been annotated in `docs/04` and `results/RESULTS.md`; raw data
backing this audit is committed (`results/nl/sweep_responses.json`,
`results/nl/multihop_replication.json`).

**Bottom line.** The core rank bound (Theorem I, frozen read-out) is correct and
numerically exact, and the two-regime sweep observation survives. But three
findings materially change what this branch may claim: (1) no *trained* linear-
attention model was ever run — the "linear" curves are constructed maps, so
prediction P2 is untested; (2) the multi-layer ("depth") argument does not apply
to real architectures with residual connections; (3) two headline sweep numbers
were wrong — the `multihop t=32` "cliff" fails to replicate (2/2 fresh seeds
correct) and the `selective_copy` "collapse" was a grader artifact (0.094
positional → 0.898 alignment-robust). Closest prior art (Jelassi et al. 2024)
was missing from the related-work doc and overlaps the central thesis
substantially.

---

## A. Theory

### A1. Theorem I — core bound HOLDS; two write-up gaps (Minor)
Re-derived: for the frozen read-out setting, a linear-attention map has
`rank(A) ≤ Hm` (row normalization is diagonal scaling; preserves the bound), the
target `P_π` is orthogonal, and Eckart–Young gives relative squared error
`≥ 1 − Hm/N`. Numerics match to machine precision. Gaps:

- **(a) Multi-head with output projections.** The stated proof sums attention
  matrices, i.e. assumes per-head output projections `W_h = I`. Real multi-head
  output is `Σ_h A_h V W_h`, which is *not* of the form `A·V`. The bound still
  holds via the Kronecker form: the operator on `vec(V)` is `Σ_h (W_h^⊤ ⊗ A_h)`,
  each term of rank `≤ m·d_v`, so total rank `≤ H·m·d_v`, while the target
  `I_{d_v} ⊗ P_π` has `N·d_v` unit singular values → same floor `1 − Hm/N`.
  This lemma should be written into `docs/00` (it *strengthens* the claim).
- **(b) Uniqueness of `A*`.** With `d_v < N`, `AV = P_πV` on one instance does
  not force `A = P_π`. The argument is sound only because the embedding `E`
  carries routing one-hots and **no values**, so `A` is independent of `V` and
  the bound is in expectation over `V`. Currently implicit; should be explicit.

### A2. Depth argument does NOT cover real architectures (Major)
The "product of L rank-≤m stochastic maps has rank ≤ m" remark (docs/00 §4,
`depth_separation.py`) assumes **no residual connections**. With residual
streams the per-layer map is `I + (low rank)` — full rank — and inter-layer
MLPs recompute features, so the rank-product ceiling simply does not apply to
any real multi-layer linear-attention LLM. `depth_separation.py` demonstrates
the frozen, residual-free case only. The burden of the multi-layer claim rests
entirely on Theorem II — which is informal (A3). All claims of the form "depth
doesn't rescue linear attention" must be scoped to "frozen, residual-free
stacks (proved) + fixed-state streaming (informal argument)".

### A3. Theorem II is informal, and Gather's cut needs restating (Minor–Major)
No proof is written; the shape matches published formal results (Zoology's
state lower bound; Jelassi et al. 2024). Two specifics:
- Gather's routing pointers are **interleaved** with values in the prompt, so
  the "prefix cut before the queries" story fits MQAR/kv_lastwrite, not Gather
  as encoded. The correct Gather argument is a live-set one: at the midpoint
  cut of a random permutation, Θ(N) values must still be held. Fixable, but
  currently misstated.
- The overfit-vs-generalize corollary is a heuristic counting sketch, not a
  proof. Label it as such.

### A4. Softmax positive side: claim exceeds construction (Major)
The oracle and trained softmax heads use embeddings of width `2N` — **width
grows with the task**. The repo claims softmax handles all `N` at fixed cost
with logit sharpness `~log N`; the supporting construction (binary index codes
/ JL, `d_k = O(log N)`, as in Sanford–Hsu–Telgarsky) is asserted but never
built or measured. Either implement the `O(log N)`-width construction
numerically or hedge the claim. As it stands, the numeric experiments compare
*growing-width softmax* against *fixed-capacity linear*.

---

## B. Experiments

### B1. No trained linear-attention model exists anywhere (Critical)
`train.py` trains only the softmax head. Both "linear" curves are
**constructed** maps (rank truncations of `P_π`) whose `m/N` collapse is
arithmetic, not learned behavior. This is legitimate for the *bound* (P1 — it
caps all linear heads, trained or not), but prediction **P2 ("a trained fixed
linear model's accuracy is capped and decreases past N > Hm") was never
tested**, and any reading of the tables as "trained softmax vs trained linear"
is wrong. Cheapest fix with high value: train an actual elu-feature linear head
under the identical protocol; theory says it must sit at/below the floor.

### B2. Sequence graders overstate degradation — measured (Major)
`grade_gather` (also used by `selective_copy`/`sort_by_key`) scores
**positionally**: one inserted/dropped line early in a long output misaligns
everything after it. Re-grading the *raw committed responses* with LCS
(order-preserving, alignment-robust):

| instance | positional (committed) | LCS re-grade |
|---|---|---|
| gather N64 | 1.000 | 1.000 |
| gather N128 | 0.586 | 0.750 |
| gather N256 | 0.219 | 0.469 |
| selective_copy N64 | 1.000 | 1.000 |
| selective_copy N128 | 0.810 | 0.983 |
| selective_copy N256 | **0.094** | **0.898** |
| sort_by_key N32 | 0.812 | 0.906 |
| sort_by_key N64 | 0.219 | 0.578 |
| sort_by_key N128 | 0.023 | 0.492 |

**Consequences:** the P3 "graceful degradation" *direction* survives (gather
and sort genuinely degrade), but magnitudes were overstated ~2×, and the
`selective_copy` "collapse to 0.09" was **wrong in kind** — the model kept ~90%
of the correct items in order and was punished for inserting extras. Adopt
LCS/edit-distance grading for sequence outputs and re-issue the tables.

### B3. The multihop t=32 "cliff" fails to replicate (Major)
Original: `t32 seed0 = 0.00`, **n = 1**. Replication with fresh seeds (same
generator, fresh Haiku sub-agents): `t32 s1` ✓, `t32 s2` ✓ (solved via cycle
detection), `t24 s1` ✓ → **2/2 correct at t=32**. The "deep-composition cliff"
claim in docs/04 / RESULTS.md is unsupported; strike it. Pooled, t=32 is 2/3 —
high variance, needs ≥10 seeds before any claim. Data:
`results/nl/multihop_replication.json`.

### B4. Sweep statistics generally (Minor)
Most cells are n=1 (mqar n=2); no confidence intervals. All cells are point
samples; the findings doc says so for three families but the summary tables
read as measurements. Any external claim needs seed replication.

### B5. Width confound in `train.py` (Minor, subsumed by A4)
The softmax head's input dimension is `2N` — it scales with the sweep variable.

### B6. Units inconsistency in the rank table (Cosmetic)
`eckart_young_lower_rel` is *squared* relative error; `concrete_rankr_rel_err`
is *unsquared*. At N=16 they read 0.5 vs 0.707 — the **same optimum** in
different units, presented side by side. Harmonize (report both as unsquared).

---

## C. Claims and novelty

### C1. Missing closest prior art (Major)
**Jelassi, Brandfonbrener, Kakade, Malach — "Repeat After Me: Transformers are
Better than State Space Models at Copying" (arXiv:2402.01032, ICML 2024):**
proves a 2-layer transformer copies exponentially long strings while any
fixed-state GSSM is information-theoretically limited, and confirms on
pretrained LLMs. This is the same separation shape as Theorem II applied to a
copy task (≈ Gather with identity routing), including the pretrained-model
validation strategy. Zoology likewise has a *formal* recurrent-state lower
bound for MQAR. **Residual novelty here:** (i) the Eckart–Young *per-layer
rank* framing on a permutation target (clean and, to current knowledge, not
stated elsewhere in this form); (ii) closed-form `A*` as a measurable artifact
+ the generator/visualization packaging; (iii) the overfit-vs-generalize
framing. docs/03's novelty section must be tempered accordingly — done in this
commit's annotation; full rewrite pending.

### C2. Positioning of the task families (Minor)
`mqar` is imported (acknowledged); `chain` ≈ RULER's variable tracking;
`gather/sort/selective_copy` relate to the copying literature above. "Seven-
family generator" = 4 new members + consolidation; say so explicitly.

---

## D. Reproducibility & integrity

### D1. Raw sweep responses were not committed (fixed in this commit)
`sweep_results.json` had scores only; the raw answers lived in the ephemeral
scratchpad and would have been lost at container recycle — this audit could
re-grade only because the container survived. Now committed:
`results/nl/sweep_responses.json` (27 records).

### D2. Benchmark contamination risk (note for the future)
Prompts *and answer keys* are committed in a **public** repo; `noindex`
protects the Pages site, not the repository. If this generator is ever used
as a benchmark: evaluate only with fresh seeds, and add a canary GUID to
generated instances.

### D3. Console generators are structural mirrors (already disclosed)
The in-browser generators use a different PRNG; live previews are not the
committed instances. Documented; no action.

---

## E. What survives cleanly
- **Theorem I** (frozen read-out) — correct, tight, numerically exact.
- **Self-containedness audit design** — programmatic gold, graders 1.00 on
  gold, Haiku 1.00 on the base suite.
- **Two-regime observation** — recall-robust vs reorder-degrading survives
  re-grading, with corrected magnitudes.
- **Generator contract** — uniqueness, reproducibility, closed-form `A*`.

## F. Prioritized remediation
1. ✅ Commit raw sweep answers + replication data (this commit).
2. ✅ Annotate the two known-wrong claims (multihop cliff, selective_copy
   collapse) in docs/04 + RESULTS.md (this commit).
3. ✅ Train a real linear-attention head (closes B1 / tests P2) — see the
   addendum below; `src/numeric/train_linear.py`,
   `results/numeric/trained_linear.json`.
4. ✅ Re-scope the depth claim (A2) and add the Kronecker multi-head lemma
   (A1a) — docs/00 §2/§4 rewritten (frozen residual-free scope stated; lemma
   added); Theorem II cut argument fixed per A3 (clean-cut vs live-set);
   corollary labeled heuristic; P2 restated per the metric split.
5. ✅ Add Jelassi et al. to docs/03 and rewrite the novelty section (C1) —
   novelty repositioned as reframing/instrumentation of a known separation.
6. Switch sequence grading to LCS; re-issue all sweep tables (B2); ≥10 seeds
   for any cell used in a claim (B3/B4).
7. ✅ Build the `O(log N)`-width softmax construction (A4/B5) —
   `src/numeric/softmax_logwidth.py`: random sign codes, `d = K·ln N`,
   `β = 3·ln N`. Measured at N=4096, d=67: softmax output error 0.0000
   (argmax 1.000) while ANY linear head at the same width is pinned
   `≥ 0.992`. The width confound in train.py (B5) is thereby resolved:
   softmax genuinely needs only logarithmic width.

---

## Addendum (post-audit experiments): B1 closed, and P2 must be split

**Trained linear head (B1 → closed).** A real elu+1 kernelized head trained by
Adam on cross-entropy (fresh permutations each step, held-out eval, best-of-3
seeds) across `m ∈ {2,8,32} × N ∈ {8,16,32,64}`:

- Every `m<N` cell **saturates the Eckart–Young floor to ~3 decimals**
  (`‖A−P‖²/N = 1−m/N`; output error `= √(1−m/N)`), and argmax accuracy lands at
  `≈ m/N`. **P2's collapse is confirmed on actually-trained models**, and the
  old truncation proxy turns out to predict trained behavior almost exactly.
- `m>N` control cells train to ~perfect → capacity, not optimization, binds.
  (At exactly `m=N`, training sometimes finds feature-collision local optima —
  two keys sharing a feature direction, mass split 50/50; does not affect the
  `m<N` conclusions.)

**The metric split (new constructive proposition).** `argmax_vs_output.py`
exhibits a rank-**4** nonnegative-feature head — keys on a circle,
`s_ij = 1 + cos(θ_{π(i)}−θ_j)/2` — with **perfect argmax routing for every
permutation at every N** (verified to N=1024), whose on-target mass is exactly
`1.5/N` and whose output error rides the floor to 1. Consequences:

- Argmax accuracy is **not rank-limited** → it is the wrong metric for the
  separation; any table using it alone (including train.py's) is inconclusive
  as evidence by itself.
- The **output** `AV` (equivalently on-target mass / Frobenius error) **is**
  rank-limited, and trained heads sit exactly on that limit.
- P2, restated correctly: *a fixed-capacity linear model's gather **output
  error** is pinned to the `1−Hm/N` floor (trained heads saturate it), and its
  CE-trained argmax accuracy collapses as `m/N` — even though argmax routing
  per se is achievable at rank 4.*
- Slogan for the program: **fixed-state linear attention can know where to
  look; it cannot move the information.**
