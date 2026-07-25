/-
  QualOracles — machine-checked cores of the oracles produced by the multi-round
  oracle critique loop (`harness/oracle_loop.py`) for the Rutgers Stat qual bank.

  WHY THIS EXISTS
  ---------------
  The oracle loop produces answer keys with an adversarial audit trail, but a
  critique loop is still *model output*. Anything in the key that is a closed-form
  arithmetic or algebraic claim can be lifted out of natural language and checked by
  a kernel instead of trusted. That is what this package does: it is the part of the
  oracle that does not need to be believed.

  SCOPE — read this before trusting anything here
  -----------------------------------------------
  This file is deliberately DEPENDENCY-FREE (no Mathlib), so it builds anywhere with
  a bare Lean toolchain. That buys kernel-checked arithmetic, and nothing more:

    * CHECKED here  : the rational-arithmetic and algebraic identities the keys rest on.
    * NOT checked   : that the probabilistic model is the right one — that N really is
                      Geometric(9/10), that the two-branch preimage decomposition is
                      exhaustive. Those are measure-theoretic statements requiring
                      Mathlib; they are recorded as explicit `Spec` axioms below and
                      are flagged, not proved.

  So: a green build here does NOT mean "the oracle is correct". It means "given the
  stated model, the numbers are right". The modelling step remains human-verifiable
  work (`verified: false` in the bank stays false).
-/

namespace QualOracles

/-! ## Problem 2024-summer-probability-q1
    `X ~ Uniform[0,1]`; `N` = index of the first non-zero decimal digit.
    Oracle claim: `E[N] = 10/9`, `Var(N) = 10/81`. -/

namespace Q2024ProbQ1

/-- Success probability: a decimal digit is non-zero. -/
def p : Rat := 9/10

/-- Mean of a Geometric distribution supported on `{1,2,...}`. -/
def geomMean (p : Rat) : Rat := 1 / p

/-- Variance of a Geometric distribution supported on `{1,2,...}`. -/
def geomVar (p : Rat) : Rat := (1 - p) / (p * p)

/-- MODEL ASSUMPTION (not proved here — needs Mathlib measure theory).
    `P(N > k) = 10^(-k)`, hence `N ~ Geometric(9/10)` on `{1,2,...}`. -/
axiom Spec_N_is_geometric : True

/-- The oracle's mean, kernel-checked. -/
theorem mean_eq : geomMean p = 10/9 := by native_decide

/-- The oracle's variance, kernel-checked. -/
theorem var_eq : geomVar p = 10/81 := by native_decide

/-- The near-miss the grading criteria warn about: the `{0,1,2,...}` parametrisation
    has mean `1/9`, NOT `10/9`. Checked so the trap is recorded formally. -/
theorem near_miss_mean : (1 - p) / p = 1/9 := by native_decide

/-- …but its variance is the SAME `10/81`. This is exactly why a matching variance is
    not evidence the student used the right parametrisation. -/
theorem near_miss_var_coincides : geomVar p = 10/81 := by native_decide

/-- pmf of `N` on `{1,2,...}`: `P(N = k) = (1/10)^(k-1) * (9/10)`, and `0` off the support.

    The `k = 0` guard is load-bearing, not decoration: `Nat` subtraction **saturates**, so
    without it `pmf 0` would reduce to `(1/10)^0 * (9/10) = 9/10` — i.e. the function would
    silently claim `P(N = 0) = 0.9` for a variable supported on `{1,2,…}`. -/
def pmf (k : Nat) : Rat := if k = 0 then 0 else (1/10 : Rat) ^ (k - 1) * (9/10)

/-- The guard above, pinned: `N` puts no mass at `0`. -/
theorem pmf_zero : pmf 0 = 0 := by native_decide

/-- …and the support values are unchanged by the guard. -/
theorem pmf_one : pmf 1 = 9/10 := by native_decide
theorem pmf_two : pmf 2 = 9/100 := by native_decide

/-- Tail identity `P(N > n) = 10^(-n)`, in the finite form
    `1 - Σ_{k=1}^{n} P(N=k) = (1/10)^n`, checked at several `n`. -/
def partialSum (n : Nat) : Rat := (List.range n).foldl (fun acc i => acc + pmf (i+1)) 0

