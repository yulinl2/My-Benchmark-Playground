# QualOracles — Lean 4 package

Machine-checks the arithmetic/algebraic core of the oracles produced by
[`harness/oracle_loop.py`](../harness/oracle_loop.py).

## Build

```bash
elan default leanprover/lean4:v4.32.1     # or: curl -sSfL https://elan.lean-lang.org/elan-init.sh | sh
lake --dir=lean build
```

Verified building on Lean **4.32.1** (`Build completed successfully`).

## Why a *two-tier* package

An oracle from a critique loop is still model output. The parts of it that are closed-form
arithmetic can be moved out of "trust me" and into a kernel. The parts that are
measure-theoretic modelling cannot — not without Mathlib — so this package refuses to
pretend otherwise:

| tier | what | status |
|---|---|---|
| **checked** | rational arithmetic + the algebraic identities the keys rest on | proved, no dependencies, builds in CI offline |
| **assumed** | that the probability model is the right one (`N` really is Geometric(9/10); the `{V=v}` preimage really has exactly two branches) | recorded as explicit `axiom Spec_*` — flagged, *not* proved |

**A green build does not mean "the oracle is correct."** It means: *given the stated
model, the numbers are right.* The modelling step stays human work — `verified` remains
`false` in the bank.

## What is actually proved

**`2024-summer-probability-q1`** (`E[N]`, `Var(N)` for the first non-zero decimal digit)
- `mean_eq : geomMean (9/10) = 10/9`
- `var_eq : geomVar (9/10) = 10/81`
- `tail_1/2/5` — the tail identity `1 - Σ_{k≤n} P(N=k) = (1/10)^n`, an *independent* route
  to the mean, checked at n = 1, 2, 5
- `near_miss_mean` / `near_miss_var_coincides` — formal record of the grading trap: the
  `{0,1,…}` parametrisation gives the **wrong mean 1/9** but the **same variance 10/81**,
  so a matching variance is not evidence the student was right

**`2023-summer-probability-q3`** (density of `V = YX`)
- `branches_equal_*` — the load-bearing identity `1 − σ(−v) = σ(v)` (substituting
  `t = eᵛ`), which is *why* the two preimage branches contribute equally and produce the
  factor 2
- `two_sigma_eq_one_plus_tanh_*` — the closed form `2σ(v) = 1 + tanh(v/2)`
- `sigma_sum_one_*` — `σ(v) + σ(−v) = 1`, the identity that makes the corrected density
  normalise to 1
- `draft_was_half` — the arithmetic witness of the defect the critic caught: the round-0
  draft integrated to **1/2**, short by exactly the missing branch

That last one is the point of the whole exercise. The round-0 draft for this problem was
**wrong** (it tracked only the `Y=+1` branch). The critique loop caught it, the revision
fixed it, and the error is now pinned in a formal statement so it cannot silently come
back.

## Next (not done)

The `Spec_*` axioms are the honest boundary. Discharging them means vendoring Mathlib
(`MeasureTheory`, `ProbabilityTheory.Distributions.Geometric`) and formalising the model
itself — real work, not a flag flip.

— 🤖 AI4StatMath review agent (Claude Code, autonomous; via @yulinl2, not Yulin)
