# A Task Distribution that Separates Softmax from Linear Attention: A Self-Contained Research Record and Handoff

**Constructive task families, two separation theorems, multi-tier model evidence, an
adversarial self-audit with published retractions, and a CI-enforced reproducibility
contract, from a six-week research line (June 22 – August 1, 2026).**

*Self-contained technical report, 2026-08-01. All quantitative claims carry receipts into
the pinned record (Appendix B); quotations from the record are verbatim and attributed;
inference is labeled as inference; counts are stated as of the pinned commits (research
branch `ddbb4b5`, `main` `82449a3`) unless dated otherwise. This document is designed to
function as a sole input for follow-up studies: §§1–9 state every load-bearing fact inline;
the repository paths resolve for byte-level audit and for re-running the instruments.*

---

## Abstract

This report is the complete record of a research line asking whether one can **construct**
long-context task distributions whose optimal attention pattern is fully determined by the
prompt (*self-contained*), yet provably unreachable by **linear / kernelized attention** at
any fixed capacity — while softmax attention realizes it. The line produced: (1) a
provable core — a rank bound via Eckart–Young giving relative gather error `≥ 1 − Hm/N`
for any `H`-head, feature-dimension-`m` linear read-out against a random permutation
target, with a multi-head Kronecker lemma, plus a communication-style fixed-state bound —
reproduced numerically to `1e-9`; (2) a seven-family instance generator whose
self-containedness is enforced by CI: independent reference solvers re-derive every answer
from prompt text alone (36-check suite, all passing at the pinned commit); (3) NL evidence
from 27 single-seed probe instances of a commercial softmax model plus a **75-run
fresh-seed replication** over 13 claim cells with dual graders; (4) a **trained
cross-architecture separation**: identical 2-layer residual stacks (~127K parameters)
differing only in the mixer, trained from scratch on multi-query recall — at K=32 pairs,
softmax 0.999 vs linear 0.342; and (5) an adversarial self-audit (15 adjudicated findings)
whose corrections are part of the result: one headline NL cell **retracted** (the
"multihop cliff" — 1.000 across 10 fresh seeds), sequence-task degradation found ~2×
overstated by a positional-grading artifact, the depth argument re-scoped to frozen
residual-free stacks, an early "trained linear" gap closed by actually training one (it
saturates the theoretical floor to `~5e-6`), and the closest prior art (Jelassi et al.,
arXiv:2402.01032) initially missed, now positioned against. The record is unusual in that
every failed claim, superseded baseline, and grading artifact is retained with receipts;
the closing contribution is the discipline itself — closed-form gold, dual graders,
fresh-seed replication, sabotage-validated checkers, and a CI gate that regenerates
numeric artifacts and fails on drift.

---

## 1. Introduction

### 1.1 The questions

- **RQ1 (construction).** Does a *generator* of long-context tasks exist — not one
  cherry-picked example — whose optimal attention map `A*(x)` is a closed-form function of
  the prompt, so that failure can never be attributed to missing knowledge?
- **RQ2 (separation).** For such tasks, is there a provable gap: linear/kernelized
  attention bounded away from the optimum at any fixed `(H, m)` budget, softmax not?
- **RQ3 (lift).** Does the numeric separation survive lifting to natural language, probed
  on a commercial softmax model?
- **RQ4 (architecture, not prompt-luck).** Does the separation appear when *identical*
  models differing only in the mixer are trained from scratch on the same distribution?

A fifth question became load-bearing in practice: **RQ0** — can the claims survive an
adversarial audit of their own graders, seeds, and write-ups, and what discipline makes the
surviving subset trustworthy?

### 1.2 Why this record is evidentially unusual

- **Closed-form ground truth everywhere.** Every task instance carries a programmatic gold
  answer and, in the numeric setting, the exact optimal attention matrix `A*`. Graders were
  verified to score 1.0 on gold (test suite §5); the commercial model scored 1.000 on all
  9 base-suite instances (`results/nl/haiku_verification.json`), establishing that the NL
  lift is solvable *before* difficulty scaling — so later degradation measures capacity,
  not task ambiguity.
