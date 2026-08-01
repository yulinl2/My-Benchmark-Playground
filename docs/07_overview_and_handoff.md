# A Task Distribution that Separates Softmax from Linear Attention — Overview & Handoff

**Purpose.** This is a self-contained intro for follow-up studies. Read it alone
and you will know: the question, the two theorems, exactly what was built and
measured, what holds vs. what was walked back, and where every artifact lives.
It is written to be *honest first* — the corrections are as important as the
results, because they define what a follow-up may safely build on.

**Branch:** `research/long-context-attention-expressivity-separation` (work lands
on `claude/long-context-task-distribution-2iydu1`).
**Live audit console:** <https://yulinl2.github.io/My-Benchmark-Playground/attention/>
(noindex; built from `main:sites/attention/`).
**Status:** analytic core proven; NL and trained-model evidence in hand, with a
documented adversarial self-audit and two published retractions.

---

## 1. The question

> Can we design a family of long-context tasks whose optimal attention pattern
> is **completely determined by the prompt itself** (a *self-contained* spec),
> yet a model built on **linear / kernelized attention** provably cannot hit it
> for **any fixed** parameter / head / depth budget — while softmax can?

Three requirements make the separation meaningful:

- **Constructive** — a generator of hard instances, not one cherry-picked example.
- **Self-contained** — the target `y*(x)` is a deterministic function of the
  input tokens, so failure can never be excused by "the model didn't know a
  fact." The fact is in the context, and the ground-truth attention map `A*(x)`
  is known in closed form (we can measure attention *realizability*, not just
  task accuracy).
- **Liftable** — the numeric construction carries over to natural language,
  where we probe commercial softmax models.

## 2. The construction

**`Gather(N)`** is the canonical member. The prompt lists values `v₁…v_N` and a
routing spec naming, for each output slot `i`, a source index `π(i)`. The optimum
is `Y* = P_π V` where `P_π` is the `N×N` permutation matrix of `π`. The **optimal
read-out attention is exactly `P_π`** — one-hot rows. With `π ∼ Unif(S_N)` this
is a uniformly random permutation.

Two literature-anchored siblings share the difficulty signature, and a
seven-family generator gives breadth:

| family | what it routes | optimal `A*` |
|---|---|---|
| `gather` | permutation of a value stream | full permutation `P_π` (rank `N`) |
| `mqar` | k key→value pairs, then k queries (Zoology diagnostic) | partial permutation (rank `k`) |
| `chain` | variable-assignment pointer chains + distractors | length-`L` pointer follow |
| `selective_copy` | keep/drop-filtered copy | monotone sub-permutation |
| `sort_by_key` | reorder pairs by key | sort permutation |
| `kv_lastwrite` | last-write-wins over repeated keys | recency-resolved lookup |
| `multihop_map` | apply a function map `t` times | `t`-step composition |

## 3. The two separation theorems

**Theorem I — the rank bound (the provable core).**
A read-out from `H` linear-attention heads with feature dim `m` produces
`A = Σ_h D_h⁻¹ Φ_Q⁽ʰ⁾ Φ_K⁽ʰ⁾ᵀ`, so `rank(A) ≤ H·m`. The target `P_π` is
orthogonal (all singular values `= 1`). By Eckart–Young the best rank-`r`
Frobenius approximation leaves the bottom `N−r` unit values, so the relative
gather error obeys

```
    E = E_V ‖AV − P_π V‖²_F / ‖V‖²_F  ≥  1 − Hm/N  ⟶ 1   as N → ∞.
```

Softmax has no such bound (its map can be full-rank), and drives `A → P_π`,
`E → 0`. A multi-head lemma (Kronecker form on `vec(V)`) shows per-head output
projections don't rescue it: total rank `≤ H·m·d_v` vs. `N·d_v` unit values.
**This is the clean, tight, numerically exact kernel of the whole line.**

**Theorem II — the state / communication bound (the streaming view).**
Linear attention has an equivalent recurrent form with a **fixed-size state**
`Z_t ∈ ℝ^{m×d}`, independent of `N`. Specifying which value pairs with which of
`N` keys needs `≈ N·log₂N` bits at the prefix cut; the state carries only
`≈ m·(precision)` bits. Grow `N` past that and recall must fall — the same
MQAR/"Based" recall–throughput bottleneck. (Informal for deep residual stacks;
see the scope note below.)

