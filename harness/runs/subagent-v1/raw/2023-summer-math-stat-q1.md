# Problem 1 — Linear model: Neyman–Pearson power, Bernstein–von Mises, ridge limit

**Model.** $Y = X\theta + \varepsilon$, $X \in \mathbb{R}^{n\times p}$ (treated as fixed/known design), $\theta \in \mathbb{R}^p$ unknown, $\varepsilon \sim N(0, I_n)$. Thus $Y \sim N(X\theta, I_n)$, with known unit error variance. The density of $Y$ at parameter $\theta$ is
$$
f_\theta(y) = (2\pi)^{-n/2}\exp\!\Big(-\tfrac12 \|y - X\theta\|^2\Big).
$$

---

## Part 1. Maximal power of a level-$\alpha$ test for $H_0:\theta=\theta_0$ vs $H_1:\theta=\theta_1$

Both hypotheses are **simple**, so by the **Neyman–Pearson Lemma** the test maximizing power among all level-$\alpha$ tests is the likelihood-ratio test that rejects for large values of $f_{\theta_1}(Y)/f_{\theta_0}(Y)$. We compute that maximal power explicitly.

### The likelihood ratio is a single linear statistic

$$
\log\frac{f_{\theta_1}(Y)}{f_{\theta_0}(Y)}
= -\tfrac12\|Y - X\theta_1\|^2 + \tfrac12\|Y - X\theta_0\|^2 .
$$
Expanding the squares, the quadratic term $\|Y\|^2$ cancels:
$$
\log\frac{f_{\theta_1}(Y)}{f_{\theta_0}(Y)}
= Y^\top X(\theta_1-\theta_0) - \tfrac12\big(\|X\theta_1\|^2 - \|X\theta_0\|^2\big).
$$
Hence the LR is a strictly increasing function of the **scalar linear statistic**
$$
T := (\theta_1-\theta_0)^\top X^\top Y = \langle X(\theta_1-\theta_0),\, Y\rangle .
$$
Rejecting for large LR is equivalent to rejecting for large $T$. Write
$$
\delta := X(\theta_1-\theta_0)\in\mathbb{R}^n, \qquad
d^2 := \|\delta\|^2 = (\theta_1-\theta_0)^\top X^\top X (\theta_1-\theta_0).
$$
$d$ is the **(non-centrality / separation) distance** between the two mean vectors.

### Distribution of $T$ under each hypothesis

$T = \delta^\top Y$ is a linear functional of a Gaussian vector, hence Gaussian, with variance $\operatorname{Var}(T)=\delta^\top I_n \delta = d^2$ under both hypotheses. Its mean:
- Under $H_0$ ($EY = X\theta_0$): $\ \mathbb{E}_0 T = \delta^\top X\theta_0$.
- Under $H_1$ ($EY = X\theta_1$): $\ \mathbb{E}_1 T = \delta^\top X\theta_1 = \mathbb{E}_0 T + \delta^\top X(\theta_1-\theta_0) = \mathbb{E}_0 T + d^2.$

So $T \sim N(\mu_0, d^2)$ under $H_0$ and $T \sim N(\mu_0 + d^2, d^2)$ under $H_1$, where $\mu_0=\delta^\top X\theta_0$. The means differ by exactly $d^2$, the variance is $d^2$, so in standardized units the two distributions are separated by $d^2/d = d$ standard deviations.

### The optimal test and its power

**Degenerate case $d=0$** (i.e. $X\theta_0 = X\theta_1$): the two distributions of $Y$ are identical, the hypotheses are indistinguishable, and no test beats its size; the maximal power equals $\alpha$.

**Case $d>0$.** The most powerful level-$\alpha$ test rejects when $T > c$, with $c$ chosen so the size is $\alpha$:
$$
\mathbb{P}_0(T > c) = \alpha
\ \Longrightarrow\
c = \mu_0 + d\, z_{1-\alpha},
$$
where $z_{1-\alpha}=\Phi^{-1}(1-\alpha)$ and $\Phi$ is the standard normal CDF. (No randomization is needed since $T$ is continuous.) The power is
$$
\beta = \mathbb{P}_1(T>c)
= \mathbb{P}_1\!\left(\frac{T-(\mu_0+d^2)}{d} > \frac{c-(\mu_0+d^2)}{d}\right)
= \mathbb{P}\!\left(Z > z_{1-\alpha} - d\right),
$$
since $\dfrac{c-(\mu_0+d^2)}{d} = \dfrac{d z_{1-\alpha} - d^2}{d} = z_{1-\alpha}-d$. Therefore