- **Self-containedness is machine-enforced, not asserted.** For each of the seven
  families, an independent reference solver parses the *prompt text* and re-derives the
  answer; equality with the generator's answer key is a CI-gated test across 12 seeds per
  family (`tests/run_tests.py`, section 1).
- **Total retention including failures.** The branch retains the superseded
  sparse-supervision baseline (commit `c01bb26`), the retracted sweep cell, both graders
  (the artifact-producing one and its replacement), and the audit that indicts them
  (`docs/05_self_audit.md`) — 26 commits, June 22 → August 1
  (`git log --reverse`, receipts in §2.3).
- **Adjudicated provenance.** Commits are attributed: 21/26 authored
  `Claude <yl2021@stat.rutgers.edu>` (agent), 5/26 `yulinl2 <yulinli@bu.edu>` (principal),
  with model-lineage trailers on the agent commits — 8 × "Claude Opus 4.8 (1M context)",
  15 × "Claude Fable 5" (`git log --format=%b | grep Co-Authored-By | sort | uniq -c`).
  Work spanned multiple ephemeral sessions and containers, including parallel sessions
  whose interleaved pushes were reconciled by fetch-and-reset; the trailer census is the
  era record (threat 7, §8).

### 1.3 Contributions

1. The two-theorem separation core with exact numeric reproduction and a trained-head
   confirmation that the floor is *achieved*, not merely bounded (§3, Tier 0).
2. A seven-family self-contained task generator with dual graders and a CI contract (§2.2, §5).
3. The NL scaling evidence: a two-regime fingerprint on a commercial softmax model, with a
   75-run fresh-seed replication that both confirms the fingerprint and retracts one of its
   headline cells (§3, Tier 1; §4).
4. The trained cross-architecture result at matched parameters (§3, Tier 2) — prediction
   P4 in its task-trained form.
5. The self-audit methodology and its outcome ledger — what survived, what was corrected,
   what was withdrawn (§4) — plus the portable discipline distilled from it (§5).

### 1.4 Epistemic status — three strata

Hold the report's content in three strata and do not mix them:

- **Proven / mechanically checked:** Theorem I and its lemma; the Eckart–Young floor
  reproduced to `1e-9`; generator determinism, size honoring, and self-containedness;
  grader gold-score properties. Each is a CI-gated test at the pinned commit.
- **Case evidence** (one commercial model probed through one harness; one tiny-model
  training recipe; usable as existence proofs and effect directions, never as rates):
  every Haiku accuracy, every replication mean ± sd, every Tier-2/Tier-3 cell.
- **Case background** (context only; generalize nothing from it): repository layout, the
  interactive console, deployment history.

---

## 2. The object of study

### 2.1 The construction

**`Gather(N)`** is the canonical task. The prompt lists values `v₁…v_N` and a routing spec
naming, for each output slot `i`, a source index `π(i)`; the optimum is `Y* = P_π V` with
`P_π` the permutation matrix of `π ∼ Unif(S_N)`. The optimal read-out attention **is**
`P_π` — one bright cell per row. Seven families share the signature (formal definitions in
`docs/01_task_family_spec.md`; NL generators in `src/nl/`):

| family | routes | optimal `A*` (rank) |
|---|---|---|
| `gather` | permutation of a value stream | `P_π` (rank `N`) |
| `mqar` | k key→value pairs, k queries (Zoology diagnostic) | partial permutation (rank `k`) |
| `chain` | pointer chains among distractors | `L`-step follow |
| `selective_copy` | keep/drop-filtered copy | monotone sub-permutation |
| `sort_by_key` | reorder by numeric key | sort permutation |
| `kv_lastwrite` | last-write-wins recall | recency-resolved lookup |
| `multihop_map` | apply a map `t` times | `t`-step composition |

