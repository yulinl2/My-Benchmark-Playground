# Solution: 2021-summer-math-stat-q2

## Setup and notation

Write $y = (y_1,\dots,y_n)^T$, $x = (x_1,\dots,x_n)^T$ (known constants), and $\mathbf 1 = (1,\dots,1)^T$. The model is
$$
y \sim N_n(\beta x,\ \Sigma), \qquad \Sigma = \sigma^2\big[(1-\rho)I_n + \rho\,\mathbf 1\mathbf 1^T\big].
$$
Indeed $\operatorname{var}(y_i)=\sigma^2$ and $\operatorname{cov}(y_i,y_j)=\sigma^2\rho$ for $i\neq j$, so the correlation matrix is the **equicorrelation (compound symmetry)** matrix
$$
R(\rho) = (1-\rho)I_n + \rho\,\mathbf 1\mathbf 1^T .
$$

**Eigenstructure of $R$.** $R$ acts on $\operatorname{span}(\mathbf 1)$ by $R\mathbf 1 = (1-\rho + n\rho)\mathbf 1$, and on $\mathbf 1^\perp$ as $(1-\rho)I$. Hence its eigenvalues are
$$
\lambda_1 = 1 + (n-1)\rho \quad(\text{eigenvector }\mathbf 1),\qquad \lambda_2 = 1-\rho \quad(\text{multiplicity }n-1).
$$
The constraint $-\tfrac1{n-1} < \rho < 1$ is exactly the condition that **both** eigenvalues are strictly positive, i.e. that $\Sigma$ is positive definite (a valid covariance). Also
$$
\det R = (1-\rho)^{n-1}\big(1+(n-1)\rho\big).
$$

**Inverse of $R$.** Write $R = (1-\rho)\big(I + b\,\mathbf 1\mathbf 1^T\big)$ with $b = \rho/(1-\rho)$. By the stated linear-algebra fact (a Sherman–Morrison rank-one update) with $a=\mathbf 1$, $a^Ta=n$,
$$
(I + b\,\mathbf 1\mathbf 1^T)^{-1} = I + c\,\mathbf 1\mathbf 1^T,\qquad c = -\frac{b}{1+bn} = -\frac{\rho}{1+(n-1)\rho}.
$$
Therefore
$$
\boxed{\;R^{-1} = \frac{1}{1-\rho}\Big(I_n - \frac{\rho}{1+(n-1)\rho}\,\mathbf 1\mathbf 1^T\Big),\qquad \Sigma^{-1} = \frac1{\sigma^2}R^{-1}.\;}
$$

A convenient orthogonal decomposition of any vector $v\in\mathbb R^n$: let $\bar v = \tfrac1n\sum v_i$, so $v = \bar v\,\mathbf 1 + (v-\bar v\mathbf 1)$ with the two pieces $R$-orthogonal. Then
$$
v^T R^{-1} v = \frac{1}{1-\rho}\sum_{i}(v_i-\bar v)^2 + \frac{n}{1+(n-1)\rho}\,\bar v^2 ,
\tag{$\star$}
$$
because $\sum(v_i-\bar v)^2 = \|v-\bar v\mathbf 1\|^2$ lies in $\mathbf 1^\perp$ (eigenvalue $1-\rho$ of $R$) and $\bar v\mathbf 1$ lies along $\mathbf 1$ (eigenvalue $1+(n-1)\rho$). Identity $(\star)$ is used repeatedly below.

---

## Part 1 — MVUE of $\beta$ among linear estimators ($\rho$ known, $\beta,\sigma^2$ unknown)

We seek $\hat\beta = a^T y$ that is unbiased for $\beta$ for all $(\beta,\sigma^2)$ and has minimum variance.

**Unbiasedness.** $\mathbb E[a^Ty] = \beta\,a^Tx$. This equals $\beta$ for all $\beta$ iff
$$
a^T x = 1. \tag{1}
$$
Such $a$ exists iff $x\neq 0$. (If $x=0$ then $\mathbb E(y)=0$ identically, no unbiased estimator of $\beta$ exists — see the degenerate remark below. Assume $x\neq 0$.)

