# 2019 Summer Math-Stat, Question 2 — Worked Solution

**Setup (Part 1).** We observe $(X_{i\cdot}, y_i)_{i=1}^n$ from
$$
y_i = X_{i\cdot}^\top \beta + \varepsilon_i,\qquad 1\le i\le n,
$$
with $X_{i\cdot}\in\mathbb{R}^p$ mean zero, $\Sigma=\mathbb{E}(X_{i\cdot}X_{i\cdot}^\top)$, $\beta\in\mathbb{R}^p$, $p\ge n$, $\|\beta\|_0\le k$, and $\varepsilon_i\overset{iid}{\sim}N(0,\sigma^2)$ independent of the $X_{i\cdot}$. Stack into $y\in\mathbb{R}^n$, design matrix $X\in\mathbb{R}^{n\times p}$ (rows $X_{i\cdot}^\top$), noise $\varepsilon\in\mathbb{R}^n$, so $y=X\beta+\varepsilon$. Write $\hat\Sigma=\tfrac1n X^\top X$ for the sample (Gram) covariance. We assume throughout the columns of $X$ are normalized so that $\hat\Sigma_{jj}=\tfrac1n\sum_i X_{ij}^2 \asymp 1$ (e.g. $\le 1$ after standardization), and that $\Sigma$ has bounded eigenvalues / the design satisfies a restricted eigenvalue (RE) condition (defined in 1a). The active set is $S=\{j:\beta_j\ne 0\}$, $|S|\le k$.

---

## Part 1a (5 pts): Lasso, tuning, and rates

**Lasso optimization.** The Lasso estimator is
$$
\hat\beta \;=\; \arg\min_{b\in\mathbb{R}^p}\;\Big\{ \tfrac{1}{2n}\,\|y - Xb\|_2^2 \;+\; \lambda\,\|b\|_1 \Big\}.
$$
The $\ell_1$ penalty induces sparsity; $\lambda>0$ is the tuning parameter.

**Choice of tuning parameter.** The standard choice is driven by the "noise level" of the score. The KKT/optimality condition requires $\lambda$ to dominate the empirical correlation between the columns of $X$ and the noise, $\big\|\tfrac1n X^\top\varepsilon\big\|_\infty$. For sub-Gaussian columns with $\hat\Sigma_{jj}\lesssim 1$, each $\tfrac1n X_{\cdot j}^\top\varepsilon$ is mean-zero with standard deviation of order $\sigma/\sqrt n$, and a union bound over $p$ coordinates gives $\big\|\tfrac1n X^\top\varepsilon\big\|_\infty \lesssim \sigma\sqrt{\log p / n}$ with probability $\ge 1-2/p$. Hence choose
$$
\boxed{\;\lambda = C\,\sigma\sqrt{\dfrac{\log p}{n}}\;}\qquad (C>2\sqrt2\ \text{suffices}),
$$
i.e. $\lambda\asymp \sigma\sqrt{\log p/n}$. (If $\sigma$ is unknown one uses the scaled/square-root Lasso or plugs in $\hat\sigma$ from 1b.)

**Restricted eigenvalue (RE) condition.** There exists $\kappa>0$ with
$$
\frac{1}{n}\|Xv\|_2^2 \;=\; v^\top\hat\Sigma v \;\ge\; \kappa\,\|v_S\|_2^2
\qquad\text{for all } v\in\mathbb{R}^p \text{ with } \|v_{S^c}\|_1\le 3\|v_S\|_1.
$$
This holds w.h.p. when $\Sigma\succ 0$ has bounded eigenvalues and $n\gtrsim k\log p$.

**Rates of convergence** (stated, not derived). On the event $\lambda\ge 2\|\tfrac1n X^\top\varepsilon\|_\infty$ together with RE, the oracle inequalities give
$$
\frac{1}{n}\|X(\hat\beta-\beta)\|_2^2 \;\lesssim\; \frac{k\lambda^2}{\kappa} \;\asymp\; \frac{\sigma^2\,k\log p}{\kappa\,n},
\qquad
\|\hat\beta-\beta\|_1 \;\lesssim\; \frac{k\lambda}{\kappa} \;\asymp\; \frac{\sigma\,k}{\kappa}\sqrt{\frac{\log p}{n}} .
$$
So the prediction-error rate is $k\log p/n$ and the $\ell_1$-estimation rate is $k\sqrt{\log p/n}$. (Also $\|\hat\beta-\beta\|_2^2\lesssim \sigma^2 k\log p/(\kappa^2 n)$.)

