# 2018 Summer Probability Q1

**Setup.** Let $X_1, X_2 \overset{\text{iid}}{\sim} \mathrm{Uniform}[0,1]$, let $\bar X = \tfrac{1}{2}(X_1+X_2)$, and define
$$
T = \max\{X_1, \bar X\}.
$$

**Key structural observation.** Compare $X_1$ and $\bar X$:
$$
\bar X \ge X_1 \iff \tfrac{X_1+X_2}{2} \ge X_1 \iff X_2 \ge X_1 .
$$
Hence there are two branches, each occurring with probability $\tfrac12$ by symmetry:

- **Branch A** ($X_2 < X_1$): then $\bar X < X_1$, so $T = X_1$.
- **Branch B** ($X_2 \ge X_1$): then $\bar X \ge X_1$, so $T = \bar X = \tfrac{X_1+X_2}{2}$.

This decomposition drives every part.

---

## (a) CDF of $T$

Since $T = \max\{X_1,\bar X\}$,
$$
F_T(t) = P(T \le t) = P\big(X_1 \le t,\ \bar X \le t\big)
= P\big(X_1 \le t,\ X_1 + X_2 \le 2t\big),\qquad 0\le t\le 1 .
$$
Because $(X_1,X_2)$ is uniform on the unit square, $F_T(t)$ equals the **area** of the region
$$
R_t = \{(x_1,x_2)\in[0,1]^2 : x_1 \le t,\ x_1 + x_2 \le 2t\}.
$$
For fixed $x_1\in[0,t]$, the variable $x_2$ runs over $[0,\ \min(1,\,2t-x_1)]$.

**Case 1: $0 \le t \le \tfrac12$.** Here $2t \le 1$ and $x_1\le t$ give $2t-x_1 \le 2t \le 1$, so the upper limit is simply $2t-x_1$:
$$
F_T(t) = \int_0^t (2t - x_1)\,dx_1 = 2t\cdot t - \tfrac{t^2}{2} = \frac{3t^2}{2}.
$$

**Case 2: $\tfrac12 \le t \le 1$.** Now $2t - x_1 > 1$ for $x_1 < 2t-1$, where the cap at $1$ binds. Split $x_1$ at $a = 2t-1 \ge 0$:
$$
F_T(t) = \int_0^{2t-1} 1\,dx_1 + \int_{2t-1}^{t} (2t-x_1)\,dx_1
= (2t-1) + \Big[\tfrac{(2t-1)^2}{2}\Big]
= -\frac{t^2}{2} + 2t - \frac12 .
$$
(The bracketed integral evaluates to $2t(t-(2t-1)) - \tfrac12\big(t^2-(2t-1)^2\big) = \tfrac12(2t-1)^2$.)

**Final CDF.**
$$
\boxed{\,F_T(t) =
\begin{cases}
0, & t<0,\\[4pt]
\dfrac{3t^2}{2}, & 0\le t \le \tfrac12,\\[8pt]
-\dfrac{t^2}{2} + 2t - \dfrac12, & \tfrac12 \le t \le 1,\\[8pt]
1, & t>1.
\end{cases}}
$$
Checks: $F_T(\tfrac12)=\tfrac38$ from both pieces (continuous), and $F_T(1)=1$. Differentiating gives the density
$$
f_T(t) =
\begin{cases}
3t, & 0\le t\le \tfrac12,\\
2-t, & \tfrac12\le t\le 1,
\end{cases}
$$
which is continuous at $t=\tfrac12$ ($f_T(\tfrac12)=\tfrac32$) and integrates to $1$.

---

## (b) $\mathbb{E}[T]$

Using the density from (a),
$$
\mathbb{E}[T] = \int_0^{1/2} t\,(3t)\,dt + \int_{1/2}^{1} t\,(2-t)\,dt .
$$
First integral: $\int_0^{1/2} 3t^2\,dt = t^3\big|_0^{1/2} = \tfrac18$.

Second integral:
$$
\int_{1/2}^{1} (2t - t^2)\,dt = \Big[t^2 - \tfrac{t^3}{3}\Big]_{1/2}^{1}
= \Big(1 - \tfrac13\Big) - \Big(\tfrac14 - \tfrac{1}{24}\Big)
= \tfrac{2}{3} - \tfrac{5}{24} = \tfrac{11}{24}.
$$
Therefore
$$
\mathbb{E}[T] = \frac18 + \frac{11}{24} = \frac{3}{24} + \frac{11}{24} = \boxed{\dfrac{7}{12}} \approx 0.5833 .
$$

*(Sanity check: $\mathbb{E}[X_1]=\tfrac12$ and $T\ge X_1$, so $\mathbb{E}[T]>\tfrac12$, consistent.)*