**Variance.** $\operatorname{var}(a^Ty) = a^T\Sigma a = \sigma^2\,a^T R\, a$. Since $\sigma^2>0$ is a positive multiplier independent of $a$, minimizing variance is equivalent to minimizing $a^T R\, a$ subject to $(1)$, **and the minimizer does not depend on the unknown $\sigma^2$** — so a uniformly best (minimum variance for every $\sigma^2$ simultaneously) linear unbiased estimator exists.

**Constrained minimization (Lagrange / GLS).** Minimize $a^T R a$ s.t. $a^Tx=1$. Lagrangian $a^TRa - 2\mu(a^Tx-1)$; stationarity gives $Ra = \mu x$, i.e. $a = \mu R^{-1}x$. Imposing $(1)$: $\mu\, x^TR^{-1}x = 1$, so $\mu = (x^TR^{-1}x)^{-1}$ (note $x^TR^{-1}x>0$ since $x\neq0$ and $R^{-1}\succ0$). Hence
$$
\boxed{\;a^\star = \frac{R^{-1}x}{x^TR^{-1}x},\qquad \hat\beta = \frac{x^T R^{-1} y}{x^T R^{-1} x}.\;}
$$
This is the **generalized least squares (Aitken) estimator**, and $R^{-1}$ may be replaced by the explicit form above (the scalar $1/(1-\rho)$ cancels between numerator and denominator). Its variance is
$$
\operatorname{var}(\hat\beta) = \sigma^2\,a^{\star T}Ra^\star = \frac{\sigma^2}{x^TR^{-1}x}.
$$

**Why this is the MVUE among linear estimators.** This is the **Gauss–Markov / Aitken theorem**: among linear unbiased estimators of $\beta$, the GLS estimator has minimum variance. Direct verification: any unbiased $a = a^\star + d$ must satisfy $d^Tx=0$ (from $(1)$). Then
$$
a^TRa = a^{\star T}Ra^\star + 2\,a^{\star T}Rd + d^TRd.
$$
The cross term vanishes: $a^{\star T}Rd = \mu\,x^T R^{-1}R d = \mu\,x^Td = 0$. Since $d^TRd\ge 0$ (with equality iff $d=0$ as $R\succ0$),
$$
a^TRa \ge a^{\star T}Ra^\star,
$$
with equality iff $a=a^\star$. So $\hat\beta$ is the unique linear MVUE, for every $\sigma^2$. $\qquad\blacksquare$

**Explicit form.** Using $(\star)$-type algebra, $x^TR^{-1}y = \frac1{1-\rho}\Big[\sum_i(x_i-\bar x)(y_i-\bar y) + \frac{1-\rho}{1+(n-1)\rho}\,n\bar x\bar y\Big]$, etc. (Closed form is the displayed boxed ratio.)

**Remark.** Existence requires $x\neq 0$. If $x=0$, no linear (indeed no) unbiased estimator of $\beta$ exists, since the distribution of $y$ does not depend on $\beta$.

---

## Part 2 — MLE of $(\sigma^2,\rho)$ ($\beta$ known, $\sigma^2,\rho$ unknown)