---

## Part 1b (10 pts): Estimating $\sigma^2$ and its rate

**Estimator.** Use the Lasso residuals. With $\hat\beta$ from 1a, define
$$
\boxed{\;\hat\sigma^2 \;=\; \frac{1}{n}\,\big\| y - X\hat\beta \big\|_2^2 \;=\; \frac1n\sum_{i=1}^n \big(y_i - X_{i\cdot}^\top\hat\beta\big)^2 \;}.
$$
(A degrees-of-freedom-corrected version $\hat\sigma^2=\|y-X\hat\beta\|_2^2/(n-\hat s)$, $\hat s=\|\hat\beta\|_0$, has the same rate; the scaled-Lasso of Sun–Zhang produces this jointly with $\hat\beta$.)

**Rate of convergence.** Write $r=X(\hat\beta-\beta)$. Since $y-X\hat\beta=\varepsilon - r$,
$$
\hat\sigma^2 = \frac1n\|\varepsilon\|_2^2 - \frac{2}{n}\varepsilon^\top r + \frac1n\|r\|_2^2 .
$$
Therefore
$$
\hat\sigma^2 - \sigma^2 = \underbrace{\Big(\tfrac1n\|\varepsilon\|_2^2 - \sigma^2\Big)}_{(\mathrm I)} \;-\; \underbrace{\tfrac{2}{n}\varepsilon^\top r}_{(\mathrm{II})} \;+\; \underbrace{\tfrac1n\|r\|_2^2}_{(\mathrm{III})} .
$$

- **(I)** $\tfrac1n\|\varepsilon\|_2^2$ is the mean of $n$ iid $\sigma^2\chi^2_1$ variables; by the CLT / $\chi^2$ concentration, $|(\mathrm I)| = O_P(\sigma^2/\sqrt n)$. (Sub-exponential tail: $\Pr(|(\mathrm I)|>\sigma^2 t)\le 2e^{-cn\min(t,t^2)}$.)
- **(III)** By 1a, $|(\mathrm{III})| = \tfrac1n\|X(\hat\beta-\beta)\|_2^2 \lesssim \sigma^2 k\log p/(\kappa n) = O_P\!\big(\sigma^2 k\log p/n\big)$.
- **(II)** By Cauchy–Schwarz, $\big|\tfrac2n\varepsilon^\top r\big| \le 2\sqrt{\tfrac1n\|\varepsilon\|_2^2}\,\sqrt{\tfrac1n\|r\|_2^2} = O_P\!\big(\sigma\cdot \sigma\sqrt{k\log p/n}\big) = O_P\!\big(\sigma^2\sqrt{k\log p/n}\big)$. (Equivalently use the Hölder bound $|\tfrac1n\varepsilon^\top X(\hat\beta-\beta)|\le\|\tfrac1n X^\top\varepsilon\|_\infty\|\hat\beta-\beta\|_1\lesssim \sigma\sqrt{\log p/n}\cdot \sigma k\sqrt{\log p/n}=\sigma^2 k\log p/n$, which is even smaller.)

Combining, the dominant stochastic term is (I) of order $1/\sqrt n$, while the bias-type terms are $O_P(k\log p/n)$ (using the sharper Hölder bound for (II)):
$$
\boxed{\;\big|\hat\sigma^2-\sigma^2\big| \;=\; O_P\!\left(\frac{\sigma^2}{\sqrt n} + \frac{\sigma^2\,k\log p}{n}\right).}
$$
Hence whenever $k\log p = o(\sqrt n)$ (i.e. $k\log p/\sqrt n\to 0$), the estimator is $\sqrt n$-consistent: $\sqrt n(\hat\sigma^2-\sigma^2)\Rightarrow N(0,2\sigma^4)$, the same first-order behavior as the oracle $\tfrac1n\|\varepsilon\|_2^2$.

---