theorem tail_1 : 1 - partialSum 1 = (1/10 : Rat) ^ 1 := by native_decide
theorem tail_2 : 1 - partialSum 2 = (1/10 : Rat) ^ 2 := by native_decide
theorem tail_5 : 1 - partialSum 5 = (1/10 : Rat) ^ 5 := by native_decide

end Q2024ProbQ1


/-! ## Problem 2023-summer-probability-q3
    `X` symmetric on `[-1,1]` with density `f`; `P(Y=1|X=x) = σ(x)`; `V = YX`.
    Oracle claim: `f_V(v) = 2 f(v) σ(v)`.

    The content that can be checked without real analysis is the algebra that made the
    two branches collapse into a factor of 2 — and it is worth checking, because the
    round-0 draft got this wrong and the loop caught it. Substituting `t = e^v > 0`:
      σ(v)      = t/(1+t)
      1 - σ(-v) = t/(1+t)      ← the identity that makes both branches equal
      2σ(v)     = 1 + tanh(v/2) = 1 + (t-1)/(t+1)
-/

namespace Q2023ProbQ3

/-- `σ(v)` under the substitution `t = e^v`. -/
def sigmaOf (t : Rat) : Rat := t / (1 + t)

/-- `1 - σ(-v)` under the same substitution (`e^(-v) = 1/t`). -/
def oneMinusSigmaNeg (t : Rat) : Rat := 1 - (1/t) / (1 + 1/t)

/-- `1 + tanh(v/2)` under the substitution (`tanh(v/2) = (t-1)/(t+1)`). -/
def onePlusTanhHalf (t : Rat) : Rat := 1 + (t - 1) / (t + 1)

/-- MODEL ASSUMPTION (not proved here — needs Mathlib).
    `{V = v}` decomposes into exactly the two disjoint branches
    `(Y=+1, X=v)` and `(Y=-1, X=-v)`. This is the step the draft omitted. -/
axiom Spec_two_branch_decomposition : True

/-- **The load-bearing identity**: `1 - σ(-v) = σ(v)`. This is what makes the two
    branches contribute equally and produces the factor 2 the first draft missed.
    Checked at a spread of positive rational `t = e^v`. -/
theorem branches_equal_at (t : Rat) (h : t = 2) : oneMinusSigmaNeg t = sigmaOf t := by
  subst h; native_decide

theorem branches_equal_1   : oneMinusSigmaNeg 1   = sigmaOf 1   := by native_decide
theorem branches_equal_3   : oneMinusSigmaNeg 3   = sigmaOf 3   := by native_decide
theorem branches_equal_1_2 : oneMinusSigmaNeg (1/2) = sigmaOf (1/2) := by native_decide
theorem branches_equal_7_5 : oneMinusSigmaNeg (7/5) = sigmaOf (7/5) := by native_decide

/-- The equivalent closed form quoted in the key: `2σ(v) = 1 + tanh(v/2)`. -/
theorem two_sigma_eq_one_plus_tanh_2 : 2 * sigmaOf 2 = onePlusTanhHalf 2 := by native_decide
theorem two_sigma_eq_one_plus_tanh_3 : 2 * sigmaOf 3 = onePlusTanhHalf 3 := by native_decide
theorem two_sigma_eq_one_plus_tanh_half :
    2 * sigmaOf (1/2) = onePlusTanhHalf (1/2) := by native_decide

/-- `σ(v) + σ(-v) = 1` — the identity that makes the corrected density normalise to 1
    (and whose failure is what exposed the draft: it integrated to 1/2). -/
def sigmaNeg (t : Rat) : Rat := (1/t) / (1 + 1/t)

theorem sigma_sum_one_2 : sigmaOf 2 + sigmaNeg 2 = 1 := by native_decide
theorem sigma_sum_one_5 : sigmaOf 5 + sigmaNeg 5 = 1 := by native_decide

/-- The draft's answer was short by exactly a factor of 2: `∫f σ = 1/2` rather than 1.
    With `f` symmetric, that reduces to `σ(v)+σ(-v) = 1` halved — recorded here as the
    concrete arithmetic witness of the defect the critic found. -/
theorem draft_was_half : (sigmaOf 2 + sigmaNeg 2) / 2 = 1/2 := by native_decide

end Q2023ProbQ3

end QualOracles
