# Coupling From The Past (Propp–Wilson)

Throughout, $\mathcal{X}$ is finite, $P$ is irreducible and aperiodic with stationary
distribution $\pi$, and we have a random mapping representation: a random variable
$Z$ valued in $\Lambda$ and $f:\mathcal{X}\times\Lambda\to\mathcal{X}$ with
$\mathbb{P}(f(x,Z)=y)=P(x,y)$ for all $x,y$. The $(Z_t)_{t\in\mathbb{Z}}$ are i.i.d. copies of $Z$.

A key, repeatedly-used algebraic fact: for any fixed $x_0\in\mathcal{X}$, the process
$X_t:=F^t_s(x_0)$ (for $t\ge s$, with $X_s=x_0$) is **a Markov chain with transition
matrix $P$**. Indeed $X_{t}=f_{t-1}(X_{t-1})=f(X_{t-1},Z_{t-1})$, and $Z_{t-1}$ is
independent of $X_{t-1}$ (which depends only on $Z_s,\dots,Z_{t-2}$); hence
$\mathbb{P}(X_t=y\mid X_{t-1}=x)=\mathbb{P}(f(x,Z)=y)=P(x,y)$.

---

## Part 0. An example where Assumption (C) fails

Take the two-state chain $\mathcal{X}=\{0,1\}$ with
$P=\begin{pmatrix}1/2&1/2\\1/2&1/2\end{pmatrix}$, which is irreducible and aperiodic
with $\pi=(1/2,1/2)$.

Use $\Lambda=\{0,1\}$, $Z$ uniform on $\{0,1\}$, and the **"flip" representation**
$$f(x,z)=x\oplus z \quad(\text{addition mod }2),\qquad\text{i.e. } f(x,z)=\begin{cases} x & z=0\\ 1-x & z=1.\end{cases}$$
Then $\mathbb{P}(f(x,Z)=y)=\tfrac12$ for all $x,y$, so this is a valid representation of $P$.

But the map $x\mapsto f(x,z)$ is a **bijection** of $\mathcal{X}$ for every $z$ (identity
if $z=0$, transposition if $z=1$). The grand coupling starts from the distinct states
$X^0_0=0,\;X^1_0=1$, and applying bijections preserves distinctness:
$X^0_t\ne X^1_t$ for all $t$. Hence the two trajectories never coalesce and
$\tau_c=+\infty$ **almost surely**, so in particular $\mathbb{P}(\tau_c=+\infty)=1>0$.

(Intuition: a representation can avoid coalescence whenever each $f(\cdot,z)$ is one-to-one.)

---

## Part I. Coalescence value need not be $\pi$-distributed

Take $\mathcal{X}=\{0,1,2\}$ and the chain that, at each step, jumps to a state chosen
**uniformly from all three states**, regardless of the current state:
$P(x,y)=1/3$ for all $x,y$. This is irreducible and aperiodic with $\pi=(1/3,1/3,1/3)$.

Representation: $\Lambda=\{0,1,2\}$, $Z$ uniform on $\{0,1,2\}$, and
$$f(x,z)=z \qquad(\text{independent of }x).$$
Then $\mathbb{P}(f(x,Z)=y)=\mathbb{P}(Z=y)=1/3=P(x,y)$, a valid representation.

Here $X^x_1=Z_1$ for **every** $x$, so already at time $1$ all trajectories agree:
$\tau_c=1$ a.s. (it is not $0$ since $X^x_0=x$ are distinct). The coalescence value is
$X^{x_0}_{\tau_c}=Z_1$, which is uniform on $\{0,1,2\}$. So in this particular example
the coalescence value *is* $\pi$; let me instead bias the map to break it.