## Part 1c (15 pts): Debiased (de-sparsified) estimator of $\beta_1$

**Why debias.** $\hat\beta$ has an $O(\lambda)$ shrinkage/regularization bias and a non-tractable, non-Gaussian distribution, so it cannot be used directly for inference on a single coordinate. The de-sparsified Lasso (Zhang–Zhang; van de Geer–Bühlmann–Ritov–Dezeure; Javanmard–Montanari) removes the first-order bias to leave an asymptotically Gaussian pivot.

**KKT identity.** The KKT conditions of the Lasso give, for a subgradient $\hat\kappa\in\partial\|\hat\beta\|_1$,
$$
\hat\Sigma(\hat\beta-\beta) = \tfrac1n X^\top\varepsilon - \lambda\hat\kappa .
$$

**Construction.** Fix coordinate $j=1$. Let $e_1$ be the first standard basis vector. We want a vector $m\in\mathbb{R}^p$ ("score" / relaxed inverse-covariance row) with $\hat\Sigma m\approx e_1$. The debiased estimator is
$$
\boxed{\;\hat\beta_1^{\,d} \;=\; \hat\beta_1 \;+\; \frac{1}{n}\, m^\top X^\top\big(y - X\hat\beta\big)\;}
\;=\; \hat\beta_1 + m^\top\Big(\tfrac1n X^\top(y-X\hat\beta)\Big).
$$

**Algorithm to obtain $m$ (nodewise / regression-based).**
The vector $m$ is built from a regression of column 1 of $X$ on the remaining columns.

1. **Nodewise Lasso.** Let $X_{\cdot 1}$ be the first column and $X_{\cdot,-1}$ the others. Solve
$$
\hat\gamma = \arg\min_{\gamma\in\mathbb{R}^{p-1}} \Big\{ \tfrac1n\|X_{\cdot 1}-X_{\cdot,-1}\gamma\|_2^2 + 2\lambda_1\|\gamma\|_1 \Big\}.
$$
2. **Residual.** $\eta = X_{\cdot 1}-X_{\cdot,-1}\hat\gamma$, and $\hat\tau_1^2 = \tfrac1n\eta^\top X_{\cdot 1} = \tfrac1n\|\eta\|_2^2 + \lambda_1\|\hat\gamma\|_1$.
3. **Score vector.** Set $m = \eta/\hat\tau_1^{2}$ scaled so that $m^\top X_{\cdot 1}/n = 1$; explicitly $m^\top X/n$ has first entry $1$ and small other entries. Equivalently define the projection direction $z_1=\eta$ and use
$$
\hat\beta_1^{\,d} = \hat\beta_1 + \frac{z_1^\top(y-X\hat\beta)}{z_1^\top X_{\cdot 1}} .
$$

**Equivalent constrained construction (Javanmard–Montanari).** Choose $m$ to solve
$$
m=\arg\min_{u} u^\top\hat\Sigma u \quad\text{s.t.}\quad \|\hat\Sigma u - e_1\|_\infty\le \mu,
$$
with $\mu\asymp\sqrt{\log p/n}$; this directly controls the bias term below.

Either way, $\hat\Theta$ with rows $m^{(j)}$ is an approximate inverse of $\hat\Sigma$ (a relaxed $\Sigma^{-1}=\Theta=(\theta_{jk})$ estimate). For the single coordinate $\beta_1$ we only need its first row $m$.

---

## Part 1d (20 pts): Asymptotic normality and confidence interval

**Bias–variance decomposition.** Using $y-X\hat\beta=\varepsilon-X(\hat\beta-\beta)$,
$$
\hat\beta_1^{\,d} = \hat\beta_1 + \tfrac1n m^\top X^\top\varepsilon - \tfrac1n m^\top X^\top X(\hat\beta-\beta)
= \hat\beta_1 + \tfrac1n m^\top X^\top\varepsilon - m^\top\hat\Sigma(\hat\beta-\beta).
$$
Subtract $\beta_1=e_1^\top\beta$ and write $m^\top\hat\Sigma(\hat\beta-\beta) = e_1^\top(\hat\beta-\beta) + (\hat\Sigma m - e_1)^\top(\hat\beta-\beta) = (\hat\beta_1-\beta_1) + (\hat\Sigma m-e_1)^\top(\hat\beta-\beta)$. The $(\hat\beta_1-\beta_1)$ cancels, giving
$$
\hat\beta_1^{\,d}-\beta_1 \;=\; \underbrace{\frac{1}{n}\,m^\top X^\top\varepsilon}_{=:W\ \text{(linear/Gaussian term)}} \;-\; \underbrace{(\hat\Sigma m - e_1)^\top(\hat\beta-\beta)}_{=:\Delta\ \text{(remainder/bias)}} .
$$