With $\beta$ known, set the residual $e = y - \beta x$, so $e \sim N_n(0,\ \sigma^2 R(\rho))$. The log-likelihood is
$$
\ell(\sigma^2,\rho) = -\frac n2\log(2\pi) - \frac n2\log\sigma^2 - \frac12\log\det R - \frac{1}{2\sigma^2}\,e^TR^{-1}e .
$$
Using the eigen-decomposition, introduce the two quadratic forms
$$
A = \sum_{i=1}^n (e_i-\bar e)^2 = \|e-\bar e\mathbf 1\|^2 \quad(\ge 0),\qquad B = n\bar e^2 = \frac1n\Big(\sum_i e_i\Big)^2\quad(\ge0),
$$
where $\bar e = \tfrac1n\sum e_i$. By $(\star)$,
$$
e^TR^{-1}e = \frac{A}{1-\rho} + \frac{B}{1+(n-1)\rho},
$$
and $\log\det R = (n-1)\log(1-\rho) + \log\big(1+(n-1)\rho\big)$. Thus
$$
\ell = \text{const} - \frac n2\log\sigma^2 - \frac{n-1}{2}\log(1-\rho) - \frac12\log\big(1+(n-1)\rho\big) - \frac{1}{2\sigma^2}\Big(\frac{A}{1-\rho}+\frac{B}{1+(n-1)\rho}\Big).
$$

**Reparametrize via the eigenvalues.** Let
$$
\theta_1 = \sigma^2(1-\rho) \;(\text{the }\mathbf 1^\perp\text{-variance}),\qquad \theta_2 = \sigma^2\big(1+(n-1)\rho\big)\;(\text{the }\mathbf 1\text{-variance}).
$$
These are exactly the (distinct) eigenvalues of $\Sigma$, with multiplicities $n-1$ and $1$. The map $(\sigma^2,\rho)\mapsto(\theta_1,\theta_2)$ is a bijection from $\{\sigma^2>0,\ -\frac1{n-1}<\rho<1\}$ onto $\{\theta_1>0,\ \theta_2>0\}$ (inverse: $\sigma^2 = \frac{(n-1)\theta_1+\theta_2}{n}$, $\rho = \frac{\theta_2-\theta_1}{(n-1)\theta_1+\theta_2}$). In these coordinates the likelihood **separates**:
$$
\ell = \text{const} - \frac{n-1}{2}\log\theta_1 - \frac{A}{2\theta_1} \;-\; \frac12\log\theta_2 - \frac{B}{2\theta_2}.
$$
Each piece is a one-parameter normal-variance log-likelihood. Maximizing $-\tfrac k2\log\theta - \tfrac S2/\theta$ over $\theta>0$ gives $\hat\theta = S/k$ (set derivative $-\tfrac{k}{2\theta}+\tfrac{S}{2\theta^2}=0$; second derivative negative, so it is the unique global max provided $S>0$). Hence
$$
\hat\theta_1 = \frac{A}{n-1},\qquad \hat\theta_2 = B = n\bar e^2 .
$$

**Back-transform.** Using $\sigma^2 = \frac{(n-1)\theta_1+\theta_2}{n}$ and $\rho = \frac{\theta_2-\theta_1}{(n-1)\theta_1+\theta_2}$,
$$
\boxed{\;\widehat{\sigma^2} = \frac{A + B}{n} = \frac1n\sum_{i=1}^n (y_i-\beta x_i)^2,\qquad
\hat\rho = \frac{B - \tfrac{A}{n-1}}{A+B}.\;}
$$
(The clean form $\widehat{\sigma^2} = \frac1n\sum e_i^2$ follows since $A+B = \sum(e_i-\bar e)^2 + n\bar e^2 = \sum e_i^2$.) Equivalently, writing $s^2 = \tfrac1{n}\sum e_i^2 = \widehat{\sigma^2}$,
$$
\hat\rho = \frac{n\bar e^2 - \frac1{n-1}\sum(e_i-\bar e)^2}{\sum e_i^2}.
$$

**Justification it is the MLE.** Because the reparametrization is a smooth bijection of the parameter space, the MLE is invariant under it (functional invariance of MLE), and the separated objective is the sum of two concave functions each with a unique interior maximizer, so the joint maximizer is unique and global. We must check it lands in the interior, i.e. $\hat\theta_1>0$ and $\hat\theta_2>0$ (equivalently $-\tfrac1{n-1}<\hat\rho<1$ and $\widehat{\sigma^2}>0$):

- $\hat\theta_2 = B = n\bar e^2 > 0$ a.s. (zero only on the measure-zero event $\bar e=0$).
- $\hat\theta_1 = A/(n-1) > 0$ a.s. (zero only when all $e_i$ equal).