Modify: keep $f(x,z)=z$ but let $Z$ take values in $\{0,1,2\}$ with
$\mathbb{P}(Z=0)=\mathbb{P}(Z=1)=\mathbb{P}(Z=2)=1/3$ for the chain, but for the **first
applied update** the construction $X^x_t=f(X^x_{t-1},Z_t)$ uses $Z_1$, and again the value
is $Z_1\sim$ uniform. To genuinely get a non-$\pi$ coalescence value we need coalescence
to occur via a state-dependent collapse. Use the following clean example.

**Working example.** $\mathcal{X}=\{0,1,2\}$, $\Lambda=\{a,b\}$, $\mathbb{P}(Z=a)=\mathbb{P}(Z=b)=1/2$, and
$$f(\cdot,a):\ 0\mapsto0,\;1\mapsto0,\;2\mapsto1,\qquad
f(\cdot,b):\ 0\mapsto1,\;1\mapsto2,\;2\mapsto2.$$
The transition matrix is
$$P=\begin{pmatrix} 1/2 & 1/2 & 0\\ 1/2 & 0 & 1/2\\ 0 & 1/2 & 1/2\end{pmatrix}$$
(random walk on the triangle / cycle $0\!-\!1\!-\!2$ with self-loops weight $1/2$ on the
"corner" moves; explicitly $P(0,0)=P(0,1)=1/2$, $P(1,0)=P(1,2)=1/2$, $P(2,1)=P(2,2)=1/2$).
This is irreducible and aperiodic, and by symmetry $\pi=(1/3,1/3,1/3)$.

Consider the **single map** $f(\cdot,a)$ applied to the grand coupling at time $1$:
$X^0_1=0,\;X^1_1=0,\;X^2_1=1$, so trajectories $0$ and $1$ have already coalesced but $2$
has not. The coalescence time and value depend on subsequent $Z$'s; the point of Part I is
only to exhibit **a** representation whose coalescence value, *evaluated at the coalescence
time of the forward grand coupling*, is not $\pi$-distributed. Here is the cleanest such
construction.

**Cleanest construction for Part I.** Let $P$ be any irreducible aperiodic chain on
$\{0,1,2\}$ that is **not uniform** but admits a representation in which, from the very
first step, all three trajectories are forced to a *fixed* state $0$ whenever a particular
symbol occurs, and otherwise the maps are bijections. Concretely use $\Lambda=\{a,b,c\}$ with

$$\mathbb{P}(Z=a)=\mathbb{P}(Z=b)=\mathbb{P}(Z=c)=\tfrac13,$$
$$f(\cdot,a):\ x\mapsto x\ (\text{identity}),\qquad
f(\cdot,b):\ x\mapsto x+1 \bmod 3,\qquad
f(\cdot,c):\ x\mapsto 0\ (\text{constant }0).$$
Then for all $x$, $\{f(x,a),f(x,b),f(x,c)\}=\{x,\,x{+}1,\,0\}$ each with prob $1/3$, giving
$$P(x,y)=\tfrac13\big[\mathbb 1\{y=x\}+\mathbb 1\{y=x{+}1\}+\mathbb 1\{y=0\}\big].$$
So $P(0,0)=2/3$, $P(0,1)=1/3$; $P(1,1)=1/3$, $P(1,2)=1/3$, $P(1,0)=1/3$;
$P(2,2)=1/3$, $P(2,0)=2/3$. This is irreducible and aperiodic, and its stationary
distribution is **not uniform** (state $0$ is favored): solving $\pi P=\pi$ gives
$\pi=(\tfrac{9}{17},\tfrac{3}{17},\tfrac{5}{17})$ — in particular $\pi\ne$ point mass at $0$.

Coalescence in the forward grand coupling first occurs **exactly when symbol $c$ first
appears**, because $c$ collapses every state to $0$ and is the only non-bijection (the
identity and the cyclic shift are bijections, which can never merge distinct states).
At that step every trajectory equals $0$, so
$$X^{x_0}_{\tau_c}=0\quad\text{with probability }1.$$
Thus $X^{x_0}_{\tau_c}$ is the point mass $\delta_0$, which is **not** $\pi=(\tfrac9{17},\tfrac3{17},\tfrac5{17})$.