**Remainder is negligible.** By Hölder,
$$
|\Delta| \le \|\hat\Sigma m - e_1\|_\infty\,\|\hat\beta-\beta\|_1 \le \mu\cdot \|\hat\beta-\beta\|_1.
$$
With the construction giving $\|\hat\Sigma m-e_1\|_\infty\lesssim\sqrt{\log p/n}$ (assumed high-probability event), and the assumed event $\|\hat\beta-\beta\|_1\lesssim k\sqrt{\log p/n}$ from 1a,
$$
|\Delta| \;\lesssim\; \frac{k\log p}{n} \;=\; o\!\Big(\frac1{\sqrt n}\Big)\quad\text{provided } k\log p = o(\sqrt n).
$$
So $\sqrt n\,\Delta\overset{P}{\to}0$ (the *ultra-sparse* / beta-min-free condition $k\ll\sqrt n/\log p$).

**Gaussian term.** Conditional on $X$, $W=\tfrac1n m^\top X^\top\varepsilon = \tfrac1n\sum_i (m^\top X_{i\cdot})\varepsilon_i$ is a linear combination of independent $N(0,\sigma^2)$, hence
$$
W \mid X \;\sim\; N\!\Big(0,\; \tfrac{\sigma^2}{n^2} m^\top X^\top X\, m\Big) = N\!\Big(0,\; \tfrac{\sigma^2}{n}\, m^\top\hat\Sigma m\Big).
$$
Define $V_1 = m^\top\hat\Sigma m$ (with the nodewise construction $V_1 = \|\eta\|_2^2/(n\hat\tau_1^4)\approx 1/\hat\tau_1^2 \to \Theta_{11}=(\Sigma^{-1})_{11}$). Then
$$
\frac{\sqrt n\,(\hat\beta_1^{\,d}-\beta_1)}{\sigma\sqrt{V_1}} \;=\; \frac{\sqrt n\,W}{\sigma\sqrt{V_1}} - \frac{\sqrt n\,\Delta}{\sigma\sqrt{V_1}} \;\xrightarrow{\ d\ }\; N(0,1),
$$
exactly $N(0,1)$ for the first (conditionally Gaussian) term and $o_P(1)$ for the second. Theorems used: **CLT / exact Gaussian linear combination of Gaussians**, **Hölder's inequality**, and **Slutsky's theorem** (replacing $\sigma^2,V_1$ by consistent estimates).

**Asymptotic normality statement.**
$$
\boxed{\;\sqrt n\,(\hat\beta_1^{\,d}-\beta_1) \;\xrightarrow{\ d\ }\; N\!\big(0,\ \sigma^2\,\Theta_{11}\big),\qquad \Theta_{11}=(\Sigma^{-1})_{11}. }
$$
The asymptotic variance $\sigma^2\Theta_{11}$ is the semiparametric efficiency bound for one coordinate, so the debiased Lasso is efficient.

**Confidence interval.** Estimate the standard error by $\widehat{\mathrm{se}} = \hat\sigma\sqrt{V_1/n} = \hat\sigma\sqrt{m^\top\hat\Sigma m}/\sqrt n$ (with $\hat\sigma$ from 1b, $V_1=m^\top\hat\Sigma m$). A level-$(1-\alpha)$ confidence interval for $\beta_1$ is
$$
\boxed{\;\hat\beta_1^{\,d} \;\pm\; z_{1-\alpha/2}\,\frac{\hat\sigma\,\sqrt{m^\top\hat\Sigma m}}{\sqrt n}\;},
$$
where $z_{1-\alpha/2}$ is the standard normal quantile. By the convergence above and Slutsky, $\Pr(\beta_1\in\text{CI})\to 1-\alpha$. (The same construction for every $j$ yields simultaneous coordinate-wise inference.)