So with probability one the MLE exists, is unique, and is given by the boxed formulas. (On the boundary events one eigenvalue-variance estimate hits $0$; these have probability $0$.) $\qquad\blacksquare$

---

## Part 3 — All of $(\beta,\sigma^2,\rho)$ unknown

### 3(a) Minimal sufficient statistic and completeness

The density of $y$ is
$$
f(y;\beta,\sigma^2,\rho) = (2\pi)^{-n/2}(\det\Sigma)^{-1/2}\exp\!\Big[-\tfrac12 (y-\beta x)^T\Sigma^{-1}(y-\beta x)\Big].
$$
Using the projection $P = \tfrac1n\mathbf 1\mathbf 1^T$ onto $\operatorname{span}(\mathbf 1)$ and $Q=I-P$, and writing $\theta_1=\sigma^2(1-\rho)$, $\theta_2=\sigma^2(1+(n-1)\rho)$ as in Part 2,
$$
(y-\beta x)^T\Sigma^{-1}(y-\beta x) = \frac{1}{\theta_1}\,(y-\beta x)^TQ(y-\beta x) + \frac{1}{\theta_2}\,(y-\beta x)^TP(y-\beta x).
$$
Expand each quadratic in $\beta$. With $\langle u,v\rangle_Q = u^TQv$ and $\langle u,v\rangle_P = u^TPv$:
$$
(y-\beta x)^TQ(y-\beta x) = y^TQy - 2\beta\, x^TQy + \beta^2 x^TQx,
$$
and similarly with $P$. Hence the exponent is a linear combination of the statistics
$$
T = \big(\;y^TQy,\quad y^TPy,\quad x^TQ y,\quad x^TP y\;\big),
$$
with coefficients depending on $(\beta,\sigma^2,\rho)$. Concretely the exponent equals
$$
-\frac{1}{2\theta_1}\big[y^TQy - 2\beta x^TQy + \beta^2 x^TQx\big]-\frac{1}{2\theta_2}\big[y^TPy - 2\beta x^TPy + \beta^2 x^TPx\big],
$$
so this is a **curved exponential family** of order (at most) 4 with natural statistics $T$ and parameter-dependent canonical parameters $\big(\tfrac{1}{\theta_1},\tfrac{1}{\theta_2},\tfrac{\beta}{\theta_1},\tfrac{\beta}{\theta_2}\big)$ (the terms in $\beta^2$ contribute only to the normalizing/quadratic-in-data-free part).

**Minimal sufficient statistic.** By the standard exponential-family / ratio criterion (Lehmann–Scheffé), a minimal sufficient statistic is obtained from the set of statistics that multiply algebraically independent functions of the parameter in the exponent. Provided $x$ is **not** proportional to $\mathbf 1$ and is **not** orthogonal to $\mathbf 1$ (the generic case, so that both $x^TQ$ and $x^TP$ are nonzero and the four canonical functions are not redundant), the minimal sufficient statistic is
$$
\boxed{\;T = \Big(\, y^TQy,\; y^TPy,\; x^TQy,\; x^TPy \,\Big)\;}
$$
equivalently $\big(\sum_i(y_i-\bar y)^2,\ \bar y,\ \sum_i (x_i-\bar x)(y_i-\bar y),\ \bar x\bar y\big)$ up to one-to-one transformation. (When $x$ is special — proportional to or orthogonal to $\mathbf 1$ — some coordinates of $T$ become constants/redundant and $T$ collapses; see below.)

**Minimality (sketch).** Form the likelihood ratio $f(y;\eta)/f(z;\eta)$ for two data points $y,z$. It is constant in $\eta=(\beta,\sigma^2,\rho)$ iff $y$ and $z$ give the same value of every statistic whose multiplier ranges over a set rich enough to separate them — i.e. iff $T(y)=T(z)$. The four canonical functions $\tfrac1{\theta_1},\tfrac1{\theta_2},\tfrac\beta{\theta_1},\tfrac\beta{\theta_2}$ span a set whose linear hull, as $(\beta,\sigma^2,\rho)$ vary, has affine dimension equal to the number of non-redundant coordinates of $T$; this yields $T$ as minimal sufficient by Lehmann–Scheffé.

