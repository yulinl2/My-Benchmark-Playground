## 1. Restatement

$X$ on $[-1,1]$ with symmetric density $f$; $Y\in\{\pm1\}$ with
$P(Y=1\mid X=x)=\sigma(x)=\frac{1}{1+e^{-x}}$. Find the density of $V=YX$.

## 2. Assumptions

- $f$ is a density on $[-1,1]$ with $f(-x)=f(x)$.
- $Y$'s dependence on $X$ is fully specified by $\sigma$.
- Note $[-1,1]$ is symmetric about $0$, so $v\in[-1,1]\iff -v\in[-1,1]$: **both** preimage
  branches stay inside the support.

## 3. Derivation

**(Revised: the previous version tracked only one branch.)** For $v\in[-1,1]$, the event
$\{V=v\}=\{YX=v\}$ decomposes into two *disjoint* routes:
$$\{Y=+1,\ X=v\}\quad\text{and}\quad\{Y=-1,\ X=-v\}.$$
Hence
$$f_V(v)=f(v)\,P(Y=1\mid X=v)\;+\;f(-v)\,P(Y=-1\mid X=-v).$$

Now the key simplification:
$$P(Y=-1\mid X=-v)=1-\sigma(-v)=1-\frac{1}{1+e^{v}}=\frac{e^{v}}{1+e^{v}}
=\frac{1}{1+e^{-v}}=\sigma(v).$$
So *both* conditional factors equal $\sigma(v)$, and by symmetry $f(-v)=f(v)$:
$$f_V(v)=f(v)\sigma(v)+f(v)\sigma(v)=2f(v)\,\sigma(v)=\frac{2f(v)}{1+e^{-v}}.$$

**Normalisation check (the test the first draft failed).** Using $\sigma(v)+\sigma(-v)=1$
and symmetry of $f$,
$$\int_{-1}^{1}2f(v)\sigma(v)\,dv=\int_{-1}^{1}f(v)\big[\sigma(v)+\sigma(-v)\big]dv
=\int_{-1}^{1}f(v)\,dv=1\ \checkmark$$

**Qualitative claim, now derived.** $2\sigma(v)>1\iff v>0$, so the tilt genuinely moves
mass to positive $v$; and $f_V(v)+f_V(-v)=2f(v)[\sigma(v)+\sigma(-v)]=2f(v)$, i.e. the
*symmetrised* law of $V$ returns the law of $X$ — a useful sanity identity.

## 4. Final answer

$$\boxed{\ f_V(v)=2f(v)\,\sigma(v)=\frac{2f(v)}{1+e^{-v}},\qquad v\in[-1,1].\ }$$

Equivalently $f_V(v)=f(v)\big(1+\tanh(v/2)\big)$.

## 5. Grading criteria

Must (i) decompose $\{V=v\}$ into **both** branches, (ii) use
$1-\sigma(-v)=\sigma(v)$ together with symmetry of $f$, (iii) land on $2f(v)\sigma(v)$.
**Near-misses that must NOT get credit:** $f(v)\sigma(v)$ (one branch only — integrates to
$1/2$); $f_V=f$ (ignores the tilt entirely). A student who writes the two-branch formula
but does not simplify $1-\sigma(-v)=\sigma(v)$ may still receive most credit if the
expression is correct.

## 6. Self-assessed confidence

**high.** Two independent checks pass: normalisation to exactly 1, and the symmetrisation
identity $f_V(v)+f_V(-v)=2f(v)$.

## Response to review

- **Defect 1 (high, missing branch) — FIXED.** Both preimages are now carried; this was a
  genuine error in the draft, not a presentational gap.
- **Defect 2 (high, integrates to 1/2) — FIXED and adopted as a standing check.** The
  corrected density integrates to exactly 1; the reviewer's factor-2 diagnosis was right.
- **Defect 3 (medium, unjustified intuition) — FIXED.** The tilt claim is now derived from
  $2\sigma(v)\gtrless1$ rather than asserted.
- The reviewer's independent answer $2f(v)\sigma(v)$ agrees with this revision.