$$
\boxed{\;\beta_{\max} \;=\; \Phi\!\big(d - z_{1-\alpha}\big)
\;=\; \Phi\!\Big(\sqrt{(\theta_1-\theta_0)^\top X^\top X (\theta_1-\theta_0)}\; -\; z_{1-\alpha}\Big)\;}
$$

where $d=\|X(\theta_1-\theta_0)\| = \big[(\theta_1-\theta_0)^\top X^\top X(\theta_1-\theta_0)\big]^{1/2}$.

**Sanity checks.** As $d\to 0$, $\beta_{\max}\to \Phi(-z_{1-\alpha}) = \alpha$ (consistent with the degenerate case). As $d\to\infty$, $\beta_{\max}\to 1$. Power is increasing in the design separation $d$ and decreasing in $z_{1-\alpha}$ (i.e. decreasing in stringency, since smaller $\alpha$ means larger $z_{1-\alpha}$). If the error variance were a known $\sigma^2$ rather than $1$, replace $d$ by $d/\sigma$.

---

## Part 2. Bernstein–von Mises and the ridge (posterior-mean) limit

Prior: $\theta \sim N(0,\Lambda)$, $\Lambda \succ 0$ (nonsingular). Likelihood $Y\mid\theta \sim N(X\theta, I_n)$.

### Exact (Gaussian conjugate) posterior

The log-posterior is, up to an additive constant in $\theta$,
$$
\log \Pi(\theta\mid Y) = -\tfrac12\|Y-X\theta\|^2 - \tfrac12\theta^\top\Lambda^{-1}\theta + \text{const}.
$$
Collecting quadratic and linear terms in $\theta$:
$$
-\tfrac12\,\theta^\top\big(X^\top X + \Lambda^{-1}\big)\theta + \theta^\top X^\top Y + \text{const}.
$$
This is the log of a Gaussian. By Gaussian–Gaussian conjugacy the posterior is exactly
$$
\boxed{\;\theta \mid Y \sim N(\mu_n, \Sigma_n),\qquad
\Sigma_n = \big(X^\top X + \Lambda^{-1}\big)^{-1},\qquad
\mu_n = \Sigma_n X^\top Y.\;}
\tag{$\ast$}
$$
This exact form drives both subparts.

---

### Part 2(a). Direct proof of a Bernstein–von Mises theorem

**Assumptions.** $p$ fixed; $\frac1n X^\top X \to \Sigma$ as $n\to\infty$ with $\Sigma \succ 0$ (positive definite). The data are generated under a fixed true parameter $\theta^\star$ (frequentist truth), so $Y = X\theta^\star + \varepsilon$, $\varepsilon\sim N(0,I_n)$. Let $\hat\theta_n = (X^\top X)^{-1}X^\top Y$ denote the MLE (= OLS estimator; $X^\top X$ is invertible for large $n$ since $\frac1n X^\top X\to\Sigma\succ0$).

**Goal (BvM).** The posterior, recentered at the MLE and rescaled by $\sqrt n$, converges to a *fixed* Gaussian that does not depend on the prior, and matches the sampling distribution of the MLE. Concretely, let $h := \sqrt n(\theta-\hat\theta_n)$ be the local parameter under the posterior. We show
$$
\big\| \,\Pi\big(\sqrt n(\theta - \hat\theta_n)\in \cdot \mid Y\big) - N\!\big(0,\ \Sigma^{-1}\big)\,\big\|_{TV} \xrightarrow{\ \mathbb{P}\ } 0,
$$
i.e. the rescaled posterior converges in total variation, in probability, to $N(0,\Sigma^{-1})$ — the inverse Fisher information per observation. (The Fisher information of one "averaged" observation is $\Sigma$; for the whole sample it is $X^\top X \approx n\Sigma$.)

**Proof.** Because everything is exactly Gaussian, we can prove the statement by directly controlling the mean and covariance of the posterior, then invoking that two Gaussians with vanishing parameter differences have vanishing total-variation distance.