## 4. Evidence, tier by tier

**Tier 0 — analytic / numeric (`src/numeric/`).** All CI-checked.
- Eckart–Young floor reproduced to `1e-9`; concrete rank-`m` maps sit at/above it.
- Softmax reaches the target at **logarithmic width**: at `N = 4096`, `d = 67`,
  softmax gather error `0.0000` while *any* linear head at the same width is
  pinned `≥ 0.992`.
- Depth: a product of rank-`(Hm)` maps still has rank `≤ Hm` (frozen stacks).
- A **real linear-attention head was trained** and *saturates* the `1−Hm/N`
  floor (closing an early gap where "linear" curves were constructed, not trained).

**Tier 1 — NL lift + Haiku sweep (`src/nl/`, `results/nl/`).** 27 instances,
in-session Haiku sub-agents, prompt-only, graded deterministically. Two regimes:
- **Recall-robust** (`mqar`, `chain`, `kv_lastwrite`): softmax stays flat exactly
  where fixed-state models provably need state growing with `k`.
- **High-rank output** (`gather`, `sort_by_key`, …): graceful budget-limited
  decay as `N` grows — not a fixed small-`N` floor.

**Tier 2 — trained cross-architecture separation (`src/tier3/`) — the decisive test.**
Two **identical** 2-layer residual+MLP stacks (~127K params, `d=64`), differing
**only** in the mixer (softmax vs. linear), trained from scratch on MQAR (Zoology
protocol; fresh maps every batch), eval on 2,560 fresh sequences:

| K (pairs) | softmax | linear |
|---|---|---|
| 8 | 1.000 | 0.989 |
| 16 | 1.000 | 0.972 |
| **32** | **0.999** | **0.342** |
| 64 | 0.019 | 0.013 |

