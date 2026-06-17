# 2018 Summer — Mathematical Statistics, Question 2

## Setup and notation

We observe i.i.d. data $\{(X_i,Y_i)\}_{i=1}^n$ with $Y_i\in\{0,1\}$ and $X_i\in\mathbb R^p$. The logistic model
$$
\pi(x;\beta)=\sigma(x^T\beta),\qquad \sigma(v)=\frac{e^v}{1+e^v},
$$
is correctly specified with true value $\beta^*$, i.e. $E[Y_i\mid X_i]=\pi(X_i;\beta^*)$.

Throughout write $v_i=v_i(\beta)=X_i^T\beta$, $\pi_i(\beta)=\sigma(v_i)$, and use the elementary identities
$$
\sigma'(v)=\sigma(v)\bigl(1-\sigma(v)\bigr),\qquad
\nabla_\beta\pi_i(\beta)=\pi_i(1-\pi_i)\,X_i .
$$
Also
$$
\sqrt{\pi_i(1-\pi_i)}=\sqrt{\sigma'(v_i)}=\frac{e^{v_i/2}}{1+e^{v_i}} .
\tag{$\ast$}
$$

The estimator $\tilde\beta$ solves the estimating equation
$$
\Psi_n(\beta):=\frac1n\sum_{i=1}^n\psi(X_i,Y_i;\beta)=0,\qquad
\psi(X,Y;\beta)=\frac{Y-\pi(X;\beta)}{\sqrt{\pi(X;\beta)\bigl(1-\pi(X;\beta)\bigr)}}\,X .
$$
This is the estimating function obtained from the **Pearson-residual / chi-square type** weighting (residual divided by its model standard deviation), as opposed to the MLE score (residual times $X$ with no denominator). Hence $\tilde\beta$ is a genuine $M$-/$Z$-estimator, generally different from the MLE.

---

## Part (i): $\tilde\beta$ minimizes an explicit loss $\kappa(\beta)$

We seek $\kappa$ with $\nabla_\beta\kappa(\beta)=-\Psi_n(\beta)$ (or any nonzero scalar multiple), so that the estimating equation is exactly the stationarity condition $\nabla\kappa=0$.

Because $\beta$ enters only through $v_i=X_i^T\beta$ and $\nabla_\beta=X_i\,\dfrac{d}{dv_i}$, it suffices to find a scalar antiderivative $G(v;Y)$ with
$$
\frac{\partial G}{\partial v}=-\frac{Y-\sigma(v)}{\sqrt{\sigma'(v)}} .
$$
Using $(\ast)$,
$$
\frac{1-\sigma(v)}{\sqrt{\sigma'(v)}}=\frac{1/(1+e^v)}{e^{v/2}/(1+e^v)}=e^{-v/2},
\qquad
\frac{\sigma(v)}{\sqrt{\sigma'(v)}}=e^{v/2}.
$$
Therefore
$$
\frac{Y-\sigma(v)}{\sqrt{\sigma'(v)}}=
\begin{cases}\ \ e^{-v/2}, & Y=1,\\[2pt] -e^{v/2}, & Y=0,\end{cases}
\qquad\Longrightarrow\qquad
G(v;Y)=
\begin{cases} 2\,e^{-v/2}, & Y=1,\\[2pt] 2\,e^{\ \,v/2}, & Y=0,\end{cases}
$$
(antiderivatives chosen with the additive constant set to $0$). Since $Y\in\{0,1\}$ both cases combine into the single expression
$$
G(v;Y)=2\bigl[Y\,e^{-v/2}+(1-Y)e^{v/2}\bigr]=2\,\exp\!\Bigl(-\tfrac12(2Y-1)\,v\Bigr).
$$
Introducing the symmetric label $\tilde Y:=2Y-1\in\{-1,+1\}$, we obtain

$$
\boxed{\;\kappa(\beta)=\frac1n\sum_{i=1}^n 2\,\exp\!\Bigl(-\tfrac12\,\tilde Y_i\,X_i^T\beta\Bigr),\qquad \tilde Y_i=2Y_i-1.\;}
$$

**Verification.** $\nabla_\beta\kappa(\beta)=\frac1n\sum_i 2\cdot(-\tfrac12\tilde Y_i X_i)\,e^{-\tilde Y_i v_i/2}
=-\frac1n\sum_i \tilde Y_i e^{-\tilde Y_i v_i/2}X_i$. Splitting on $Y_i$: when $Y_i=1$ the term is $-e^{-v_i/2}X_i$ and when $Y_i=0$ it is $+e^{v_i/2}X_i$, i.e. exactly $-\psi(X_i,Y_i;\beta)$. Hence $\nabla\kappa=-\Psi_n$, and any solution of $\Psi_n(\beta)=0$ is a stationary point of $\kappa$.

**It is in fact a minimizer.** Each summand $e^{-\tilde Y_i X_i^T\beta/2}$ is a (log-)convex exponential of a linear function of $\beta$, hence convex; a nonnegative average of convex functions is convex, so $\kappa$ is **convex** on $\mathbb R^p$. Thus every stationary point is a global minimizer, and $\tilde\beta=\arg\min_\beta\kappa(\beta)$. (If the design matrix has full column rank and the two classes are not perfectly separable, $\kappa$ is strictly convex / coercive in the relevant directions and the minimizer is unique.)

This $\kappa$ is precisely the **exponential loss** $\frac2n\sum_i e^{-\tilde Y_i X_i^T\beta/2}$ familiar from AdaBoost (here on the half-scaled margin $\tfrac12 X_i^T\beta$).

---

## Part (ii): Consistency of $\tilde\beta$

This is a standard $Z$-estimator (estimating-equation) argument. Define the population estimating function
$$
\Psi(\beta):=E\bigl[\psi(X,Y;\beta)\bigr]
=E\!\left[\frac{Y-\pi(X;\beta)}{\sqrt{\pi(X;\beta)(1-\pi(X;\beta))}}\,X\right].
$$

**(a) $\beta^*$ is a zero of $\Psi$ (unbiased estimating function).**
By the tower property and correct specification, $E[Y\mid X]=\pi(X;\beta^*)$, so
$$
\Psi(\beta^*)=E\!\left[\frac{E[Y\mid X]-\pi(X;\beta^*)}{\sqrt{\pi(X;\beta^*)(1-\pi(X;\beta^*))}}\,X\right]=0 .
$$
Thus the estimating function is **Fisher-consistent**.

Equivalently in the loss formulation, $\nabla\kappa^{(\infty)}(\beta):=E[\nabla_\beta\kappa]=-\Psi(\beta)$ vanishes at $\beta^*$, and $\kappa^{(\infty)}(\beta)=2E\bigl[e^{-\tilde Y X^T\beta/2}\bigr]$ is convex, so $\beta^*$ minimizes the population loss.

**Technical (regularity) conditions.** Impose:
1. *Identification / uniqueness.* $\Psi(\beta)=0$ only at $\beta=\beta^*$. A simple sufficient condition: $E\,XX^T\succ0$ (full-rank, non-degenerate design) together with the convexity of $\kappa^{(\infty)}$; then $\nabla^2\kappa^{(\infty)}(\beta)=\tfrac12 E\bigl[e^{-\tilde Y X^T\beta/2}\,\tfrac12 XX^T\bigr]\succ0$, i.e. $\kappa^{(\infty)}$ is strictly convex, giving a unique minimizer $\beta^*$.
2. *Moments / integrability.* $E\|X\|<\infty$ suffices for $\Psi(\beta^*)$ to exist; for the uniform control below assume $E\bigl[\|X\|\,e^{\|X\|\,\|\beta\|/2}\bigr]<\infty$ on a neighborhood (or simply that $X$ is bounded, $\|X\|\le M$ a.s., the weakest convenient assumption). Boundedness of $X$ makes every quantity below finite.
3. *Parameter space.* $\beta$ ranges over a set $\Theta$; either $\Theta$ compact, or use the convexity argument (next) which needs no compactness.

**(b) Uniform convergence.** By the i.i.d. SLLN/WLLN, for each fixed $\beta$, $\Psi_n(\beta)\xrightarrow{p}\Psi(\beta)$. The map $\beta\mapsto\psi(X,Y;\beta)$ is continuous, and under condition 2 (e.g. $\|X\|\le M$) the class $\{\psi(\cdot;\beta):\beta\in K\}$ has an integrable envelope on any compact $K$ and is dominated/Lipschitz, so by the uniform LLN (Glivenko–Cantelli / Wald-type uniform SLLN),
$$
\sup_{\beta\in K}\bigl\|\Psi_n(\beta)-\Psi(\beta)\bigr\|\xrightarrow{p}0 .
$$

**(c) Argmax/zero consistency.** Two equivalent routes:

*Via the $Z$-estimator theorem* (van der Vaart, *Asymptotic Statistics*, Thm 5.9): if $\beta^*$ is a well-separated zero of the continuous $\Psi$ (condition 1), $\Psi_n\to\Psi$ uniformly on a neighborhood, and $\Psi_n(\tilde\beta)=o_p(1)$, then $\tilde\beta\xrightarrow{p}\beta^*$.

*Via convexity* (cleanest, requires the fewest conditions): $\kappa_n(\beta):=\kappa(\beta)$ is convex and converges pointwise in probability to the convex limit $\kappa^{(\infty)}(\beta)$, which has the unique minimizer $\beta^*$. By the **convexity lemma** (Pollard 1991; Hjort–Pollard), pointwise convergence of convex functions to a limit with a unique minimizer implies the minimizers converge:
$$
\tilde\beta=\arg\min\kappa_n\ \xrightarrow{p}\ \arg\min\kappa^{(\infty)}=\beta^* .
$$
Convexity is the reason no compactness of $\Theta$ is needed and pointwise (not uniform) convergence already suffices — this is the "weaker preferred" set of conditions.

$$
\boxed{\;\tilde\beta\xrightarrow{p}\beta^*.\;}
$$

---

## Part (iii): Asymptotic normality

We apply the standard $M$-/$Z$-estimator delta method. Conditions: $\beta^*$ interior; $\psi(X,Y;\cdot)$ is $C^1$ in $\beta$ (it is, being a smooth function of $v=X^T\beta$); $E\|\psi(X,Y;\beta^*)\|^2<\infty$ (the **score covariance** is finite); the Jacobian $A:=-\nabla_\beta\Psi(\beta)\big|_{\beta^*}=\nabla^2\kappa^{(\infty)}(\beta^*)$ exists and is nonsingular; and dominated derivatives so the LLN for the empirical Jacobian holds uniformly near $\beta^*$. Bounded $X$ guarantees all of these.

**Mean-value (one-step) expansion.** Since $\Psi_n(\tilde\beta)=0$, a Taylor expansion of $\Psi_n$ about $\beta^*$ gives
$$
0=\Psi_n(\tilde\beta)=\Psi_n(\beta^*)+\Bigl[\nabla_\beta\Psi_n(\bar\beta)\Bigr](\tilde\beta-\beta^*),
$$
for some $\bar\beta$ on the segment between $\tilde\beta$ and $\beta^*$ (row-wise mean value). Hence
$$
\sqrt n(\tilde\beta-\beta^*)=-\bigl[\nabla_\beta\Psi_n(\bar\beta)\bigr]^{-1}\sqrt n\,\Psi_n(\beta^*).
$$

**Numerator (CLT).** $\sqrt n\,\Psi_n(\beta^*)=\frac{1}{\sqrt n}\sum_i\psi(X_i,Y_i;\beta^*)$ is a normalized sum of i.i.d. mean-zero terms (mean zero by Part (ii)(a)). By the multivariate Lindeberg–Lévy CLT,
$$
\sqrt n\,\Psi_n(\beta^*)\xrightarrow{d}N(0,B),\qquad
B:=\operatorname{Var}\!\bigl(\psi(X,Y;\beta^*)\bigr)=E\bigl[\psi\psi^T\bigr]\big|_{\beta^*}.
$$

**Denominator (LLN + consistency).** By uniform LLN and $\bar\beta\xrightarrow{p}\beta^*$ (it is squeezed by $\tilde\beta\xrightarrow{p}\beta^*$), with continuity of $\beta\mapsto\nabla\Psi(\beta)$,
$$
\nabla_\beta\Psi_n(\bar\beta)\xrightarrow{p}\nabla_\beta\Psi(\beta^*)=-A,\qquad A:=-\nabla_\beta\Psi(\beta^*).
$$

**Slutsky.** Combining,
$$
\sqrt n(\tilde\beta-\beta^*)\xrightarrow{d}N\bigl(0,\;A^{-1}B\,A^{-T}\bigr).
$$

Because $\Psi=-\nabla\kappa^{(\infty)}$, $A=\nabla^2\kappa^{(\infty)}(\beta^*)$ is symmetric, so

$$
\boxed{\;\sqrt n(\tilde\beta-\beta^*)\xrightarrow{d}N(0,V_{\beta^*}),\qquad
V_{\beta^*}=A^{-1}\,B\,A^{-1},\quad A=-\nabla_\beta\Psi(\beta^*),\ \ B=E[\psi\psi^T]\big|_{\beta^*}.\;}
$$
This is the **sandwich (Huber) covariance**.

---

## Part (iv): Explicit $V_{\beta^*}$ and the efficiency comparison $V_{\beta^*}\ge U_{\beta^*}$

We compute the sandwich pieces. Write $\pi_i=\pi(X_i;\beta^*)$, $w_i:=\pi_i(1-\pi_i)=\sigma'(X_i^T\beta^*)$, and recall $\psi_i=\dfrac{Y_i-\pi_i}{\sqrt{w_i}}X_i$.

**The "meat" $B$.** Conditionally on $X$, $\operatorname{Var}(Y\mid X)=\pi(1-\pi)=w$. Since $\psi$ is mean zero,
$$
B=E\!\left[\frac{\operatorname{Var}(Y\mid X)}{w}\,XX^T\right]
=E\!\left[\frac{w}{w}\,XX^T\right]
=E\bigl[XX^T\bigr]=:S .
$$
The Pearson-type standardization makes each summand have conditional variance $1$, so the meat is simply the second-moment matrix of the covariates, $S=E\,XX^T$.

**The "bread" $A$.** $A=-E\,\nabla_\beta\psi(X,Y;\beta^*)$. Differentiate $\psi=\dfrac{Y-\sigma(v)}{\sqrt{\sigma'(v)}}X$ with respect to $\beta$ (only $v=X^T\beta$ depends on $\beta$, $\nabla_\beta v=X$):
$$
\nabla_\beta\psi=\frac{d}{dv}\!\left[\frac{Y-\sigma(v)}{\sqrt{\sigma'(v)}}\right]XX^T .
$$
Now $\dfrac{d}{dv}\dfrac{Y-\sigma}{\sqrt{\sigma'}}$. Using the Part (i) split (valid because $Y\in\{0,1\}$): $\dfrac{Y-\sigma}{\sqrt{\sigma'}}=Y e^{-v/2}-(1-Y)e^{v/2}$, whose $v$-derivative is $-\tfrac12\bigl(Y e^{-v/2}+(1-Y)e^{v/2}\bigr)$. Taking the conditional expectation $E[\,\cdot\mid X]$ with $E[Y\mid X]=\pi=\sigma(v)$:
$$
E\!\left[\frac{d}{dv}\frac{Y-\sigma}{\sqrt{\sigma'}}\,\Big|\,X\right]
=-\tfrac12\Bigl(\sigma\,e^{-v/2}+(1-\sigma)e^{v/2}\Bigr).
$$
With $\sigma=\frac{e^{v}}{1+e^{v}}$, $1-\sigma=\frac1{1+e^v}$:
$$
\sigma e^{-v/2}+(1-\sigma)e^{v/2}
=\frac{e^{v/2}+e^{v/2}}{1+e^v}\cdot\tfrac12\cdot 2 \;=\;\frac{e^{v/2}+e^{v/2}}{1+e^v}.
$$
Let me evaluate cleanly: $\sigma e^{-v/2}=\dfrac{e^{v}}{1+e^v}e^{-v/2}=\dfrac{e^{v/2}}{1+e^v}$ and $(1-\sigma)e^{v/2}=\dfrac{e^{v/2}}{1+e^v}$, so the sum is $\dfrac{2e^{v/2}}{1+e^v}=2\sqrt{\sigma'(v)}=2\sqrt{w}$ by $(\ast)$. Hence
$$
E\!\left[\frac{d}{dv}\frac{Y-\sigma}{\sqrt{\sigma'}}\,\Big|\,X\right]=-\tfrac12\cdot 2\sqrt w=-\sqrt w .
$$
Therefore
$$
A=-E[\nabla_\beta\psi]=-E\Bigl[-\sqrt{w}\,XX^T\Bigr]=E\bigl[\sqrt{w}\,XX^T\bigr]
=E\Bigl[\sqrt{\pi(1-\pi)}\;XX^T\Bigr].
$$

**Sandwich.** With $A=E[\sqrt w\,XX^T]$ and $B=E[XX^T]$,
$$
\boxed{\;V_{\beta^*}=A^{-1}BA^{-1}=\Bigl(E[\sqrt{w}\,XX^T]\Bigr)^{-1}\,E[XX^T]\,\Bigl(E[\sqrt{w}\,XX^T]\Bigr)^{-1},
\qquad w=\pi(1-\pi).\;}
$$

**The MLE covariance $U_{\beta^*}$.** For comparison, the logistic-MLE score is $s_i=(Y_i-\pi_i)X_i$ with information
$$
U_{\beta^*}^{-1}=I(\beta^*)=E\bigl[w\,XX^T\bigr]\quad\Longrightarrow\quad U_{\beta^*}=\bigl(E[w\,XX^T]\bigr)^{-1}.
$$
(The MLE is itself a sandwich, but under correct specification bread $=$ meat $=I$, collapsing to the inverse information.)

### Proof that $V_{\beta^*}\ge U_{\beta^*}$

This is the classical statement that the MLE is the **efficient** member of this family of unbiased estimating equations; any other unbiased estimating function gives a covariance no smaller. We prove it directly.

Consider the general linearly-weighted unbiased estimating function $\frac1n\sum_i (Y_i-\pi_i)\,h(X_i)$ where $h:\mathbb R^p\to\mathbb R^{p}$ is a fixed (matrix-valued) weight; here our estimator uses $h(X)=X/\sqrt{w}$ while the MLE uses $h(X)=X$. For any such estimator the sandwich covariance is $A_h^{-1}B_hA_h^{-1}$ with (using $\operatorname{Var}(Y\mid X)=w$ and $\nabla_\beta\pi=wX^T$)
$$
A_h=E\bigl[h(X)\,w\,X^T\bigr],\qquad B_h=E\bigl[h(X)\,w\,h(X)^T\bigr].
$$
For our estimator $h=X/\sqrt w$: $A=E[\sqrt w XX^T]$, $B=E[XX^T]$ — matching above. For the MLE $h=X$: $A=B=E[wXX^T]=I$.

Now invoke a Cauchy–Schwarz (information-inequality) argument. For random matrices/vectors, the generalized Cauchy–Schwarz inequality states that for any (suitable) $U,W$,
$$
E[UW^T]\,\bigl(E[WW^T]\bigr)^{-1}\,E[WU^T]\ \preceq\ E[UU^T].
$$
Apply it with the score-direction $W=\sqrt w\,X$ (so $E[WW^T]=I=U_{\beta^*}^{-1}$) and with $U=\sqrt w\,h(X)=\sqrt w\cdot X/\sqrt w=X$ for our estimator, i.e. $U=X$:
$$
E[U W^T]=E[X\,\sqrt w\,X^T]=E[\sqrt w\,XX^T]=A,\qquad
E[U U^T]=E[XX^T]=B,\qquad E[WW^T]=I .
$$
The inequality gives
$$
A\,I^{-1}A^T=A\,I\,A=A I A\ \preceq\ B,
$$
wait — we use it in the efficiency direction. The cleanest equivalent statement of the information bound for unbiased estimating equations (Godambe's theorem) is: among all weights $h$, the sandwich covariance $A_h^{-1}B_hA_h^{-1}$ is minimized (in the Loewner order) by the choice $h\propto$ the true score direction, $h(X)=X$ (the MLE), and the minimum equals $I^{-1}=U_{\beta^*}$. Concretely, for any $h$,
$$
A_h^{-1}B_hA_h^{-1}\ \succeq\ \bigl(E[wXX^T]\bigr)^{-1}=U_{\beta^*}.
\tag{Godambe}
$$

*Direct verification of (Godambe) for our $h$.* We must show
$$
A^{-1}BA^{-1}\succeq I^{-1},\qquad A=E[\sqrt w XX^T],\ B=E[XX^T],\ I=E[wXX^T].
$$
Equivalently (conjugating by $A\succ0$, which preserves the Loewner order), this is
$$
B\ \succeq\ A\,I^{-1}A,\qquad\text{i.e.}\qquad E[XX^T]\ \succeq\ E[\sqrt w XX^T]\,\bigl(E[wXX^T]\bigr)^{-1}E[\sqrt w XX^T].
$$
This is exactly the generalized Cauchy–Schwarz inequality
$$
E[UW^T]\bigl(E[WW^T]\bigr)^{-1}E[WU^T]\preceq E[UU^T]
$$
with the identifications
$$
U=X,\qquad W=\sqrt w\,X:\quad
E[UU^T]=E[XX^T]=B,\ \ E[WW^T]=E[wXX^T]=I,\ \ E[UW^T]=E[\sqrt w XX^T]=A.
$$
Hence $A I^{-1}A\preceq B$, and conjugating by $A^{-1}$ yields
$$
\boxed{\,I^{-1}\preceq A^{-1}BA^{-1},\quad\text{i.e.}\quad V_{\beta^*}\ \ge\ U_{\beta^*}\ \ (\text{difference } V_{\beta^*}-U_{\beta^*}\succeq0).\,}
$$

*Proof of the generalized Cauchy–Schwarz used.* For any vectors $a$, set $Z=a^T\bigl(U-A I^{-1}W\bigr)$. Then $E[Z^2]\ge0$ expands to
$$
a^T\Bigl(E[UU^T]-E[UW^T]I^{-1}E[WU^T]-E[UW^T]I^{-1}E[WU^T]+E[UW^T]I^{-1}E[WW^T]I^{-1}E[WU^T]\Bigr)a .
$$
Since $E[WW^T]=I$, the last two terms combine to $-E[UW^T]I^{-1}E[WU^T]$ once; collecting,
$$
0\le a^T\bigl(E[UU^T]-A I^{-1}A^T\bigr)a\quad\forall a
\;\Longrightarrow\; E[UU^T]\succeq A I^{-1}A^T = A I^{-1}A,
$$
using $A=A^T$ here (both $E[\sqrt w XX^T]$ and the symmetric construction). $\qquad\blacksquare$

(Equality, hence efficiency, holds iff $U=AI^{-1}W$ a.s., i.e. $X\propto\sqrt w\cdot\sqrt w X$ in the relevant sense, which forces $w$ constant — only when $\pi(X;\beta^*)$ is constant across the support, a degenerate case. Generically $V_{\beta^*}\succ U_{\beta^*}$ strictly.)

### Is the result intuitive?

**Yes.** Under a correctly specified model the MLE is asymptotically efficient: it attains the Cramér–Rao / Godambe information bound, so its asymptotic covariance $U_{\beta^*}=I(\beta^*)^{-1}$ is the smallest achievable among all regular (asymptotically unbiased) estimators, in particular among all unbiased estimating equations of the form $\sum_i (Y_i-\pi_i)h(X_i)=0$. The estimator $\tilde\beta$ is one such competitor that uses the *wrong* weighting: it down-weights each residual by $1/\sqrt{w_i}=1/\sqrt{\pi_i(1-\pi_i)}$ instead of by the efficient score weight. Equivalently, the MLE weights the score contribution of each observation by its information $w_i$ (heteroskedasticity-optimal weighting, à la GLS/Gauss–Markov), whereas $\tilde\beta$ uses a suboptimal weighting; using anything but the variance-optimal weights can only inflate the asymptotic variance. So $V_{\beta^*}\ge U_{\beta^*}$ is exactly what efficiency of the MLE predicts. The two coincide only in the degenerate case where the conditional variance $w$ is constant over the covariate support (no information to gain from re-weighting).

---

## Summary of answers

- **(i)** $\displaystyle \kappa(\beta)=\frac2n\sum_{i=1}^n \exp\!\bigl(-\tfrac12(2Y_i-1)X_i^T\beta\bigr)$ — the (convex) exponential loss on $\pm1$ labels; $\tilde\beta=\arg\min\kappa$.
- **(ii)** $\tilde\beta\xrightarrow{p}\beta^*$, because the estimating function is unbiased ($\Psi(\beta^*)=0$) with $\beta^*$ the unique zero (full-rank design $E\,XX^T\succ0$), via the convexity/$Z$-estimator consistency theorem.
- **(iii)** $\sqrt n(\tilde\beta-\beta^*)\xrightarrow{d}N(0,V_{\beta^*})$ with the sandwich $V_{\beta^*}=A^{-1}BA^{-1}$, $A=-\nabla_\beta\Psi(\beta^*)$, $B=E[\psi\psi^T]|_{\beta^*}$.
- **(iv)** $A=E[\sqrt{\pi(1-\pi)}\,XX^T]$, $B=E[XX^T]$, so
$$
V_{\beta^*}=\bigl(E[\sqrt{w}\,XX^T]\bigr)^{-1}E[XX^T]\bigl(E[\sqrt{w}\,XX^T]\bigr)^{-1},\quad w=\pi(1-\pi),
$$
and $V_{\beta^*}\ge U_{\beta^*}=\bigl(E[w\,XX^T]\bigr)^{-1}$ in the Loewner order, by the generalized Cauchy–Schwarz / Godambe information inequality. This is intuitive: the MLE uses the efficient (information-optimal) weighting and is asymptotically efficient, so any alternative unbiased estimating equation, including this Pearson-standardized one, has variance no smaller.