*Step 1: Posterior of the local parameter.* From $(\ast)$, $\theta\mid Y \sim N(\mu_n,\Sigma_n)$. Under the affine map $\theta \mapsto h=\sqrt n(\theta - \hat\theta_n)$, the conditional law of $h$ given $Y$ is Gaussian:
$$
h \mid Y \sim N\big(m_n,\ V_n\big),\qquad
m_n = \sqrt n(\mu_n - \hat\theta_n),\qquad
V_n = n\,\Sigma_n .
$$

*Step 2: Covariance converges.* 
$$
V_n = n\big(X^\top X + \Lambda^{-1}\big)^{-1}
= \Big(\tfrac1n X^\top X + \tfrac1n\Lambda^{-1}\Big)^{-1}.
$$
Since $\frac1n X^\top X \to \Sigma$ and $\frac1n \Lambda^{-1}\to 0$ (here $\Lambda$ is fixed), the inside converges to $\Sigma$, and by continuity of matrix inversion at the invertible matrix $\Sigma$,
$$
V_n \longrightarrow \Sigma^{-1}.
$$
(This is deterministic given the design.)

*Step 3: Mean converges to $0$ in probability.* Using $\mu_n = \Sigma_n X^\top Y$ and $\hat\theta_n=(X^\top X)^{-1}X^\top Y$, write $A_n := X^\top X$, $B_n := A_n+\Lambda^{-1}=\Sigma_n^{-1}$. Then
$$
\mu_n - \hat\theta_n = B_n^{-1}X^\top Y - A_n^{-1}X^\top Y
= \big(B_n^{-1} - A_n^{-1}\big)X^\top Y .
$$
Use the identity $B_n^{-1}-A_n^{-1} = -B_n^{-1}(B_n - A_n)A_n^{-1} = -B_n^{-1}\Lambda^{-1}A_n^{-1}$. Also $A_n^{-1}X^\top Y = \hat\theta_n$. Hence
$$
\mu_n - \hat\theta_n = -B_n^{-1}\Lambda^{-1}\hat\theta_n,
\qquad
m_n = \sqrt n(\mu_n-\hat\theta_n) = -\sqrt n\, B_n^{-1}\Lambda^{-1}\hat\theta_n .
$$
Now $\sqrt n\,B_n^{-1} = \big(\frac1n B_n\big)^{-1}/\sqrt n = \big(\frac1n X^\top X + \frac1n\Lambda^{-1}\big)^{-1}/\sqrt n \to \Sigma^{-1}\cdot 0 = 0$ (the bracket $\to\Sigma^{-1}=O(1)$, divided by $\sqrt n\to\infty$). And $\hat\theta_n \xrightarrow{\mathbb P}\theta^\star$ (consistency of OLS: $\hat\theta_n = \theta^\star + A_n^{-1}X^\top\varepsilon$, with $\operatorname{Var}(\hat\theta_n)=A_n^{-1}\to 0$ since $A_n^{-1}\approx \frac1n\Sigma^{-1}$; while $\Lambda^{-1}$ is a fixed matrix). Therefore
$$
m_n = -\big(\sqrt n B_n^{-1}\big)\,\Lambda^{-1}\,\hat\theta_n \xrightarrow{\ \mathbb P\ } 0\cdot \Lambda^{-1}\cdot\theta^\star = 0 .
$$