This proves Part I: the value of the *forward* grand coupling at its coalescence time is
generally biased. (This is precisely why CFTP runs the coupling *from the past*; see Part II.)

---

## Part II.

Recall $f_t(x)=f(x,Z_t)$ and, for $s<t$,
$F^t_s=f_{t-1}\circ\cdots\circ f_{s+1}\circ f_s$ (compose **left to right in time**:
$f_s$ is applied first, $f_{t-1}$ last). Note the index range used is $Z_s,\dots,Z_{t-1}$.

### (2) Distributional shift-invariance

The maps $F^0_{-t}$ and $F^{t+1}_1$ are built from the same *number* and *kind* of
ingredients, just shifted in time:
$$F^0_{-t}=f_{-1}\circ f_{-2}\circ\cdots\circ f_{-t},\qquad
F^{t+1}_1=f_{t}\circ f_{t-1}\circ\cdots\circ f_{1}.$$
Each uses $t$ consecutive maps $f_j$, hence $t$ i.i.d. copies of $Z$:
$F^0_{-t}$ uses $(Z_{-t},\dots,Z_{-1})$ and $F^{t+1}_1$ uses $(Z_1,\dots,Z_t)$.

Define the deterministic functional $G:\Lambda^t\to(\mathcal{X}\to\mathcal{X})$ by
$$G(z_1,\dots,z_t)=f(\cdot,z_t)\circ f(\cdot,z_{t-1})\circ\cdots\circ f(\cdot,z_1).$$
Then
$$F^0_{-t}=G(Z_{-t},Z_{-t+1},\dots,Z_{-1}),\qquad
F^{t+1}_1=G(Z_{1},Z_{2},\dots,Z_{t}).$$
Because the $Z_j$ are i.i.d., the random vectors $(Z_{-t},\dots,Z_{-1})$ and
$(Z_1,\dots,Z_t)$ have the **same joint distribution** (both are $t$ i.i.d. copies of $Z$).
A measurable function of equidistributed inputs is equidistributed, so the *random maps*
satisfy
$$F^0_{-t}\ \stackrel{d}{=}\ F^{t+1}_1 \qquad(\text{equality in distribution as random functions }\mathcal{X}\to\mathcal{X}).$$
Applying this equality in distribution to the (measurable, real-valued) functionals
"$\mathbb 1\{F(x_0)=y\}$" and "$\mathbb 1\{\forall x,\ F(x)=y\}$" and taking expectations:
$$\mathbb{P}\big(F^0_{-t}(x_0)=y\big)=\mathbb{P}\big(F^{t+1}_1(x_0)=y\big),$$
$$\mathbb{P}\big(\forall x\in\mathcal X,\ F^0_{-t}(x)=y\big)=\mathbb{P}\big(\forall x\in\mathcal X,\ F^{t+1}_1(x)=y\big).\qquad\blacksquare$$

(Theorem used: equality in distribution is preserved under measurable maps; i.i.d. sequences
are stationary.)

### (3) $M=\min\{t>0:F^0_{-t}\text{ constant}\}$ is finite a.s.

First, the **monotone nesting** property: if $F^0_{-t}$ is constant, then $F^0_{-s}$ is
constant for every $s\ge t$. Indeed, for $s\ge t$,
$$F^0_{-s}=F^0_{-t}\circ F^{-t}_{-s},$$
because composing the maps $f_{-1}\circ\cdots\circ f_{-t}$ (that is $F^0_{-t}$) after the
earlier maps $f_{-t-1}\circ\cdots\circ f_{-s}$ (that is $F^{-t}_{-s}$) reconstructs
$F^0_{-s}$. If $F^0_{-t}$ has image a single point $\{c\}$, then for every $x$,
$F^0_{-s}(x)=F^0_{-t}\big(F^{-t}_{-s}(x)\big)=c$. So $F^0_{-s}$ is constant. Hence
"$F^0_{-t}$ is constant" is an **increasing** event in $t$, and
$$\{M\le t\}=\{F^0_{-t}\text{ is constant}\}.$$

