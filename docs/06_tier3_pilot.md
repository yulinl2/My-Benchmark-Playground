# Tier 3 (CPU pilot): Cross-Architecture Separation on Pretrained & Task-Trained Models

The decisive experiment of the program — softmax vs fixed-state architectures on
the same self-contained recall task — run at CPU scale in this container.
Three evidence tiers, weakest → strongest. Code: `src/tier3/`; data:
`results/tier3/*.json`.

**Design principle.** All pretrained comparisons use Pile-trained model pairs at
matched scale (Pythia vs Mamba vs RWKV), so *architecture is the only variable*.
The task is associative recall in completion form: k facts
(`The password for {city} is {word}.`), then the verbatim query prefix; greedy
exact-match. Two value formats: 3-char codes (multi-token) and common words
verified single-token in NeoX BPE (copying = 1 token → recall is the only
bottleneck).

---

## Tier A — zero-shot, ~150M (pythia-160m / mamba-130m / rwkv-4-169m)

| k | pythia-160m (codes/words) | mamba-130m | rwkv-169m |
|---|---|---|---|
| 4 | 0.33 / 0.33 | 0.58 / 0.33 | 0.08 / 0.08 |
| 8 | 0.21 / 0.08 | 0.21 / 0.17 | 0.08 / 0.00 |
| 16 | 0.13 / 0.08 | 0.17 / 0.08 | 0.00 / 0.00 |
| 32 | 0.04 / 0.04 | **0.000 / 0.000** | 0.00 / 0.00 |
| 64 | 0.08 / 0.08 | **0.000 / 0.000** | 0.00 / 0.00 |

**Error-mode diagnostic** (pythia-160m, k=16, words): of 24 completions, 17 were
plausible words *not in the list* ("gold", "wood"), 5 were another city's value,
and the model emitted one fixed value ("olive") for several different queries.
It follows the *format* perfectly but performs **no binding at all** — the
scores at this tier are mostly degenerate-prior luck.

**Lesson A (methodological):** zero-shot prompting cannot elicit in-context
recall at the 100M tier from ANY of the three architectures; evals here measure
format-following, not retrieval. Single-token values did not help → the floor
is capability, not tokenization.

**Lesson A′ (theory-consistent detail):** the fixed-state models are the only
ones printing *exact-0.000* cells at k ≥ 32 (mamba, both formats), while
softmax retains a small nonzero tail — the saturation signature visible even
through the capability floor.

## Tier B — zero-shot, ~400M (pythia-410m / mamba-370m, words)

| k | pythia-410m | mamba-370m |
|---|---|---|
| 8 | **0.500** | 0.188 |
| 16 | 0.062 | 0.062 |
| 32 | 0.062 | **0.000** |
| 64 | 0.062 | 0.062 |

**Lesson B:** binding *emerges with scale*, and the moment it exists the
ordering is architecture-shaped: at k=8 softmax scores 2.7× the Pile-matched
SSM. Beyond k=16 both floor out zero-shot — consistent with Jelassi et al.
(arXiv:2402.01032), whose pretrained separations required ~1B+ models. The
zero-shot tier is therefore *directionally consistent with P4 but
capability-limited*: it cannot show softmax "flat in k" because pretrained
models this small cannot do the task at large k under any mixer.

## Tier C — task-trained tiny models (the Zoology protocol) — decisive

Identical 2-layer residual stacks (embeddings, LayerNorm, MLP, residual
stream; ~125k params) differing ONLY in the sequence mixer — softmax attention
vs elu+1 linear attention — trained from scratch on synthetic MQAR with a
**fresh random key→value map every batch** (nothing memorizable; retrieval is
the only solution), then evaluated on 2,560 fresh sequences. `train_tiny.py`.

Because these are *residual* stacks trained end-to-end, this tier also
empirically probes the audit-A2 gap: the frozen rank-product argument does not
cover residual architectures, but Theorem II (fixed state) predicts the linear
mixer still caps when K outgrows its state.

> **Status: run in progress** (`results/tier3/trained_tiny_mqar.json` pending —
> a container restart killed the first run; relaunched). Table to be inserted
> on completion.

---

## Verdict so far

- **P4, zero-shot form:** partially supported — architecture-ordered where
  capability exists (Tier B, k=8), fixed-state exact-zero saturation observed
  (both scales), but full "softmax flat" curves need ≥1B models (GPU tier) or
  task training (Tier C).
- **Methodological export:** benchmark scores at the 100M zero-shot tier are
  format artifacts; error-mode analysis (binding vs prior-emission) should
  accompany any small-model recall claim.
- The **GPU milestone** remains for large-k pretrained curves (1.4B/2.8B
  pairs), but the CPU pilot has already produced the qualitative signature the
  theory predicts.