**Completeness.** This is a *curved* exponential family: the natural parameter $\eta(\beta,\sigma^2,\rho)=\big(\tfrac1{\theta_1},\tfrac1{\theta_2},\tfrac\beta{\theta_1},\tfrac\beta{\theta_2}\big)$ lives on a $3$-dimensional manifold inside $\mathbb R^4$, not an open subset of $\mathbb R^4$. A minimal sufficient statistic of a curved family is generally **not complete** because of an internal functional relationship; completeness holds only when the model is actually a *full-rank* (regular) exponential family of dimension equal to that of $T$, i.e. when the dimension of $T$ drops to $3$ and the parameter map is onto an open set.

The relationship that can cause incompleteness: note $\dfrac{\beta/\theta_1}{1/\theta_1} = \dfrac{\beta/\theta_2}{1/\theta_2} = \beta$, i.e. the two "linear" canonical parameters are tied to the two "quadratic" ones by the **same** $\beta$. This forces a deterministic constraint among the components of an unbiased-estimator construction unless one of $x^TQ$, $x^TP$ vanishes.

Carrying this out, the **necessary and sufficient condition for the minimal sufficient statistic to be complete** is that $x$ be orthogonal to $\mathbf 1$ **or** $x$ be proportional to $\mathbf 1$ — i.e.
$$
\boxed{\;x^TP x \cdot x^TQ x = 0 \iff \bar x = 0 \ \ (\textstyle\sum_i x_i = 0)\quad\text{or}\quad x_1=\cdots=x_n.\;}
$$
In these two cases the family reduces to a full-rank exponential family in $3$ statistics with the canonical parameter ranging over an open subset of $\mathbb R^3$, so $T$ is complete; otherwise (generic $x$ with $\bar x\neq0$ and not all $x_i$ equal) the family is genuinely curved and $T$ is **not** complete.

*Reasoning for the two complete cases.*
- If $x_1=\cdots=x_n=k$ (so $x=k\mathbf 1$): then $Qx=0$, $x^TQy = k\,\mathbf 1^TQy/\!\!\!=0$ in fact $x^TQy = k\,\mathbf 1^TQ y = 0$ since $Q\mathbf 1=0$. The mean lies entirely in $\operatorname{span}(\mathbf 1)$. The statistic collapses to $T=(y^TQy,\ y^TPy,\ \bar y)$ with three free canonical parameters $\big(\tfrac1{\theta_1},\tfrac1{\theta_2},\tfrac{\beta}{\theta_2}\big)$ varying over an open set ⇒ full rank ⇒ complete.
- If $\sum x_i=0$ (so $Px=0$, $\bar x=0$): then $x^TPy=0$, and $T=(y^TQy,\ y^TPy,\ x^TQy)$ with free canonical parameters $\big(\tfrac1{\theta_1},\tfrac1{\theta_2},\tfrac{\beta}{\theta_1}\big)$ over an open set ⇒ full rank ⇒ complete.

In the generic case both $x^TQy$ and $x^TPy$ survive, the model is curved (3-dim parameter, 4-dim statistic), and one can build a nonzero function of $T$ with zero expectation for all parameters (e.g. exploiting that the same $\beta$ controls both linear terms), so $T$ is not complete.

### 3(b) MLE of $(\beta,\sigma^2,\rho)$ in the two special cases

The profile log-likelihood: for fixed $(\sigma^2,\rho)$ the MLE of $\beta$ is the GLS estimator from Part 1 (with $R^{-1}$),
$$
\hat\beta(\rho) = \frac{x^TR^{-1}y}{x^TR^{-1}x}.
$$
Then substitute and, exactly as in Part 2, the residual $\hat e = y - \hat\beta(\rho)x$ yields $\widehat{\sigma^2},\hat\rho$ via the eigenvalue-variance estimates. We treat the two cases.

