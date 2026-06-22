# Experimental Plan

Three tiers, increasing in realism and cost. Tiers 1–2 run here (numpy, in-session
sub-agents). Tier 3 (open SSM checkpoints on GPU) is specified as the next
milestone.

---

## Tier 1 — Numeric, analytic + trained (no external models)

### 1a. Analytic rank separation — `src/numeric/rank_separation.py`
Directly evaluates Theorem I. For a random permutation `P_π (N×N)`:
- compute the best rank-`r` Frobenius approximation error (Eckart–Young) for
  `r = Hm`, confirming relative error `= 1 − r/N`;
- contrast with a softmax map whose logits are `β·P_π`, showing error `→ 0` as
  the temperature sharpens.

**Pass criterion:** measured linear-floor matches `1 − Hm/N` to numerical
precision; softmax error decays toward 0 with `β`.

### 1b. Trained heads — `src/numeric/train.py`
End-to-end train a single softmax head and a single linear-attention head (with
learnable `W_Q, W_K` and feature dim `m`) on `Gather(N)` drawn fresh each step.
- Sweep `N ∈ {8, 16, 32, 64}` at fixed `m`.
- Report gather MSE / exact-match accuracy vs. `N`.

**Predicted result (P1, P2):** softmax accuracy ≈ 1 across `N`; linear accuracy
collapses once `N > m`, tracking the `1 − m/N` floor.

---

## Tier 2 — NL lift on commercial softmax model (Haiku) via in-session sub-agents

**Purpose (see proposal §7):** *self-containedness audit* + *difficulty
fingerprint*. This does **not** test linear attention (no commercial linear
model exists); it confirms the NL tasks are genuinely solvable from the prompt by
a random-access (softmax) model, which is the precondition for the separation to
be meaningful, and characterizes how softmax degrades (context-budget-limited,
not rank-limited).

### Protocol
1. `src/nl/task_generator.py` emits NL instances with a hidden answer key for
   `task ∈ {gather, mqar, chain}` at several difficulties.
2. For each instance, spawn a **Haiku sub-agent** (Max-plan covered, in-session)
   as the *solver*. The solver receives only the prompt text (no tools, no web),
   and must return the answer in a strict format.
3. A deterministic grader (`src/nl/grading.py`) compares against the key.
4. Aggregate accuracy vs. difficulty into `results/nl/*.json`.

### Sub-agent harness (how it is actually invoked here)
The orchestrator (this session) calls the `Agent` tool with `subagent_type` set
to a Haiku-backed solver, one call per instance (batched in parallel where
possible), passing a prompt of the exact shape:

```
You are a careful solver. Use ONLY the information in the PROMPT below.
Do not use outside knowledge. Return your answer between <answer>…</answer>.

PROMPT:
<the generated NL instance>
```

The orchestrator records each returned `<answer>` and grades it. Results captured
in this branch live in `results/nl/`. `src/nl/run_haiku_verification.py`
documents the exact instances used and provides the offline grader so runs are
reproducible; the live model calls are driven by the orchestrator's `Agent` tool
rather than an API key in the script (keeps secrets out of the repo).

### Pass criteria
- **Self-containedness:** Haiku ≥ 95% on small `N` (e.g. `gather N=8`,
  `mqar k=4`, `chain L=3`). If not, the generator is buggy (ambiguous instance)
  — fix before trusting anything else.
- **Fingerprint:** accuracy stays high until `N`/`k` is large relative to context
  budget, then declines — qualitatively distinct from a fixed small-`N` floor.

---

## Tier 3 — Cross-architecture separation (next milestone, GPU)

Run the *same generated instances* through open checkpoints:
- **Softmax baselines:** Pythia / Llama-class small models.
- **Linear / SSM:** RWKV, Mamba, RetNet, Based, GLA.

Plot accuracy vs. `N` (gather), `k` (mqar), `L_chain` (chain). Prediction P4:
SSM/linear curves collapse with the difficulty knob on instances where softmax
stays flat, at matched parameter count. Requires GPU + `transformers`; tracked as
the decisive empirical test.

---

## Threats to validity & controls
- **Tokenization confounds (NL):** keep symbols single-token where possible;
  report with multiple surface renderings.
- **Positional-encoding crutches:** randomize the mapping between position and
  pointer so the model cannot exploit a trivial offset.
- **Memorization:** draw `π`/keys fresh per instance from a space far larger than
  any training set (`N!`), per the overfit-vs-generalize corollary.
- **Prompt-format luck:** average over ≥3 surface templates per task.