---

## (c) $\mathbb{E}[X_1 \mid T = t]$

We need the conditional distribution of $X_1$ given $T=t$. Use the two-branch decomposition. The joint law of $(X_1,X_2)$ has density $1$ on the unit square.

**Branch A** ($X_2 < X_1$): here $T = X_1$, so conditioning on $T=t$ forces $X_1 = t$ *exactly*. The "density of $T$ contributed by branch A at $t$" is obtained by fixing $X_1=t$ and letting $X_2$ range over $\{X_2<X_1\}=[0,t]$:
$$
f_{T,A}(t) = \underbrace{1}_{\text{dens. of }X_1\text{ at }t}\cdot \underbrace{P(X_2<t)}_{=\,t} = t .
$$
Thus, conditionally on $T=t$, branch A places an **atom at $X_1=t$**.

**Branch B** ($X_2\ge X_1$): here $T=\tfrac{X_1+X_2}{2}$. For fixed $X_1=x$, the map $X_2\mapsto T=\tfrac{x+X_2}{2}$ has $dX_2 = 2\,dT$, so the joint density of $(X_1, T)$ on this branch is $1\cdot 2 = 2$. The constraints are $X_2 = 2t-x \ge x$ (i.e. $x\le t$) and $0\le X_2\le 1$ (i.e. $x \ge 2t-1$), together with $x\ge 0$. So $x$ ranges over $[\max(0,2t-1),\ t]$ with density $2$. The branch-B contribution to $f_T$ is
$$
f_{T,B}(t) = 2\big(t - \max(0,2t-1)\big).
$$

**Total** $f_T(t) = f_{T,A}(t) + f_{T,B}(t)$:
- $t\le\tfrac12$: $f_T = t + 2t = 3t$ ✓
- $t\ge\tfrac12$: $f_T = t + 2(t-(2t-1)) = t + 2(1-t) = 2 - t$ ✓

both matching part (a). The **conditional density of $X_1$ given $T=t$** is the mixture
$$
X_1\mid T=t \;\sim\; \frac{t}{f_T(t)}\,\delta_{\{x=t\}} \;+\; \frac{2}{f_T(t)}\,\mathbf 1\{\,\max(0,2t-1)\le x\le t\,\}\,dx .
$$

### Case $0\le t\le \tfrac12$  (here $\max(0,2t-1)=0$, $f_T=3t$)

$$
\mathbb{E}[X_1\mid T=t] = \frac{1}{3t}\Big( \underbrace{t\cdot t}_{\text{atom}} + \int_0^t x\cdot 2\,dx\Big)
= \frac{1}{3t}\big(t^2 + t^2\big) = \frac{2t^2}{3t} = \frac{2t}{3}.
$$

### Case $\tfrac12\le t\le 1$  (here $\max(0,2t-1)=2t-1$, $f_T=2-t$)

$$
\int_{2t-1}^{t} 2x\,dx = t^2 - (2t-1)^2 = t^2 - (4t^2-4t+1) = -3t^2 + 4t - 1,
$$
so
$$
\mathbb{E}[X_1\mid T=t] = \frac{1}{2-t}\Big(t\cdot t + (-3t^2+4t-1)\Big)
= \frac{-2t^2 + 4t - 1}{2-t} = \frac{2t^2 - 4t + 1}{t-2}.
$$
Polynomial division ($2t^2-4t+1 = (t-2)(2t) + 1$) gives the clean form
$$
\mathbb{E}[X_1\mid T=t] = 2t - \frac{1}{\,2-t\,}.
$$

**Final answer.**
$$
\boxed{\;\mathbb{E}[X_1\mid T=t] =
\begin{cases}
\dfrac{2t}{3}, & 0\le t\le \tfrac12,\\[8pt]
2t - \dfrac{1}{2-t}, & \tfrac12 \le t\le 1.
\end{cases}}
$$
Both pieces agree at $t=\tfrac12$: $\tfrac{2}{3}\cdot\tfrac12 = \tfrac13$ and $1 - \tfrac{1}{3/2} = 1-\tfrac23 = \tfrac13$. At $t=1$, $\mathbb{E}[X_1\mid T=1]=2-1=1$, as expected ($T=1$ forces $X_1=1$). Numerical checks against simulation: $t=0.3\!\to\!0.20$, $t=0.5\!\to\!0.333$, $t=0.7\!\to\!0.631$ ✓.

---

## (d) $\operatorname{Var}[X_1 \mid T = t]$

