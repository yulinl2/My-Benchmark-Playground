## 1. Restatement

$X\sim\mathrm{Uniform}[0,1]$. Write its decimal expansion $X = 0.d_1d_2d_3\ldots$. Define
$N=\min\{k\ge 1: d_k\neq 0\}$. Find $\mathbb{E}[N]$ and $\mathrm{Var}(N)$, as two numbers.

## 2. Assumptions

- The decimal digits $d_1,d_2,\dots$ of a $\mathrm{Uniform}[0,1]$ variable are i.i.d.
  $\mathrm{Uniform}\{0,1,\dots,9\}$.
- $N$ is well defined (some digit is eventually non-zero).

## 3. Derivation

$N>k$ exactly when the first $k$ digits are all zero, i.e. $X<10^{-k}$, which has
probability $10^{-k}$. Hence
$$P(N=k)=P(N>k-1)-P(N>k)=10^{-(k-1)}-10^{-k}=\left(\tfrac{1}{10}\right)^{k-1}\cdot\tfrac{9}{10}.$$
So $N$ is Geometric **on $\{1,2,\dots\}$** ("number of trials to the first success") with
success probability $p=9/10$, success = "digit is non-zero".

For that parametrisation, $\mathbb{E}[N]=1/p$ and $\mathrm{Var}(N)=(1-p)/p^{2}$.

$$\mathbb{E}[N]=\frac{1}{9/10}=\frac{10}{9},\qquad
\mathrm{Var}(N)=\frac{1/10}{(9/10)^{2}}=\frac{1/10}{81/100}=\frac{10}{81}.$$

## 4. Final answer

$$\boxed{\ \mathbb{E}[N]=\tfrac{10}{9}\approx 1.1111\ },\qquad
\boxed{\ \mathrm{Var}(N)=\tfrac{10}{81}\approx 0.12346\ }$$

## 5. Grading criteria

Must identify $N$ as geometric **supported on $\{1,2,\dots\}$** with $p=9/10$ and produce
both values. Most likely near-miss that must NOT get credit: using the
$\{0,1,2,\dots\}$ ("failures before first success") parametrisation, giving
$\mathbb{E}=1/9$ (and the same variance $10/81$). The variance coincides, so a student
reporting $\mathbb{E}[N]=1/9$ has the wrong mean and must lose the mean credit even
though the variance matches.

## 6. Self-assessed confidence

**high.** Biggest risk it is wrong: the digit-independence claim in §2 is asserted rather
than proved.