**K=32 is the result**: identical params and training, softmax at ceiling, linear
holding only ~⅓ of the bindings — graceful capacity exhaustion, the fixed-state
signature (`d=64` holds ~16–20 bindings). This **empirically closes the residual-
stream loophole** (Theorem II's informal case): residual + MLP does *not* rescue
the linear mixer once `K` outgrows its state. Zero-shot pretrained pilots (Pythia
vs. Mamba vs. RWKV, 160M/410M) are *directionally* consistent — at k=8/410M
softmax scores 2.7× the Pile-matched SSM, SSM cells hit exact-0 — but
capability-limited beyond small `k`.

## 5. What was walked back (read this before trusting any single number)

The line carries an adversarial self-audit (`docs/05_self_audit.md`). The
corrections, all now reflected in the data and the console:

1. **`multihop t=32` "cliff" retracted.** The single-seed `0.00` did **not**
   replicate: `1.000 ± 0.000` over 10 fresh seeds. It was a formatting artifact.
2. **Sequence-task decay was ~2× overstated by grading.** The positional grader
   zeroes everything after one dropped line. Under an alignment-robust LCS grader
   the decay is far milder (e.g. `selective_copy` N256: `0.094` positional →
   `0.898` LCS). Both graders now ship; sequence claims use LCS.
3. **The depth argument does not cover real architectures.** The rank-product
   result holds only for *frozen, residual-free* stacks. For real residual
   models the claim rests on Theorem II (and now the Tier-2 trained result), not
   on depth-kills-rank.
4. **`K=64` is an optimization wall, not evidence.** Both mixers collapse there
   under this tiny-model recipe (softmax fails too), so no separation is claimed
   at K=64 — only at K=32.
5. **Closest prior art was initially missed:** Jelassi et al. 2024
   (arXiv:2402.01032) overlaps the central thesis and required ~1B+ models for
   pretrained separations; now cited.

**What survives cleanly:** Theorem I (tight, exact); the self-containedness
design (programmatic gold, graders 1.00 on gold, Haiku 1.00 on the base suite);
the two-regime observation (with corrected magnitudes); the generator contract
(uniqueness, reproducibility, closed-form `A*`); and the Tier-2 K=32 separation.

## 6. Falsifiable predictions (status)

- **P1** (linear read-out error `≥ 1−Hm/N`, softmax `≈ 0`) — ✅ proven + numeric.
- **P2** (trained fixed linear model saturates the output floor; argmax collapses
  as `m/N`) — ✅ tested. Caveat, proved constructively: argmax accuracy alone is
  *not* rank-limited (a rank-4 head can argmax-route any permutation while its
  *output* stays at the floor), so the separation lives in the **output metric**.
- **P3** (Haiku solves NL lifts within budget; falls only as `N`→budget) — ✅
  observed, with the grading corrections above.
- **P4** (open SSM/linear models collapse where softmax doesn't, same instances)
  — ✅ **demonstrated in task-trained form** (Tier 2, K=32); zero-shot pretrained
  directionally consistent but capability-limited.

## 7. Literature anchors

Linear/kernelized attention (Katharopoulos et al., arXiv:2006.16236); SSMs and
linear RNNs — Mamba/S4 (2312.00752), RWKV (2305.13048), RetNet (2307.08621),
Gated Linear Attention (2312.06635), Based (2402.18668); the MQAR / Zoology
associative-recall diagnostic (Arora et al., 2312.04927); the closest prior art
on recall/memory lower bounds, Jelassi et al. (2402.01032); induction heads
(2209.11895); and sparse-averaging transformers (2306.02896). Full annotations
with what-is-novel-here in `docs/03_related_work.md`.

## 8. Where everything lives

```
docs/00_research_proposal.md   question, formalization, both theorems, predictions
docs/01_task_family_spec.md    T(N,k,ρ) and members, formal
docs/02_experimental_plan.md   numeric / NL / Tier-3 protocols
docs/03_related_work.md        anchors + verified arXiv ids, novelty
docs/04_findings_generalization.md   breadth+depth findings (corrections banner)
docs/05_self_audit.md          the adversarial pass — READ THIS
docs/06_tier3_pilot.md         trained + zero-shot cross-arch, honest frontier
src/numeric/                   rank_separation, train_linear, depth_separation, …
src/nl/                        7-family generators, graders (positional+LCS), sweep
src/tier3/                     run_pilot.py (zero-shot), train_tiny.py (Zoology)
results/                       committed run outputs (numeric / nl / tier3)
tests/run_tests.py             36-check contract suite (CI-gated)
.github/workflows/research-ci.yml   suite + tolerance-based artifact-drift gate
sites/attention/  (on main)    interactive audit console (source of truth)
```

**Reproduce the spine:**
```bash
pip install numpy
python3 tests/run_tests.py                    # 36 checks: generators/graders/theorems/specs
python3 src/numeric/rank_separation.py        # analytic floor 1 − r/N
python3 src/numeric/train_linear.py           # trained head saturates the floor
python3 src/tier3/train_tiny.py               # K=32 softmax-vs-linear separation (torch)
```
The test suite proves **self-containedness end-to-end**: an independent reference
solver per family re-derives every answer from the prompt *text alone*, so the
"the optimum is in the prompt" claim is enforced by CI, not asserted.

## 9. Open frontier for follow-ups

The two clean next milestones, both GPU/recipe work rather than more CPU probing:

1. **Push the trained curve past the K=64 wall** — larger `d`, better positional
   / circuit-formation recipe, to see where softmax's *own* ceiling moves and how
   far the linear gap widens before softmax also saturates.
2. **Large-`k` pretrained separations** — 1.4B/2.8B Pile-matched pairs
   (Pythia/Mamba/RWKV), to lift the zero-shot tier from "directionally
   consistent" to error-barred curves.

Three methodological cautions, each of which cost a wrong preliminary conclusion
here: (a) zero-shot scores from ~100M models are format artifacts — check
binding vs. prior-token emission; (b) sparse supervision yields universal `1/K`
plateaus — verify supervision density before concluding "can't learn X"; (c)
learned-APE induction has trainability cliffs in sequence length — include the
standard short causal conv before comparing mixers.

*The single most important inheritance from this line is not a number — it is the
discipline: closed-form gold, two graders, fresh-seed replication, and an
adversarial self-audit that retracts its own headline cells. Build the follow-ups
the same way.*