### 2.2 The two theorems

**Theorem I — rank bound (proved; the core).** An `H`-head linear-attention read-out with
feature dimension `m` yields `A = Σ_h D_h⁻¹ Φ_Q⁽ʰ⁾ Φ_K⁽ʰ⁾ᵀ`, `rank(A) ≤ Hm`. `P_π` is
orthogonal, so by Eckart–Young the relative gather error obeys
`E ≥ 1 − Hm/N → 1` as `N → ∞`. A multi-head lemma (operator on `vec(V)` is
`Σ_h (W_hᵀ ⊗ A_h)`, rank `≤ H·m·d_v` vs `N·d_v` unit singular values) shows per-head
output projections do not evade the bound. Softmax is unbounded in this sense and reaches
the target at **logarithmic width**: at `N = 4096`, `d = 67`, softmax gather error 0.0000
while any linear head at the same width is pinned `≥ 0.992`
(`src/numeric/softmax_logwidth.py`; statement in `docs/00_research_proposal.md` §2).

**Theorem II — fixed-state / communication bound (informal; empirically supported at
Tier 2).** Linear attention's recurrent form carries an `N`-independent state
(`O(m·d)` numbers); specifying which value binds to which of `N` keys needs `≈ N·log₂N`
bits at the prefix cut. Once `N` exceeds state capacity, recall must fall. Scope note
(post-audit): the *rank-product* depth argument covers only frozen residual-free stacks
(`src/numeric/depth_separation.py`); for real residual models the claim rests on Theorem II
— and on the Tier-2 trained result, which closes the residual-stream loophole empirically.

### 2.3 History (eras, with commit receipts)

| era | window (2026) | signal events | receipts |
|---|---|---|---|
| E0 design | Jun 22 | proposal, formalization, predictions P1–P4 | `7e5dbff` |
| E1 implementation | Jun 22 | numeric experiments + NL/Haiku base suite; external review round | `0a3879c`, `9868b38` |
| E2 generalization | Jun 27–28 | breadth (7 families) + depth + 27-instance scaling sweep; interactive console | `f403b50`, `6196628` |
| E3 audit & remediation | Jul 1–2 | adversarial self-audit (15 findings); trained linear head; LCS regrade + 75-run replication; theory re-scope | `8205bed`, `74e5198`, `c1ac009`, `76eb75d` |
| E4 cross-architecture | Jul 2 | zero-shot pilots (160M/410M); task-trained grid through two failed recipes to the decisive K=32 cell | `ba6a06d`…`f0ac266` |
| E5 hardening | Jul 5 | 36-check test suite + Research CI + tolerance drift gate (first CI run failed on last-ULP float drift; fixed) | `0a503a3`, `bb040e9` |
| E6 handoff | Aug 1 | this document | `ddbb4b5` |

---

## 3. Results by evidence tier

### Tier 0 — analytic / numeric (mechanically checked; `src/numeric/`, `results/numeric/`)

- Eckart–Young floor `1 − r/N` reproduced to `1e-9`; concrete rank-`m` maps sit at/above it
  (CI tests `num/rank`).
- Log-width softmax: `N=4096, d=67` → softmax error 0.0000, any same-width linear head
  `≥ 0.992`.
- **Trained linear head saturates the floor.** `elu+1` linear attention with `W_Q, W_K`
  trained by Adam on fresh permutations: at `(N=8, m=2)` Frobenius error² / N =
  `0.7500049` vs floor `0.75`; at `(N=16, m=2)` `0.8750023` vs `0.875`
  (`results/numeric/trained_linear.json`) — the bound is *achieved*, closing audit finding
  B1. Constructive caveat (audit): **argmax accuracy is not rank-limited** — a rank-4 head
  can argmax-route any permutation while its output error stays at the floor
  (`src/numeric/argmax_vs_output.py`); separation claims therefore live in the output
  metric, never in argmax tables.