---

## Part 1e (15 pts): Support recovery via thresholding

**Estimator.** Threshold the debiased estimates. Compute $\hat\beta_j^{\,d}$ for every $j$ (as in 1c–1d), with per-coordinate standard error $\widehat{\mathrm{se}}_j=\hat\sigma\sqrt{V_j/n}\asymp \sigma\sqrt{\Theta_{jj}/n}\asymp \sqrt{\log p/n}$-scale once multiplied by a $\sqrt{\log p}$ factor. Define
$$
\boxed{\;\hat S \;=\; \Big\{\,j : \big|\hat\beta_j^{\,d}\big| \;\ge\; \tau\,\Big\},\qquad \tau = C'\,\sigma\sqrt{\frac{\log p}{n}}\;}
$$
for a suitable constant $C'$ (more precisely $\tau_j = \hat\sigma\sqrt{V_j}\,\sqrt{2\log p}/\sqrt n$, a Bonferroni/maximal-deviation level so that all null coordinates are simultaneously below threshold w.h.p.). Equivalently one may threshold the Lasso itself, $\hat S=\{j:|\hat\beta_j|\ge\tau\}$; the debiased version gives cleaner control because each coordinate is $\sqrt n$-consistent and unbiased.

**Uniform error bound.** From 1d, uniformly over $j$,
$$
\hat\beta_j^{\,d} = \beta_j + \tfrac1n m^{(j)\top}X^\top\varepsilon - \Delta_j,\qquad \max_j|\Delta_j|\lesssim \frac{k\log p}{n}.
$$
The Gaussian terms $G_j:=\tfrac1n m^{(j)\top}X^\top\varepsilon$ are mean-zero with $\mathrm{sd}\asymp \sigma\sqrt{\Theta_{jj}/n}$; a maximal/union bound gives, w.h.p.,
$$
\max_{1\le j\le p}\big|\hat\beta_j^{\,d}-\beta_j\big| \;\le\; \underbrace{c_1\,\sigma\sqrt{\frac{\log p}{n}}}_{\max_j|G_j|} + \underbrace{c_2\,\frac{k\log p}{n}}_{\max_j|\Delta_j|} \;\le\; \frac{\tau}{2}
$$
for an appropriate constant in $\tau=C'\sigma\sqrt{\log p/n}$ (choosing $C'$ large enough and using $k\log p=o(\sqrt n)$ so the $\Delta$ term is lower order). Call this event $\mathcal E$, $\Pr(\mathcal E)\to1$.

**No false positives: $\hat S\subseteq S$.** If $j\notin S$ then $\beta_j=0$, so on $\mathcal E$,
$$
|\hat\beta_j^{\,d}| = |\hat\beta_j^{\,d}-\beta_j| \le \tfrac{\tau}{2} < \tau,
$$
hence $j\notin\hat S$. Contrapositive: $\hat S\subseteq S$ w.h.p.