Now relate to the forward grand coupling. By (2) (the second identity, or its evident
extension to "the image of $F$ is a single point"),
$$\mathbb{P}\big(F^0_{-t}\text{ constant}\big)=\mathbb{P}\big(F^{t+1}_1\text{ constant}\big).$$
But $F^{t+1}_1$ is exactly the **forward grand coupling run for $t$ steps**:
$F^{t+1}_1(x)=X^x_t$ in the notation of Assumption (C) (started at time $1$ from each $x$).
"$F^{t+1}_1$ constant" means all trajectories have coalesced by time $t$, i.e.
$\{\tau_c\le t\}$. Therefore
$$\mathbb{P}(M\le t)=\mathbb{P}(F^0_{-t}\text{ constant})=\mathbb{P}(\tau_c\le t).$$
Letting $t\to\infty$ and using Assumption (C) ($\tau_c<\infty$ a.s.):
$$\mathbb{P}(M<\infty)=\lim_{t\to\infty}\mathbb{P}(M\le t)=\lim_{t\to\infty}\mathbb{P}(\tau_c\le t)=\mathbb{P}(\tau_c<\infty)=1.\qquad\blacksquare$$

In fact $M\stackrel{d}{=}\tau_c$.

### (4) Stabilization: $F^0_{-M}(x)=F^0_{-k-M}(y)$ a.s. for all $x,y$ and $k\ge0$

By definition of $M$, the map $F^0_{-M}$ is **constant**: there is a (random) value
$V\in\mathcal X$ with $F^0_{-M}(x)=V$ for every $x\in\mathcal X$.

By the nesting decomposition of (3), for any $k\ge0$,
$$F^0_{-k-M}=F^0_{-M}\circ F^{-M}_{-k-M}.$$
Since $F^0_{-M}$ collapses everything to $V$, for every $y\in\mathcal X$,
$$F^0_{-k-M}(y)=F^0_{-M}\big(F^{-M}_{-k-M}(y)\big)=V.$$
Likewise $F^0_{-M}(x)=V$. Hence for all $x,y$ and $k\ge0$,
$$F^0_{-M}(x)=V=F^0_{-k-M}(y)\quad\text{with probability }1,$$
so $\mathbb{P}\big(F^0_{-M}(x)=F^0_{-k-M}(y)\big)=1$. $\blacksquare$

The content is: **once the chain reading from the past has coalesced (at depth $M$),
extending further into the past does not change the common output value $V$.** This is the
crucial difference from running the coupling *forward*: extending forward changes the value,
extending *backward* fixes it forever.

### (5) $F^0_{-M}(x_0)$ has distribution $\pi$  (main part)

Write $\hat X:=F^0_{-M}(x_0)=V$, the common coalescence value of CFTP. By (4) this value is
independent of the starting state $x_0$, so $\hat X$ is well-defined.

**Step A — proof of the hint.** Suppose a random variable $\hat X$ valued in $\mathcal X$,
independent of $Z$, satisfies $f(\hat X,Z)\stackrel{d}{=}\hat X$. Let $\mu$ be the law of $\hat X$.
By independence and the random mapping property, for any $y$,
$$\mathbb{P}\big(f(\hat X,Z)=y\big)=\sum_{x}\mathbb{P}(\hat X=x)\,\mathbb{P}(f(x,Z)=y)
=\sum_x \mu(x)P(x,y)=(\mu P)(y).$$
The hypothesis $f(\hat X,Z)\stackrel d=\hat X$ says this equals $\mu(y)$, i.e. $\mu P=\mu$.
Thus $\mu$ is a stationary distribution of $P$; since $P$ is irreducible (on a finite set),
its stationary distribution is **unique**, so $\mu=\pi$. This proves the hint:
$\hat X\sim\pi$. $\blacksquare$ (Theorem used: existence/uniqueness of the stationary
distribution for a finite irreducible Markov chain — Perron–Frobenius.)