- Depth: products of rank-`Hm` row-stochastic maps stay rank `≤ Hm` (frozen residual-free
  scope only; CI test `num/depth`).

### Tier 1 — NL lift on a commercial softmax model (case evidence; `results/nl/`)

Base suite: 9/9 instances at 1.000 (`haiku_verification.json`) — the lift is solvable
before scaling. Scaling sweep: 27 single-seed instances across the seven families
(`sweep_results.json`), showing a **two-regime fingerprint**: recall families (`mqar` to
k=128, `chain` to L=64, `kv_lastwrite` to 128 keys) essentially flat at 1.0 — exactly
where fixed-state models provably need state ∝ k — while high-rank output families
degrade with `N`.

**Fresh-seed replication** (75 runs, 13 cells, 4–10 fresh seeds each;
`sweep_replicated.json`): the two-regime fingerprint survives, with two corrections
promoted to §4. Representative cells (mean ± sd; positional / LCS graders):

| cell | n | positional | LCS |
|---|---|---|---|
| gather N64 | 4 | 0.980 ± 0.034 | 0.996 ± 0.007 |
| gather N256 | 10 | 0.545 ± 0.332 | 0.743 ± 0.182 |
| selective_copy N256 | 10 | 0.603 ± 0.272 | 0.971 ± 0.045 |
| sort_by_key N128 | 10 | 0.469 ± 0.267 | 0.930 ± 0.100 |
| multihop_map t32 | 10 | 1.000 ± 0.000 | — |
| mqar k128 | 3 | 1.000 ± 0.000 | — |

### Tier 2 — trained cross-architecture separation (case evidence; `src/tier3/`, `results/tier3/`)

Two **identical** 2-layer residual+MLP stacks (`d=64`, ~127K params, short causal conv in
both mixers per the Zoology/Based standard), differing **only** in the mixer, trained from
scratch on MQAR with fresh key→value maps every batch; eval on 2,560 fresh sequences
(`trained_tiny_mqar.json`):

| K | softmax | linear |
|---|---|---|
| 8 | 1.000 | 0.989 |
| 16 | 1.000 | 0.972 |
| **32** | **0.999** | **0.342** |
| 64 | 0.019 | 0.013 |

**K=32 is the result**: same parameters, same training — softmax at ceiling, linear
holding ~⅓ of bindings (graceful capacity exhaustion; `d=64` holds ~16–20 bindings). This
empirically closes the residual-stream loophole in Theorem II's scope. **K=64 is not
evidence**: both mixers collapse (a trainability wall of the tiny recipe — inference:
positional/circuit-formation, labeled as inference in `docs/06_tier3_pilot.md`).
Zero-shot pretrained pilots (Pythia/Mamba/RWKV at ~160M and ~400M; 38 result rows across
`pilot_recall*.json`) are directionally consistent — at k=8/410M the softmax model scores
2.7× the Pile-matched SSM (0.500 vs 0.188, n=16/cell) — but capability-limited beyond
small k; no rate claims are made from them.

---

## 4. The corrections ledger (what was walked back, verbatim-anchored)

The self-audit (`docs/05_self_audit.md`, 15 adjudicated findings) is quoted here at its
own bottom line, verbatim:

> **Bottom line.** The core rank bound (Theorem I, frozen read-out) is correct and
> numerically exact, and the two-regime sweep observation survives. But three findings
> materially change what this branch may claim: (1) no *trained* linear-attention model
> was ever run — the "linear" curves are constructed maps, so prediction P2 is untested;
> (2) the multi-layer ("depth") argument does not apply to real architectures with
> residual connections; (3) two headline sweep numbers were wrong — the `multihop t=32`
> "cliff" fails to replicate (2/2 fresh seeds correct) and the `selective_copy`
> "collapse" was a grader artifact (0.094 positional → 0.898 alignment-robust).

Disposition of each, post-remediation:

1. **Retracted:** the multihop t=32 "cliff" (single-seed 0.00). Fresh-seed status:
   1.000 ± 0.000, n=10. Cause: output-formatting artifact, not capability.