#### Case (i): $x_1=\cdots=x_n$, say $x=k\mathbf 1$ with $k\neq0$.

Here the mean is $\beta x = (\beta k)\mathbf 1$, lying entirely in $\operatorname{span}(\mathbf 1)$; only the product $\beta k$ is identified, and $\beta=(\text{mean})/k$. The GLS estimator: since $x\propto\mathbf 1$ and $\mathbf 1$ is an eigenvector of $R$, $R^{-1}x = \frac{1}{1+(n-1)\rho}x$ (the scalar cancels), giving
$$
\hat\beta = \frac{x^TR^{-1}y}{x^TR^{-1}x} = \frac{x^Ty}{x^Tx} = \frac{k\sum y_i}{k^2 n} = \frac{\bar y}{k}.
$$
This is independent of $\rho$. The residual is $\hat e = y - \hat\beta x = y - \bar y\mathbf 1$, so $\bar{\hat e}=0$, i.e. the $P$-component $B = n\bar{\hat e}^2 = 0$ identically. From Part 2's eigenvalue estimates, $\hat\theta_2 = B = 0$ — the estimate of the $\mathbf 1$-direction variance is forced to $0$, which lies on the **boundary** $\theta_2>0$ (equivalently $\rho\to 1$). Therefore:

$$
\boxed{\;\hat\beta = \frac{\bar y}{k}=\frac{\sum y_i}{\sum x_i},\qquad \widehat{\sigma^2}\,\text{ and }\hat\rho\ \text{do not have an interior MLE: it does not exist.}\;}
$$

**Why it fails.** All information about the $\mathbf 1$-direction is consumed by estimating the mean ($\hat\beta$ exactly fits $\bar y$), leaving zero residual along $\mathbf 1$. The likelihood in $\theta_2=\sigma^2(1+(n-1)\rho)$ is then $-\tfrac12\log\theta_2 - 0/(2\theta_2)$, which increases without bound as $\theta_2\to 0^+$ ($-\tfrac12\log\theta_2\to+\infty$). So the supremum is attained only on the boundary $\rho\to 1$ (or $\sigma^2\to0$ with the other piece compensating), and **no MLE exists** in the open parameter space for $(\sigma^2,\rho)$. Only $\hat\beta=\bar y/k$ is well defined.

(More precisely: $\hat\theta_1 = A/(n-1)=\frac{1}{n-1}\sum(y_i-\bar y)^2>0$ is fine, but $\hat\theta_2\to0$ drives the likelihood to $+\infty$, so the joint MLE of $(\sigma^2,\rho)$ does not exist.)

#### Case (ii): $x_1+\cdots+x_n=0$, i.e. $\bar x=0$ (and $x\neq0$, not all equal since they sum to zero but are nonzero).

Here $Px=0$ ($x\perp\mathbf 1$), so $x$ lies entirely in $\mathbf 1^\perp$. Then $R^{-1}x = \frac{1}{1-\rho}x$ (since $x\in\mathbf 1^\perp$ is in the $(1-\rho)$-eigenspace), and the scalar cancels:
$$
\hat\beta = \frac{x^TR^{-1}y}{x^TR^{-1}x} = \frac{x^Ty}{x^Tx} = \frac{\sum_i x_i y_i}{\sum_i x_i^2},
$$
the **ordinary least squares** slope, independent of $\rho$. The residual is $\hat e = y - \hat\beta x$. Note $\bar{\hat e} = \bar y - \hat\beta\bar x = \bar y$ (since $\bar x=0$), so the $P$-component is preserved: $B = n\bar{\hat e}^2 = n\bar y^2$, generally $>0$. The $Q$-component: $A = \sum(\hat e_i - \bar{\hat e})^2 = \sum_i\big((y_i-\bar y) - \hat\beta(x_i-\bar x)\big)^2 = \sum_i\big((y_i-\bar y) - \hat\beta x_i\big)^2$ (using $\bar x=0$), the residual sum of squares about the fitted line, $>0$ a.s.