*Step 4: From parameter convergence to total-variation convergence.* The total-variation distance between $N(m_n,V_n)$ and $N(0,\Sigma^{-1})$ is a continuous function of $(m_n,V_n)$ that vanishes when $(m_n,V_n)=(0,\Sigma^{-1})$ (two Gaussians coincide in TV iff equal parameters; and TV is continuous in the parameters for nondegenerate Gaussians — e.g. via Pinsker's inequality and the closed-form Gaussian KL). Since $V_n\to\Sigma^{-1}\succ0$ deterministically and $m_n\xrightarrow{\mathbb P}0$, the continuous-mapping theorem gives
$$
\big\|N(m_n,V_n) - N(0,\Sigma^{-1})\big\|_{TV}\xrightarrow{\ \mathbb P\ }0 .
$$
This is exactly the claimed convergence of the posterior of $h=\sqrt n(\theta-\hat\theta_n)$. $\qquad\blacksquare$

**Remarks / interpretation.**
- The limit $N(0,\Sigma^{-1})$ is the inverse of the per-observation Fisher information $I_1(\theta)=\Sigma$; the prior has *washed out* (it contributed only the $\frac1n\Lambda^{-1}$ term, which is asymptotically negligible). This prior-forgetting is the content of BvM.
- Equivalently one may center at the posterior mean $\mu_n$ or at $\theta^\star$; since $\sqrt n(\hat\theta_n-\theta^\star)\Rightarrow N(0,\Sigma^{-1})$ and $\sqrt n(\mu_n-\hat\theta_n)\to_{\mathbb P}0$, all three centerings agree asymptotically. A standard corollary is the asymptotic equivalence of Bayesian credible sets and frequentist confidence sets.
- Pinsker explicit bound: with $\Sigma_0=\Sigma^{-1}$,
$$
\mathrm{KL}\big(N(m_n,V_n)\,\|\,N(0,\Sigma_0)\big)
=\tfrac12\Big(\operatorname{tr}(\Sigma_0^{-1}V_n)-p+m_n^\top\Sigma_0^{-1}m_n+\log\tfrac{\det\Sigma_0}{\det V_n}\Big)\to0,
$$
and $\|\cdot\|_{TV}\le\sqrt{\tfrac12\mathrm{KL}}\to0$, giving an alternative direct route to Step 4.

---

### Part 2(b). Posterior mean as $\lambda\to\infty$ with $\Lambda=\lambda I_p$ and $X$ full rank

Take $\Lambda=\lambda I_p$, so $\Lambda^{-1}=\frac1\lambda I_p$. From $(\ast)$ the posterior mean is the **ridge estimator**
$$
\mu_n(\lambda) = \Big(X^\top X + \tfrac1\lambda I_p\Big)^{-1} X^\top Y .
$$
"$X$ full rank" with the problem's setup ($p$ fixed, $n\ge p$) means $\operatorname{rank}(X)=p$, so $X^\top X\succ0$ is invertible. As $\lambda\to\infty$, $\frac1\lambda I_p \to 0$, and by continuity of matrix inversion at the invertible matrix $X^\top X$,
$$
\mu_n(\lambda) \xrightarrow[\lambda\to\infty]{} (X^\top X)^{-1}X^\top Y .
$$
Thus

$$
\boxed{\;\lim_{\lambda\to\infty}\mathbb{E}[\theta\mid Y] = (X^\top X)^{-1}X^\top Y = \hat\theta_{\mathrm{OLS}} = \hat\theta_{\mathrm{MLE}}.\;}
$$

**Interpretation.** Sending $\lambda\to\infty$ makes the prior $N(0,\lambda I_p)$ flat (vanishing precision $\frac1\lambda\to0$), i.e. an (improper) uniform prior in the limit; the posterior mean then reduces to the ordinary least squares / maximum-likelihood estimator. For finite $\lambda$, $\mu_n(\lambda)$ is the ridge regression estimate with penalty $\frac1\lambda$, shrinking $\hat\theta_{\mathrm{OLS}}$ toward $0$; the shrinkage disappears as $\lambda\to\infty$. (Conversely $\lambda\to0^+$ gives $\mu_n\to 0$, full shrinkage to the prior mean.)

---

## Summary of answers

1. The most powerful level-$\alpha$ test (Neyman–Pearson) rejects for large $T=(\theta_1-\theta_0)^\top X^\top Y$, and its maximal power is
$$
\beta_{\max}=\Phi\big(d - z_{1-\alpha}\big),\qquad d=\sqrt{(\theta_1-\theta_0)^\top X^\top X(\theta_1-\theta_0)} .
$$
2(a). The posterior is exactly $N\big((X^\top X+\Lambda^{-1})^{-1}X^\top Y,\ (X^\top X+\Lambda^{-1})^{-1}\big)$, and the rescaled posterior of $\sqrt n(\theta-\hat\theta_n)$ converges in total variation, in probability, to $N(0,\Sigma^{-1})$ — Bernstein–von Mises; the prior washes out.
2(b). With $\Lambda=\lambda I_p$ and $X$ full rank, the posterior mean is the ridge estimator $(X^\top X+\frac1\lambda I_p)^{-1}X^\top Y$, and $\lim_{\lambda\to\infty}\mathbb E[\theta\mid Y]=(X^\top X)^{-1}X^\top Y=\hat\theta_{\mathrm{OLS}}$.