2. **Corrected ~2× overstatement:** sequence-task degradation under the positional grader
   (one dropped line zeroes all subsequent credit). Both graders now ship
   (`src/nl/grading.py`: positional + LCS); sequence claims are keyed to LCS; the
   positional numbers are retained for the record.
3. **Re-scoped:** depth-kills-rank holds only for frozen residual-free stacks; residual
   architectures are covered by Theorem II + the Tier-2 result, not by the rank product.
4. **Closed by experiment:** the missing trained linear model (finding B1) — trained, and
   it saturates the floor (§3 Tier 0). P2 was simultaneously **split**: output-metric
   claims survive; argmax-based claims are constructively invalid.
5. **Prior-art correction:** Jelassi et al. (arXiv:2402.01032) overlaps the central
   thesis and was initially uncited; now integrated (their pretrained separations required
   ~1B+ models, consistent with our zero-shot tier being capability-limited).
6. **Not evidence:** Tier-2's K=64 row (both mixers fail; recipe wall).

**What survives cleanly:** Theorem I (tight, exact); the self-containedness design; the
two-regime fingerprint with corrected magnitudes; the generator contract; the K=32 trained
separation.

---

## 5. The discipline (methodology as a portable result)

Each mechanism below exists because a specific failure class occurred; all are live at the
pinned commit:

- **Closed-form gold + solvability pre-check.** No instance enters evidence unless its
  gold is programmatic and the unscaled version is solved at 1.000 by the probe model.