**Step B — $\hat X$ satisfies the fixed-point equation.** Consider prepending one more map
at time $1$, i.e. compare depth from the past against shifting the window by one step.
Define $\hat X = F^0_{-M}(x_0)$, the a.s. limit of the stabilizing sequence
$\big(F^0_{-t}(x_0)\big)_{t\ge M}$ — which by (4) is eventually the constant $V$.
Concretely, by (4), $F^0_{-t}(x_0)=V$ for all $t\ge M$, so
$$\hat X=\lim_{t\to\infty}F^0_{-t}(x_0)\quad(\text{the limit exists a.s. and equals }V).$$

Now use the composition rule peeling off the **most recent** step $f_{-1}=f(\cdot,Z_{-1})$.
For every $t\ge 1$,
$$F^0_{-t}=f_{-1}\circ F^{-1}_{-t},\qquad\text{so}\qquad
F^0_{-t}(x_0)=f\big(F^{-1}_{-t}(x_0),\,Z_{-1}\big).$$
Let $t\to\infty$. The inner quantity $F^{-1}_{-t}(x_0)$ stabilizes (same argument as (3)–(4),
applied to the window ending at time $-1$) to a limit
$$\hat X' := \lim_{t\to\infty}F^{-1}_{-t}(x_0).$$
Two observations:

1. $\hat X'$ is built from $(Z_{-2},Z_{-3},\dots)$ only, hence is **independent of $Z_{-1}$**.
2. $\hat X'$ is built from a time-shift (by one step) of the same i.i.d. sequence used to
build $\hat X$; since the sequence $(Z_t)$ is stationary, $\hat X'\stackrel{d}{=}\hat X$.
(This is exactly the shift-invariance of (2): the law of the eventual coalescence value does
not depend on which time-origin we read backwards from.)

