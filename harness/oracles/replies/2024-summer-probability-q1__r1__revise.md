## 1. Restatement

$X\sim\mathrm{Uniform}[0,1]$, $X=0.d_1d_2d_3\ldots$, $N=\min\{k\ge1:d_k\neq0\}$.
Find $\mathbb{E}[N]$ and $\mathrm{Var}(N)$.

## 2. Assumptions

- Only uniformity of $X$ on $[0,1]$ is used. **(Revised: the i.i.d.-digit claim is no
  longer assumed; it is now a remark, not a load-bearing step.)**
- $\{X=0\}$ and the countable set of numbers with two decimal expansions
  (e.g. $0.1=0.0999\ldots$) are Lebesgue-null, so $N$ is **almost surely** well defined
  and the law of $N$ is unaffected by the convention chosen on that null set.

## 3. Derivation

The first $k$ digits are all zero **iff** $X<10^{-k}$. Therefore, directly from uniformity
and with no appeal to digit independence,
$$P(N>k)=P(X<10^{-k})=10^{-k},\qquad k\ge 0 .$$
Hence
$$P(N=k)=P(N>k-1)-P(N>k)=10^{-(k-1)}-10^{-k}=\Big(\tfrac{1}{10}\Big)^{k-1}\tfrac{9}{10},
\quad k=1,2,\dots$$
so $N\sim\mathrm{Geometric}(p=9/10)$ **supported on $\{1,2,\dots\}$**.

*Remark (not needed above).* One can also see this by noting the digits are i.i.d.
uniform on $\{0,\dots,9\}$; the tail computation is preferred because it is self-contained.

Using the $\{1,2,\dots\}$ parametrisation, $\mathbb{E}[N]=1/p$, $\mathrm{Var}(N)=(1-p)/p^2$:
$$\mathbb{E}[N]=\frac{10}{9},\qquad
\mathrm{Var}(N)=\frac{1/10}{81/100}=\frac{10}{81}.$$

*Independent check (tail sum).* $\mathbb{E}[N]=\sum_{k\ge0}P(N>k)=\sum_{k\ge0}10^{-k}
=\frac{1}{1-1/10}=\frac{10}{9}$ ✓.

## 4. Final answer

$$\boxed{\ \mathbb{E}[N]=\tfrac{10}{9}\approx 1.1111\ },\qquad
\boxed{\ \mathrm{Var}(N)=\tfrac{10}{81}\approx 0.12346\ }$$

## 5. Grading criteria

Must identify the geometric law on $\{1,2,\dots\}$ with $p=9/10$ and give both values.
**Near-miss that must NOT get full credit:** the $\{0,1,\dots\}$ parametrisation yields
$\mathbb{E}=1/9$ with the *same* variance $10/81$ — so a matching variance is not evidence
the student was right; the mean must be checked separately.

## 6. Self-assessed confidence

**high.** The result is now supported by two independent derivations (tail identity and
geometric formula) that agree.

## Response to review

- **Defect 1 (medium, unproved i.i.d. digits) — FIXED.** The derivation now runs off
  $P(N>k)=P(X<10^{-k})=10^{-k}$, which uses only uniformity. Digit independence is demoted
  to a remark and carries no weight.
- **Defect 2 (low, null sets) — FIXED.** $\{X=0\}$ and the ambiguous-expansion set are
  explicitly declared Lebesgue-null and a.s.-irrelevant.
- The reviewer's independent answer agrees with the key; no numerical change was required.