Use $\operatorname{Var} = \mathbb{E}[X_1^2\mid T=t] - \big(\mathbb{E}[X_1\mid T=t]\big)^2$, with the same mixture. The atom at $x=t$ contributes $t^2\cdot\frac{t}{f_T} = \frac{t^3}{f_T}$ to $\mathbb{E}[X_1^2\mid T=t]$.

### Case $0\le t\le\tfrac12$  ($f_T=3t$)

$$
\mathbb{E}[X_1^2\mid T=t] = \frac{1}{3t}\Big(t^3 + \int_0^t 2x^2\,dx\Big)
= \frac{1}{3t}\Big(t^3 + \tfrac{2}{3}t^3\Big) = \frac{1}{3t}\cdot \tfrac{5}{3}t^3 = \frac{5t^2}{9}.
$$
$$
\operatorname{Var}[X_1\mid T=t] = \frac{5t^2}{9} - \Big(\frac{2t}{3}\Big)^2 = \frac{5t^2}{9} - \frac{4t^2}{9} = \frac{t^2}{9}.
$$

### Case $\tfrac12\le t\le 1$  ($f_T=2-t$)

$$
\int_{2t-1}^{t} 2x^2\,dx = \frac{2}{3}\big(t^3 - (2t-1)^3\big).
$$
With $(2t-1)^3 = 8t^3 - 12t^2 + 6t - 1$,
$$
t^3 - (2t-1)^3 = -7t^3 + 12t^2 - 6t + 1,\quad\Rightarrow\quad
\int = \frac{2}{3}\big(-7t^3 + 12t^2 - 6t + 1\big).
$$
Then
$$
\mathbb{E}[X_1^2\mid T=t] = \frac{1}{2-t}\Big(t^3 + \tfrac{2}{3}(-7t^3+12t^2-6t+1)\Big)
= \frac{1}{2-t}\cdot\frac{-11t^3 + 24t^2 - 12t + 2}{3}.
$$
Subtracting $\big(\mathbb{E}[X_1\mid T=t]\big)^2 = \big(\tfrac{2t^2-4t+1}{t-2}\big)^2$ and simplifying (the algebra factors neatly) gives
$$
\operatorname{Var}[X_1\mid T=t] = \frac{(1-t)^3(1+t)}{3\,(2-t)^2}.
$$

**Final answer.**
$$
\boxed{\;\operatorname{Var}[X_1\mid T=t] =
\begin{cases}
\dfrac{t^2}{9}, & 0\le t\le \tfrac12,\\[10pt]
\dfrac{(1-t)^3(1+t)}{3\,(2-t)^2}, & \tfrac12 \le t\le 1.
\end{cases}}
$$
Checks: at $t=\tfrac12$, the first piece gives $\tfrac{(1/2)^2}{9}=\tfrac{1}{36}\approx 0.0278$; the second gives $\frac{(1/2)^3(3/2)}{3(3/2)^2} = \frac{(1/8)(3/2)}{3\cdot 9/4} = \frac{3/16}{27/4} = \frac{1}{36}$ — continuous ✓. At $t=1$, variance $=0$ (the atom forces $X_1=1$) ✓. Both pieces are nonnegative on their ranges, and match simulation ($t=0.3\!\to\!0.010$, $t=0.5\!\to\!0.0278$, $t=0.7\!\to\!0.0091$) ✓.

---

## Summary of results

| Part | Result |
|------|--------|
| (a) | $F_T(t)=\tfrac{3t^2}{2}$ on $[0,\tfrac12]$; $\;-\tfrac{t^2}{2}+2t-\tfrac12$ on $[\tfrac12,1]$ |
| (b) | $\mathbb{E}[T]=\dfrac{7}{12}$ |
| (c) | $\mathbb{E}[X_1\mid T=t]=\tfrac{2t}{3}$ on $[0,\tfrac12]$; $\;2t-\tfrac{1}{2-t}$ on $[\tfrac12,1]$ |
| (d) | $\operatorname{Var}[X_1\mid T=t]=\tfrac{t^2}{9}$ on $[0,\tfrac12]$; $\;\dfrac{(1-t)^3(1+t)}{3(2-t)^2}$ on $[\tfrac12,1]$ |

**Theorems / tools used:** definition of CDF and joint distribution of independent uniforms (area computation on the unit square), the fundamental theorem of calculus (density via differentiation of the CDF), the law of the unconscious statistician for $\mathbb{E}[T]$, a change-of-variables / Jacobian argument to obtain the joint density of $(X_1,T)$ on the continuous branch, and the mixture (atom + continuous) representation of the conditional distribution together with the identity $\operatorname{Var}=\mathbb{E}[X_1^2]-(\mathbb{E}[X_1])^2$.