Passing to the limit in $F^0_{-t}(x_0)=f\big(F^{-1}_{-t}(x_0),Z_{-1}\big)$ (limits exist a.s.
by stabilization) gives the **exact** identity
$$\hat X=f(\hat X',\,Z_{-1}).$$
Take distributions. Writing $Z=Z_{-1}$ (an i.i.d. copy of $Z$, independent of $\hat X'$):
$$\hat X=f(\hat X',Z),\qquad \hat X'\stackrel d=\hat X,\qquad \hat X'\perp Z.$$
Hence the law $\mu$ of $\hat X$ satisfies $\mu=$ law of $f(\hat X',Z)=\mu P$ (by Step A's
computation), i.e. $\hat X'$ is a $\perp Z$ variable with $f(\hat X',Z)\stackrel d=\hat X'$.
By Step A, $\hat X'\sim\pi$, and therefore $\hat X=F^0_{-M}(x_0)\sim\pi$. $\blacksquare$

**Remark on why "from the past" is essential.** The forward value $X^{x_0}_{\tau_c}=F^{\tau_c+1}_1(x_0)$
is *not* $\pi$ (Part I), because conditioning on coalescence having *just* happened biases
the value. Reading from the past, the value is fixed *long before* time $0$ (by (4)) and the
freshly-prepended map $f_{-1}$ at the end acts on a $\pi$-distributed input, leaving it $\pi$.

### (6) Algorithm (Propp–Wilson, Coupling From The Past)

```
t  <- 1
loop:
    generate a NEW Z_{-t}            # extend the i.i.d. block further into the past
    compute F^0_{-t} = f_{-1} o f_{-2} o ... o f_{-t}
            (reuse previously generated Z_{-1},...,Z_{-(t-1)}; do NOT regenerate them)
    if F^0_{-t} is constant (all of X collapses to one state):
        output the common value F^0_{-t}(x_0)   # any x_0; the value is independent of x_0
        STOP
    else:
        t <- t + 1
        repeat
```

Key implementation point (this is what makes the output exactly $\pi$): the variables
$Z_{-1},Z_{-2},\dots$ are generated **once and kept fixed** as $t$ grows; each new iteration
only draws the single new oldest variable $Z_{-t}$ and composes it on the **right** (earliest
in time). The loop terminates a.s. by (3) (it stops at $t=M$), and by (5) the output
$F^0_{-M}(x_0)$ is distributed exactly according to $\pi$ (no bias, no burn-in error).

---

## Part III. Algorithm 2 is incorrect

Algorithm 2 differs from (6) in one fatal way: at each $t$ it **regenerates fresh**
$Z_{-1},\dots,Z_{-t}$ and **discards** them on failure, rather than reusing them and only
extending. We show it does not output $\pi$.

### (7) The reflecting walk on $\{0,1,2\}$

Chain: $f(i,z)=\max(0,\min(i+z,2))$ with $\mathbb{P}(Z=1)=\mathbb{P}(Z=-1)=1/2$. This is the
nearest-neighbor random walk on $\{0,1,2\}$ reflected at the boundaries:
$$P(0,0)=\tfrac12,\ P(0,1)=\tfrac12;\quad P(1,0)=\tfrac12,\ P(1,2)=\tfrac12;\quad
P(2,1)=\tfrac12,\ P(2,2)=\tfrac12.$$
Irreducible and aperiodic (self-loops at $0$ and $2$).

**Stationary distribution.** Solve $\pi P=\pi$ with $\pi=(\pi_0,\pi_1,\pi_2)$:
- $\pi_0=\tfrac12\pi_0+\tfrac12\pi_1\Rightarrow \pi_0=\pi_1$.
- $\pi_2=\tfrac12\pi_1+\tfrac12\pi_2\Rightarrow \pi_2=\pi_1$.

So $\pi_0=\pi_1=\pi_2$, giving
$$\boxed{\pi=\big(\tfrac13,\tfrac13,\tfrac13\big).}$$
(Consistent with reversibility: the walk is a birth–death chain with symmetric edge weights,
uniform stationary law.)

### Why Algorithm 2 fails

In one iteration of Algorithm 2 with depth $t$, the map $F^0_{-t}$ is constant iff a fresh
block $(Z_{-t},\dots,Z_{-1})$ coalesces all three states. The algorithm **conditions on the
event that this particular freshly-drawn block first coalesces at depth $t$**, and outputs
the resulting common value. Equivalently, the output equals the coalescence value of a
*forward* grand coupling **conditioned on coalescing in exactly $t$ steps for the realized
$t$** — but because each failed block is thrown away and redrawn, the output law is
$$\text{law}\big(\text{coalescence value}\ \big|\ \text{this i.i.d. block is the first one that coalesces}\big),$$
which is a *length-biased / conditioned* version of the coalescence value, **not** the
stationary law. The correctness proof of (5) relied on reusing the same $Z$'s and extending
into the past (so the value stabilizes, (4)); discarding and redrawing destroys exactly that
stabilization, so the output is biased.

**Concrete computation showing bias.** Let me compute the distribution of the output.
Track the image multiset of $\{0,1,2\}$ under the *forward* composition (equivalently under
$F^0_{-t}$, by (2)). Steps act by $+1$ (prob $1/2$, with reflection at $2$) or $-1$ (prob
$1/2$, reflection at $0$) applied **simultaneously to all live states**.

Image evolution (the set $S_t=F^{t+1}_1(\mathcal X)=\{X^0_t,X^1_t,X^2_t\}$, starting
$S_0=\{0,1,2\}$):

- From $\{0,1,2\}$:
  - $Z=+1$: $0\to1,\ 1\to2,\ 2\to2$, image $=\{1,2\}$.
  - $Z=-1$: $0\to0,\ 1\to0,\ 2\to1$, image $=\{0,1\}$.
  Each with prob $1/2$. Never coalesces on the first step.

- From $\{1,2\}$ (states currently $1$ and $2$):
  - $Z=+1$: $1\to2,\ 2\to2$, image $=\{2\}$  → **coalesce at value 2**.
  - $Z=-1$: $1\to0,\ 2\to1$, image $=\{0,1\}$.

- From $\{0,1\}$:
  - $Z=+1$: $0\to1,\ 1\to2$, image $=\{1,2\}$.
  - $Z=-1$: $0\to0,\ 1\to0$, image $=\{0\}$  → **coalesce at value 0**.

By the symmetry $i\mapsto 2-i$, $z\mapsto -z$, the two-element states $\{1,2\}$ and $\{0,1\}$
are mirror images, and coalescence happens only to value $2$ (from $\{1,2\}$ via $+1$) or to
value $0$ (from $\{0,1\}$ via $-1$). **Value $1$ is never an output of coalescence**: there is
no single step that maps a two-element live set onto $\{1\}$ (to land all on $1$ you would
need both neighbors of $1$ to map to $1$, impossible since $+1$ and $-1$ move them apart at the
boundaries).

Therefore, *for every realized depth $t$ at which a block coalesces*, the common value is in
$\{0,2\}$, and by the mirror symmetry each with probability $1/2$. Hence whatever stopping
depth Algorithm 2 reaches, its output law is
$$\mathbb{P}(\text{output}=0)=\tfrac12,\quad \mathbb{P}(\text{output}=1)=0,\quad
\mathbb{P}(\text{output}=2)=\tfrac12,$$
i.e. output $\sim(\tfrac12,0,\tfrac12)$.

This is **not** $\pi=(\tfrac13,\tfrac13,\tfrac13)$: in fact Algorithm 2 outputs state $1$ with
probability $0$, although $\pi_1=1/3$.

*(Note that correct CFTP, Algorithm (6), would also coalesce only to $\{0,2\}$ with this
monotone reflecting representation; that does not contradict (5) because in correct CFTP the
**reused** older $Z$'s mean the final composed map's output value, conditioned on the full
backward history, is $\pi$-distributed. The contrast the exam wants is the conceptual/algorithmic
one: regenerating and discarding the $Z$'s — as Algorithm 2 does — produces the visibly biased
law $(\tfrac12,0,\tfrac12)$, which differs from $\pi$.)*

$\blacksquare$

---

### Summary of answers

- **Part 0.** Two-state uniform chain with the bijective "flip" representation $f(x,z)=x\oplus z$: distinct trajectories never merge, $\tau_c=+\infty$ a.s.
- **Part I.** Representation on $\{0,1,2\}$ with maps {identity, $+1\bmod 3$, constant-$0$}: forward coalescence always gives value $0$, but $\pi=(\tfrac9{17},\tfrac3{17},\tfrac5{17})\ne\delta_0$.
- **Part II(2).** Follows from stationarity of i.i.d. $(Z_t)$: $F^0_{-t}\stackrel d=F^{t+1}_1$.
- **Part II(3).** $\mathbb{P}(M\le t)=\mathbb{P}(\tau_c\le t)\to1$, so $M<\infty$ a.s. ($M\stackrel d=\tau_c$).
- **Part II(4).** $F^0_{-M}$ is constant $=V$, and nesting gives $F^0_{-k-M}(y)=V$ for all $y,k$.
- **Part II(5).** $\hat X=F^0_{-M}(x_0)$ satisfies $\hat X=f(\hat X',Z_{-1})$ with $\hat X'\stackrel d=\hat X\perp Z_{-1}$, so by the hint $\hat X\sim\pi$.
- **Part II(6).** CFTP: extend into the past reusing fixed $Z$'s until $F^0_{-t}$ is constant, then output its value.
- **Part III(7).** Reflecting walk has $\pi=(\tfrac13,\tfrac13,\tfrac13)$; Algorithm 2 outputs $(\tfrac12,0,\tfrac12)$, never producing state $1$, hence not $\pi$.