**Recover strong signals: $S_{\text{strong}}\subseteq\hat S$.** Let $S_{\text{strong}}=\{j:|\beta_j|\ge C\sqrt{\log p/n}\}$ with $C$ chosen so that $C\sigma\sqrt{\log p/n}\ge \tfrac32\tau$ (i.e. $C\ge \tfrac32 C'$, absorbing $\sigma$). If $j\in S_{\text{strong}}$, then on $\mathcal E$, by the reverse triangle inequality,
$$
|\hat\beta_j^{\,d}| \ge |\beta_j| - |\hat\beta_j^{\,d}-\beta_j| \ge C\sigma\sqrt{\tfrac{\log p}{n}} - \tfrac{\tau}{2} \ge \tfrac32\tau-\tfrac12\tau = \tau,
$$
so $j\in\hat S$. Hence $S_{\text{strong}}\subseteq\hat S$ w.h.p.

**Conclusion.**
$$
\boxed{\;S_{\text{strong}} \;\subseteq\; \hat S \;\subseteq\; S\quad\text{with probability}\to 1,\qquad \tau\asymp \sigma\sqrt{\log p/n}.}
$$
Thus exact support recovery $\hat S=S$ holds additionally under the **beta-min** condition $\min_{j\in S}|\beta_j|\ge C\sqrt{\log p/n}$ (i.e. $S=S_{\text{strong}}$). Theorems/tools: KKT conditions, Gaussian maximal inequality + union bound, reverse triangle inequality.

---

## Part 2a (15 pts): Smoothing spline and local-linear estimators

Model: $y_i=f(t_i)+\varepsilon_i$, $t_i$ random on an interval (say $[a,b]$), $\varepsilon_i$ mean-zero independent of $t_i$, variance $\sigma^2$.

**Smoothing-spline estimator.** Penalize roughness via the integrated squared second derivative:
$$
\boxed{\;\hat f_\lambda = \arg\min_{g\in W_2^2[a,b]} \Big\{ \frac1n\sum_{i=1}^n \big(y_i-g(t_i)\big)^2 + \lambda\!\int_a^b \big(g''(t)\big)^2\,dt \Big\}\;},\quad \lambda>0.
$$
$W_2^2$ is the Sobolev space of functions with square-integrable second derivative. The minimizer is a **natural cubic spline** with knots at the observed $t_i$ (this is a theorem: among all $W_2^2$ interpolants/penalized fits the optimum is a natural cubic spline). $\lambda$ trades fit (small $\lambda$ = interpolation) against smoothness (large $\lambda$ = linear least-squares fit); chosen by (generalized) cross-validation.

**Local-linear estimator of $f(x_0)$.** With kernel $K$ and bandwidth $h$, solve the locally weighted least squares
$$
(\hat a,\hat b) = \arg\min_{a,b}\sum_{i=1}^n \big(y_i - a - b(t_i-x_0)\big)^2\, K\!\Big(\frac{t_i-x_0}{h}\Big).
$$
Then
$$
\boxed{\;\hat f(x_0)=\hat a,\qquad \hat f'(x_0)=\hat b.}
$$
**Closed form.** Let $w_i=K\big((t_i-x_0)/h\big)$, $u_i=t_i-x_0$, and $S_r=\sum_i w_i u_i^{\,r}$. By the normal equations,
$$
\hat f(x_0)=\frac{S_2\,\sum_i w_i y_i - S_1\,\sum_i w_i u_i y_i}{S_0 S_2 - S_1^2},\qquad
\hat f'(x_0)=\frac{S_0\,\sum_i w_i u_i y_i - S_1\,\sum_i w_i y_i}{S_0 S_2 - S_1^2}.
$$
In matrix form, with $T_{x_0}=\big[\,\mathbf 1,\ (t_i-x_0)\,\big]\in\mathbb{R}^{n\times2}$ and $W=\mathrm{diag}(w_i)$,
$$
\begin{pmatrix}\hat a\\ \hat b\end{pmatrix} = (T_{x_0}^\top W T_{x_0})^{-1}T_{x_0}^\top W y,\qquad \hat f(x_0)=e_1^\top(\cdot),\ \ \hat f'(x_0)=e_2^\top(\cdot).
$$
Local linear has the well-known advantage of automatic boundary-bias correction and design-adaptivity. (More generally, local polynomial of degree $\ge p$ estimates $f^{(\nu)}$.)

---

## Part 2b (10 pts): Closed form of the smoothing spline via a basis

Assume a basis $\{B_1,\dots,B_K\}$ of the relevant spline space (e.g. natural cubic spline / B-spline basis), so we restrict to $g(t)=\sum_{k=1}^K \theta_k B_k(t)=B(t)^\top\theta$, $\theta\in\mathbb{R}^K$. Define:

- Design matrix $\mathbf{B}\in\mathbb{R}^{n\times K}$, $\mathbf{B}_{ik}=B_k(t_i)$, so the fitted values are $g(t_i)=(\mathbf B\theta)_i$.
- Penalty (roughness) matrix $\Omega\in\mathbb{R}^{K\times K}$, $\Omega_{k\ell}=\int_a^b B_k''(t)B_\ell''(t)\,dt$, so that $\int (g'')^2 = \theta^\top\Omega\theta$.

The objective becomes the **penalized (ridge-type) least squares**
$$
J(\theta) = \frac1n\|y-\mathbf B\theta\|_2^2 + \lambda\,\theta^\top\Omega\theta .
$$
Setting the gradient to zero:
$$
\nabla J(\theta) = -\frac2n \mathbf B^\top(y-\mathbf B\theta) + 2\lambda\,\Omega\theta = 0
\;\Longrightarrow\; \big(\mathbf B^\top\mathbf B + n\lambda\,\Omega\big)\theta = \mathbf B^\top y .
$$
Hence the closed-form coefficient vector and estimator are
$$
\boxed{\;\hat\theta = \big(\mathbf B^\top\mathbf B + n\lambda\,\Omega\big)^{-1}\mathbf B^\top y,\qquad \hat f(t)=B(t)^\top\hat\theta.}
$$
The fitted values are $\hat y = \mathbf B\hat\theta = \mathbf B(\mathbf B^\top\mathbf B+n\lambda\Omega)^{-1}\mathbf B^\top y =: S_\lambda\, y$, where $S_\lambda$ is the **smoother (hat) matrix**; its trace $\operatorname{tr}(S_\lambda)$ is the effective degrees of freedom, used in GCV
$$
\mathrm{GCV}(\lambda)=\frac{\tfrac1n\|y-S_\lambda y\|_2^2}{\big(1-\operatorname{tr}(S_\lambda)/n\big)^2}.
$$
This is a positive-definite linear system ($\mathbf B^\top\mathbf B+n\lambda\Omega\succ0$ for $\lambda>0$ when $\mathbf B$ has the constant/linear directions identified), so $\hat\theta$ is unique and the estimator is **linear in $y$**.

---

## Part 2c (10 pts): High-dimensional sparse additive model (sparsity + smoothness)

Model: $y_i=\sum_{j=1}^p f_j(X_{ij})+\varepsilon_i$, with $S=\{j:f_j\ne0\}$ small ($|S|\le k\ll p$), each $f_j$ smooth (in a Sobolev/RKHS ball), centered ($\mathbb{E} f_j(X_{\cdot j})=0$ for identifiability; absorb the intercept). We need both **sparsity** (select the few relevant components) and **smoothness** (smooth each selected component). This is the **SpAM** (Sparse Additive Models, Ravikumar–Lafferty–Liu–Wasserman) / sparsity-smoothness penalty (Meier–van de Geer–Bühlmann) framework — group-Lasso-type selection over function components.

**Basis expansion.** Expand each component in a truncated smooth basis $\{B_{j1},\dots,B_{jd}\}$ (e.g. cubic splines), $f_j(x)=\sum_{\ell=1}^d \theta_{j\ell}B_{j\ell}(x)=B_j(x)^\top\theta_j$, with per-component roughness penalty $\theta_j^\top\Omega_j\theta_j$ ($\Omega_j$ as in 2b) and smoothness/empirical norm $\|f_j\|_n^2=\tfrac1n\sum_i f_j(X_{ij})^2$.

**Estimator (sparsity-smoothness penalty).** Solve
$$
\boxed{\;\{\hat\theta_j\}=\arg\min_{\{\theta_j\}} \frac{1}{2n}\Big\|y-\sum_{j=1}^p \mathbf B_j\theta_j\Big\|_2^2 \;+\; \lambda\sum_{j=1}^p \sqrt{\,\|f_j\|_n^2 + \rho^2\,\theta_j^\top\Omega_j\theta_j\,}\;}
$$
where $\mathbf B_j\in\mathbb{R}^{n\times d}$ is the basis matrix for component $j$, and $\hat f_j(x)=B_j(x)^\top\hat\theta_j$. Two penalty roles:

- The **outer $\ell_1$-over-groups** (sum of $\ell_2$-type norms of whole components) is a **group Lasso**: it sets entire components $\hat f_j\equiv0$ to zero, achieving *variable selection / sparsity* across $j$.
- The **inner roughness term** $\rho^2\theta_j^\top\Omega_j\theta_j$ (or $\|f_j''\|^2$) enforces *smoothness* of each selected $f_j$.

A simpler/equivalent **SpAM** form uses the empirical $\ell_2$-norm penalty $\lambda\sum_j \|f_j\|_n=\lambda\sum_j\sqrt{\tfrac1n\sum_i f_j(X_{ij})^2}$ for selection, with smoothness imposed by smoothing each component (backfitting with a smoother $S_j$). The SpAM backfitting algorithm:

1. Initialize $\hat f_j=0$.
2. Cycle over $j$: compute partial residual $R_j = y-\sum_{k\ne j}\hat f_k$; smooth $P_j = S_j R_j$ (univariate smoother, e.g. the spline of 2b); apply the **soft-threshold at the function level**
$$
\hat f_j \leftarrow \Big[\,1-\frac{\lambda}{\|P_j\|_n}\,\Big]_+ P_j ,
$$
which zeroes out $\hat f_j$ when $\|P_j\|_n\le\lambda$ (selection) and shrinks otherwise.
3. Center $\hat f_j\leftarrow \hat f_j-\overline{\hat f_j}$; iterate to convergence.

**Tuning.** $d\asymp n^{1/5}$ (cubic-spline rate for twice-differentiable $f_j$), and $\lambda\asymp \sqrt{\log p/n}$ (up to the basis-size factor), so the per-component soft-threshold dominates the noise across all $p$ candidates. **Rate.** Under a sparse-additive RE/compatibility condition, this attains (up to logs) the oracle rate
$$
\sum_{j\in S}\|\hat f_j - f_j\|_n^2 \;\lesssim\; k\,n^{-4/5} + \frac{k\log p}{n},
$$
i.e. the sum of the **nonparametric estimation rate** $n^{-4/5}$ per relevant component and the **selection price** $k\log p/n$ from searching among $p$ components — exactly combining smoothness ($n^{-4/5}$) and sparsity ($k\log p/n$). This is the link to Part 1: the group-Lasso/soft-threshold mechanism is the functional analogue of the Lasso selection used there.

---

### Summary of boxed answers
- **1a.** $\hat\beta=\arg\min \tfrac1{2n}\|y-Xb\|_2^2+\lambda\|b\|_1$, $\lambda\asymp\sigma\sqrt{\log p/n}$; $\tfrac1n\|X(\hat\beta-\beta)\|_2^2\asymp \sigma^2 k\log p/n$, $\|\hat\beta-\beta\|_1\asymp \sigma k\sqrt{\log p/n}$.
- **1b.** $\hat\sigma^2=\tfrac1n\|y-X\hat\beta\|_2^2$; $|\hat\sigma^2-\sigma^2|=O_P(\sigma^2/\sqrt n + \sigma^2 k\log p/n)$, $\sqrt n$-consistent if $k\log p=o(\sqrt n)$.
- **1c.** $\hat\beta_1^d=\hat\beta_1+\tfrac1n m^\top X^\top(y-X\hat\beta)$ with $m$ from nodewise Lasso (or constrained $\|\hat\Sigma m-e_1\|_\infty\le\mu$).
- **1d.** $\sqrt n(\hat\beta_1^d-\beta_1)\Rightarrow N(0,\sigma^2\Theta_{11})$; CI $=\hat\beta_1^d\pm z_{1-\alpha/2}\hat\sigma\sqrt{m^\top\hat\Sigma m/n}$.
- **1e.** $\hat S=\{j:|\hat\beta_j^d|\ge\tau\}$, $\tau\asymp\sigma\sqrt{\log p/n}$; gives $S_{\text{strong}}\subseteq\hat S\subseteq S$ w.h.p.
- **2a.** Spline: penalized LS with $\lambda\int(g'')^2$ (natural cubic spline); local linear: $\hat f(x_0)=\hat a$, $\hat f'(x_0)=\hat b$ from weighted LS.
- **2b.** $\hat\theta=(\mathbf B^\top\mathbf B+n\lambda\Omega)^{-1}\mathbf B^\top y$, $\hat f=B(\cdot)^\top\hat\theta$, $S_\lambda=\mathbf B(\mathbf B^\top\mathbf B+n\lambda\Omega)^{-1}\mathbf B^\top$.
- **2c.** SpAM / sparsity-smoothness group-Lasso with functional soft-thresholding backfitting; oracle rate $k n^{-4/5}+k\log p/n$.