Both eigenvalue-variances are positive a.s., so the MLE exists in the interior. By Part 2's formulas with these $\hat e$:
$$
\hat\theta_1 = \frac{A}{n-1},\qquad \hat\theta_2 = B = n\bar y^2,
$$
$$
\boxed{\;
\hat\beta = \frac{\sum_i x_i y_i}{\sum_i x_i^2},\qquad
\widehat{\sigma^2} = \frac{A+B}{n} = \frac1n\sum_{i=1}^n (y_i-\hat\beta x_i)^2,\qquad
\hat\rho = \frac{B - \frac{A}{n-1}}{A+B},
\;}
$$
where $A = \sum_i (y_i-\bar y - \hat\beta x_i)^2$ and $B = n\bar y^2$.

**Justification.** With $\bar x=0$ the model is the *complete* full-rank exponential family from 3(a): the statistic $x^TPy$ vanishes, the parameter map is onto an open set, the log-likelihood is (after the $\theta_1,\theta_2$ reparametrization) strictly concave in each block, and the stationary point above is the unique interior global maximizer (same argument as Part 2, plus the GLS/concavity argument for $\beta$). Existence holds with probability one (need $A>0$ and $B>0$). Hence the MLE exists and is given by the boxed formulas.

---

## Summary of final answers

**Part 1.** With $x\neq0$, the linear MVUE (uniformly in $\sigma^2$) is the GLS estimator
$$
\hat\beta = \frac{x^TR^{-1}y}{x^TR^{-1}x},\qquad \operatorname{var}(\hat\beta)=\frac{\sigma^2}{x^TR^{-1}x},\quad R^{-1}=\tfrac1{1-\rho}\big(I-\tfrac{\rho}{1+(n-1)\rho}\mathbf 1\mathbf 1^T\big).
$$
It exists iff $x\neq0$; optimality is the Gauss–Markov/Aitken theorem.

**Part 2.** With $e=y-\beta x$, $A=\sum(e_i-\bar e)^2$, $B=n\bar e^2$:
$$
\widehat{\sigma^2}=\frac{A+B}{n}=\frac1n\sum(y_i-\beta x_i)^2,\qquad \hat\rho = \frac{B-\frac{A}{n-1}}{A+B}.
$$
Obtained by reparametrizing to the eigenvalue-variances $\theta_1=\sigma^2(1-\rho),\ \theta_2=\sigma^2(1+(n-1)\rho)$, where the likelihood separates into two normal-variance problems; MLE by invariance and concavity; exists a.s.

**Part 3(a).** Minimal sufficient statistic $T=(y^TQy,\ y^TPy,\ x^TQy,\ x^TPy)$ (curved exponential family). $T$ is complete **iff** $\sum_i x_i=0$ or $x_1=\cdots=x_n$ (equivalently $x^TPx\cdot x^TQx=0$); otherwise the family is curved and $T$ is not complete.

**Part 3(b).**
- (i) $x_i\equiv k$: $\hat\beta=\bar y/k=\sum y_i/\sum x_i$, but the MLE of $(\sigma^2,\rho)$ **does not exist** — the residual along $\mathbf 1$ is identically zero, driving $\theta_2\to0$ ($\rho\to1$) and the likelihood to $+\infty$.
- (ii) $\sum x_i=0$: MLE exists,
$$
\hat\beta=\frac{\sum x_iy_i}{\sum x_i^2}\ (\text{OLS}),\quad \widehat{\sigma^2}=\frac1n\sum(y_i-\hat\beta x_i)^2,\quad \hat\rho=\frac{B-\frac{A}{n-1}}{A+B},
$$
with $A=\sum(y_i-\bar y-\hat\beta x_i)^2$, $B=n\bar y^2$.