- **Reference-solver self-containedness gate.** Independent parsers re-derive answers from
  prompt text alone; CI-enforced across all families and 12 seeds each
  (`tests/run_tests.py` §1 — the strongest available check that "the optimum is in the
  prompt").
- **Dual graders, artifact-aware.** Strict positional + alignment-robust LCS; the
  divergence between them is itself reported (it *is* correction #2).
- **Fresh-seed replication with disjoint seeds.** Replication seeds are verified disjoint
  from originals by a CI test (`spec: replication (task,label,seed) disjoint`).
- **Sabotage-validated checkers.** The artifact drift checker's verdict counts because it
  caught a planted fault: a mutated artifact was verified to fail (exit 1) before the
  checker entered CI (commit `bb040e9`). Its first production run also recorded a real
  instrument lesson: byte-identical comparison is the wrong contract for float artifacts
  (last-ULP libm differences between runners); the shipped check compares structurally at
  `rtol 1e-6` with text artifacts exact (`tests/check_artifact_drift.py`).
- **Regenerate, don't trust.** CI re-runs the numeric experiments and fails on drift
  between committed and regenerated artifacts (`.github/workflows/research-ci.yml`).
- **Retention of superseded work.** Failed recipes and retracted cells stay in history
  with receipts (e.g., the sparse-supervision plateau grid, `c01bb26`) — they are data.
- **Attribution as data.** Agent commits carry model-lineage trailers; the census in §1.2
  is the era record for threat 7.

---

## 6. Predictions P1–P4: status and falsifiers

- **P1** (linear read-out error `≥ 1 − Hm/N`; softmax `≈ 0`) — **proven + reproduced**.
  Falsifier: any linear read-out beating the floor at fixed `(H, m)`; if P1 fails, the
  theory is wrong (`docs/00` §8, verbatim commitment).
- **P2, split post-audit** (trained fixed linear model pinned to the *output* floor;
  CE-trained argmax collapsing as `m/N`) — **tested**: the trained head saturates the
  floor to `~5e-6`. Standing caveat: argmax alone is never evidence (constructive
  counterexample on record).
- **P3** (commercial softmax model solves NL lifts within budget; degradation only near
  budget, not at fixed small `N`) — **observed** with corrections #1–#2 applied.
  Falsifier stated ex-ante: failure at small `N` on a self-contained spec indicts the
  generator, not the model.
- **P4** (fixed-state architectures collapse where softmax does not, same distribution) —
  **demonstrated in task-trained form** at K=32; zero-shot pretrained tier directionally
  consistent, capability-limited. Open falsifier for follow-ups: a linear-mixer recipe
  matching softmax at K=32 under matched parameters and training would overturn the
  Tier-2 reading.

---

## 7. Related work (ids verified in-record)

Linear/kernelized attention: Katharopoulos et al. (arXiv:2006.16236). Fixed-state model
families: Mamba/S4 (2312.00752), RWKV (2305.13048), RetNet (2307.08621), Gated Linear
Attention (2312.06635), Based (2402.18668). The MQAR/Zoology recall diagnostic: Arora et
al. (2312.04927). **Closest prior art:** Jelassi et al. (2402.01032) — recall/memory
lower bounds and pretrained-model separations; this line's distinct contributions are the
closed-form-`A*` self-contained construction, the commercial-model NL lift with
replication-and-retraction discipline, and the matched-parameter trained separation at
127K params. Mechanistic anchor: induction heads (2209.11895). Expressivity kin:
sparse-averaging transformers (2306.02896). Annotated versions: `docs/03_related_work.md`.

---

## 8. Threats to validity

1. **Single probe model, single harness.** All NL rates come from one commercial softmax
   model driven as in-session sub-agents; harness defaults (sampling, context handling)
   are unmeasured confounders. No cross-vendor replication exists yet.
2. **Small n.** Replication cells are n=4–10 (mqar k128: n=3); all means are directions,
   not coefficients. The 27-instance sweep is single-seed and retained only as the
   hypothesis-generating record.
3. **Grader degrees of freedom.** The positional→LCS correction was itself a choice; both
   graders ship precisely so a skeptic can re-key every claim to either.
4. **Tier-2 is one training run per cell.** Eval n=2,560 makes per-cell eval error small,
   but training-run variance is unmeasured (no seed replication of the grid); K=32 rests
   on a single (d=64, 1500-step) recipe. The K=64 wall bounds the recipe, not the theory.
5. **Self-measurement.** Generators, graders, tests, and this report share an author
   lineage (agent sessions; §1.2 census). The reference solvers are independent *code
   paths* but not independent *authors*; sabotage validation was executed for the drift
   checker only. External re-derivation is the designed remedy (Appendix B).
6. **Contamination surface.** The generator logic and instances are public at the console
   URL (noindex + crawler-blocked, but URL-reachable). Fresh seeds regenerate unseen
   instances, and self-containedness blunts memorization, but format familiarity for
   future models cannot be excluded; treat future-model results on *published seeds* as
   contaminated.
7. **Era and session effects.** The record spans multiple ephemeral sessions, containers,
   and model eras (trailer census: 8 Opus-4.8-era, 15 Fable-5-era agent commits), with
   parallel sessions reconciled by fetch-and-reset. Commit trailers are the only in-band
   era stamps; unrecorded divergence between parallel working states cannot be fully
   excluded, though final states were push-serialized through one remote.
8. **Zero-shot tier capability floor.** n=16/cell and ~400M-max scale make the pretrained
   pilots directional only; they cannot show "softmax flat in k" where no mixer can do
   the task.

---

## 9. Open problems (the follow-up charter)

**Compute-bound (GPU work, not more CPU probing):**
1. Push the trained grid past the K=64 recipe wall (larger `d`, better positional/
   circuit-formation recipe) — locate softmax's own ceiling and the gap's growth curve.
2. Seed-replicate the Tier-2 grid (threat 4) to put error bars on 0.999 vs 0.342.
3. Pretrained separations at 1.4B/2.8B matched pairs (lift the zero-shot tier from
   directional to error-barred).

**Design-bound:**
4. Cross-vendor NL replication (threat 1) with the same emit/grade harness.
5. Attention-map realizability measurement on real models (the construction supplies
   `A*`; nothing yet compares a real model's attention to it directly).
6. Promotion rules for the two-regime fingerprint from case evidence to an error-barred
   claim.

**Methodological cautions inherited from the record** (each cost one wrong preliminary
conclusion): zero-shot scores from ~100M models are format artifacts — check binding vs
prior-token emission; sparse supervision yields universal `1/K` plateaus — verify
supervision density before concluding "can't learn X"; learned-APE induction has
trainability cliffs in sequence length — include the standard short causal conv before
comparing mixers.

---

## Appendix A — glossary

**Self-contained task** — the target `y*(x)` and optimal attention `A*(x)` are
deterministic functions of the prompt; failure cannot be attributed to missing knowledge.
**Gather(N) / MQAR(N,k)** — §2.1 canonical tasks. **Rank floor** — the Eckart–Young bound
`E ≥ 1 − Hm/N` (Theorem I). **Fixed-state view** — linear attention as a recurrence with
`N`-independent state (Theorem II). **Positional / LCS graders** — strict-order vs
alignment-robust sequence scoring; their divergence measures the grading artifact.
**Fresh-seed replication** — re-running claim cells on seeds disjoint (CI-verified) from
the originals. **Drift gate** — CI step that regenerates numeric artifacts and fails on
out-of-tolerance divergence from committed copies. **Sabotage validation** — a checker's
verdict counts only after it has caught a planted fault. **Era** — a contiguous span of
commits under one generating process (§2.3); model lineage is recorded in commit
trailers. **Output vs argmax metric** — Frobenius-type output error (rank-limited) vs
routing argmax accuracy (provably not rank-limited); claims key to the former.

## Appendix B — data availability and verification

All coordinates are the record's own. Repository: `yulinl2/My-Benchmark-Playground`
(private). Pinned commits: research branch `claude/long-context-task-distribution-2iydu1`
@ `ddbb4b5` (this document's home; PR #9 targets
`research/long-context-attention-expressivity-separation`); `main` @ `82449a3` (console
source of truth under `sites/attention/`, deployed to
<https://yulinl2.github.io/My-Benchmark-Playground/attention/> — noindex,
crawler-blocked, URL-reachable; see threat 6).

| stratum | paths |
|---|---|
| theory & protocol | `docs/00`–`03` |
| findings & audit | `docs/04`, `docs/05_self_audit.md` (15 findings), `docs/06_tier3_pilot.md` |
| numeric code + artifacts | `src/numeric/` → `results/numeric/` (incl. `trained_linear.json`) |
| NL harness + artifacts | `src/nl/` → `results/nl/` (base suite 9 rows; sweep 27 rows; replication 75 rows / 13 cells; raw responses committed) |
| cross-architecture | `src/tier3/` → `results/tier3/` (trained grid 8 rows; zero-shot pilots 38 rows) |
| contract suite + CI | `tests/run_tests.py` (36 checks), `tests/check_artifact_drift.py`, `.github/workflows/research-ci.yml` |

**Verification (machine-checkable, from a clean checkout of `ddbb4b5`):**

```bash
pip install numpy
python3 tests/run_tests.py                 # 36 checks; exit 0 expected
python3 src/numeric/rank_separation.py     # regenerates the floor artifact
python3 src/numeric/depth_separation.py
python3 tests/check_artifact_drift.py \
  results/numeric/rank_separation.json results/numeric/rank_separation.json
# negative control for the checker itself: mutate any field of a copy and
# re-run — it must exit 1 (this was executed before the checker entered CI;
# receipt: commit message of bb040e9).
python3 src/tier3/train_tiny.py            # Tier-2 grid (torch; ~CPU-hours)
```

Provenance of this report: written by an agent session in the lineage described in §1.2
(trailer-recorded), from the pinned record, with every quantitative claim re-derived from
the artifact files at writing time (2026-08-01) rather than carried from earlier drafts;
by the record's own discipline (§5), that provenance is stated here as data, not asserted
as authority.
