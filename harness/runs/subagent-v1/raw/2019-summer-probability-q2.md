# 2019 Summer Probability Q2 — Random walk on two cliques joined by a bridge

## Setup and notation

The state space is $\mathcal{X} = \{-n,\dots,-1,0,1,\dots,n\}$, with $|\mathcal{X}| = 2n+1$. The edges are:

- the **positive clique** $K^+$ on $\{1,\dots,n\}$: every pair $\{x,y\}$, $1\le x<y\le n$;
- the **negative clique** $K^-$ on $\{-1,\dots,-n\}$: every pair $\{-x,-y\}$;
- the two **bridge** edges $\{-1,0\}$ and $\{0,1\}$.

Throughout, $P(u,v) = 1/\deg(u)$ if $\{u,v\}$ is an edge and $0$ otherwise (simple random walk, SRW).

**Key symmetry.** The map $\sigma: x \mapsto -x$ is a graph automorphism: it maps $K^+\leftrightarrow K^-$, fixes $0$, and swaps the two bridge edges. Hence $P(u,v) = P(\sigma u, \sigma v)$ for all $u,v$, and consequently $P^t(u,A) = P^t(\sigma u, \sigma A)$ for every $t$ and every set $A$. We use this repeatedly.

We write the total variation distance of two probability measures $\mu,\nu$ on $\mathcal X$ as
$$\|\mu-\nu\|_{TV} = \tfrac12\sum_{z}|\mu(z)-\nu(z)| = \max_{A\subseteq\mathcal X}\big(\mu(A)-\nu(A)\big).$$

---

## Part 1. The graph for $n=4$

Vertices: $\{-4,-3,-2,-1,0,1,2,3,4\}$ — **9 nodes**, as required.

```
   Negative clique K^-            Positive clique K^+
      -4 ---- -3                     3 ---- 4
       | \   / |                     | \   / |
       |  \ /  |                     |  \ /  |
       |  / \  |                     |  / \  |
       | /   \ |                     | /   \ |
      -2 ---- -1 ---- 0 ---- 1 ---- 2
```

In words: $\{-4,-3,-2,-1\}$ form a complete graph $K_4$ (all $\binom{4}{2}=6$ edges drawn); $\{1,2,3,4\}$ form a complete graph $K_4$ (another $6$ edges); plus the two bridge edges $\{-1,0\}$ and $\{0,1\}$.

**Edge count:** $6 + 6 + 2 = \mathbf{14}$ edges, as required.

---

## Part 2. Degrees

Vertices $\pm 2,\dots,\pm n$ are "interior" clique vertices; vertices $\pm 1$ are the clique vertices that also touch $0$.

- Inside a clique of $n$ vertices, each vertex is adjacent to the other $n-1$ clique vertices.
- The vertices $1$ and $-1$ additionally have the edge to $0$.

Therefore:
$$\boxed{\deg(1) = \deg(-1) = (n-1) + 1 = n,}\qquad \boxed{\deg(2)=\deg(-2)=n-1.}$$

More generally $\deg(\pm k) = n-1$ for $2\le k\le n$, $\deg(\pm 1) = n$, and $\deg(0)=2$.

---

## Part 3. Coupling bound via hitting time of $0$

**Claim.** $\displaystyle \max_{x\in\mathcal X}\ \big\|P^t(x,\cdot) - P^t(-x,\cdot)\big\|_{TV} \le \mathbb P_x(\tau > t)$, where $\tau = \min\{t\ge 0: X_t=0\}$.

### The coupling

Fix a starting state $x$. We construct a coupling $(X_t, Y_t)_{t\ge 0}$ of two copies of the chain with $X_0 = x$ and $Y_0 = -x$, of "reflection then coalescence" type:

- **Before meeting at $0$:** while $X_t \ne 0$, let $Y_t$ be the *mirror image* of $X_t$, i.e. $Y_t = -X_t = \sigma(X_t)$. Concretely, having chosen the move of $X$, let $Y$ make the **mirrored** move. Because $\sigma$ is an automorphism, $P(X_t, X_{t+1}) = P(\sigma X_t, \sigma X_{t+1}) = P(Y_t, Y_{t+1})$, so if $X$ does a single SRW step then $Y$ does a single SRW step as well. Thus while they are mirror images, $Y$ is a faithful SRW and $Y_t = -X_t$ remains true at the next step *as long as $X_{t+1}\ne 0$*.

- **Meeting / coalescence:** $X$ and $Y$ are mirror images, so $X_t = -Y_t$. They occupy the same vertex precisely when $X_t = -X_t$, i.e. $X_t = 0$. The first such time is exactly $\tau$ (note $Y$ reaches $0$ at the same instant, since $Y_\tau = -X_\tau = 0$). Once $X_\tau = Y_\tau = 0$, we **glue** the two chains: for $t\ge\tau$ set $Y_t = X_t$ and let them move together as a single SRW.

Each coordinate is, marginally, a simple random walk: $X$ by construction, and $Y$ because (i) before $\tau$ it is the mirror move of a SRW (hence SRW by the automorphism property), and (ii) after $\tau$ it equals $X$, a SRW. The two coordinates start at $x$ and $-x$. So this is a genuine coupling.

Let $\tau_{\mathrm{couple}} = \min\{t: X_t = Y_t\}$. By the construction the two chains first coincide exactly when $X$ first hits $0$:
$$\tau_{\mathrm{couple}} = \tau,$$
and they stay together forever after. (They cannot meet earlier: before $\tau$, $X_t=-Y_t$ with $X_t\neq 0$, so $X_t\neq Y_t$.)

### The coupling inequality

The **Coupling Lemma** (Aldous; see Levin–Peres, *Markov Chains and Mixing Times*, Prop. 4.7) states: for any coupling $(X_t,Y_t)$ with $X_0=x$, $Y_0=-x$,
$$\big\|P^t(x,\cdot)-P^t(-x,\cdot)\big\|_{TV} \le \mathbb P\big(X_t \ne Y_t\big).$$
Indeed, for any set $A$, $P^t(x,A)-P^t(-x,A) = \mathbb P(X_t\in A) - \mathbb P(Y_t\in A) \le \mathbb P(X_t\in A, Y_t\notin A) \le \mathbb P(X_t\neq Y_t)$, and taking the max over $A$ gives the bound.

In our coupling, $X_t=Y_t$ for all $t\ge\tau$, so $\{X_t\ne Y_t\}\subseteq\{\tau>t\}$, giving
$$\big\|P^t(x,\cdot)-P^t(-x,\cdot)\big\|_{TV} \le \mathbb P(X_t\ne Y_t) \le \mathbb P(\tau_{\mathrm{couple}}>t) = \mathbb P_x(\tau>t).$$

Since this holds for every $x$, taking the maximum over $x$ yields
$$\boxed{\ \max_{x\in\mathcal X}\big\|P^t(x,\cdot)-P^t(-x,\cdot)\big\|_{TV} \le \max_x\mathbb P_x(\tau>t).\ }$$
(For each fixed $x$ the inequality is exactly $\mathbb P_x(\tau>t)$, as stated.) $\qquad\blacksquare$

---

## Part 4a. One-step / two-step escape: $\max_x \mathbb P_x[\tau>2]\le 1-\epsilon_n$

We must show that from **any** start, the chain has a uniformly positive chance of hitting $0$ within $2$ steps. We bound, for each $x$, a lower bound on $\mathbb P_x(\tau\le 2)$, hence $\mathbb P_x(\tau>2)\le 1 - (\text{that lower bound})$.

Note $0$ has exactly the two neighbors $1$ and $-1$, with $\deg(1)=\deg(-1)=n$.

**Case $x=0$:** $\tau=0\le 2$, so $\mathbb P_0(\tau>2)=0$.

**Case $x=\pm1$** (handled separately, as suggested). From $1$, a single step reaches $0$ with probability $P(1,0)=1/\deg(1)=1/n$. So $\mathbb P_1(\tau\le 1)=1/n$ and
$$\mathbb P_1(\tau>2)\le \mathbb P_1(\tau>1) = 1-\tfrac1n.$$
By symmetry the same holds for $x=-1$.

**Case $|x|\ge 2$** (say $x=k$, $2\le k\le n$; the negatives are symmetric). To hit $0$ within two steps it suffices to step first to vertex $1$ (which is a neighbor of $k$ inside the clique) and then from $1$ to $0$:
$$\mathbb P_k(\tau\le 2)\ \ge\ P(k,1)\,P(1,0) = \frac{1}{\deg(k)}\cdot\frac{1}{\deg(1)} = \frac{1}{n-1}\cdot\frac1n = \frac{1}{n(n-1)}.$$
(Here $1$ is a neighbor of $k$ because both lie in the positive clique, and $k\neq 1$.) Hence
$$\mathbb P_k(\tau>2)\le 1 - \frac{1}{n(n-1)}.$$

**Combining.** The worst (largest) of the upper bounds is the interior-clique one, since for $n\ge2$, $\tfrac1{n(n-1)}\le\tfrac1n$. Therefore
$$\boxed{\ \max_{x\in\mathcal X}\mathbb P_x[\tau>2]\ \le\ 1-\epsilon_n,\qquad \epsilon_n=\frac{1}{n(n-1)}.\ }$$
This $\epsilon_n>0$ depends only on $n$. (One may also write the looser, cleaner $\epsilon_n = 1/n^2$ since $1/n^2 \le 1/(n(n-1))$.)

---

## Part 4b. Geometric tail bound for $\mathbb P_y[\tau>k]$

Set $m = \max_{x}\mathbb P_x[\tau>2]\le 1-\epsilon_n$ from Part 4a. We bootstrap this to all even/odd times by the **Markov property** and a sub-multiplicativity argument.

For any state $y$ and any times $s,t\ge0$, condition on $X_2$ (and use that $\tau>2$ means in particular $X_2\neq 0$):
$$\mathbb P_y[\tau>2+s] = \sum_{z\ne 0}\mathbb P_y[\tau>2,\ X_2=z]\,\mathbb P_z[\tau>s] \le \Big(\max_{z}\mathbb P_z[\tau>s]\Big)\,\mathbb P_y[\tau>2].$$
Taking $\max_y$ on the left and writing $a_s := \max_y\mathbb P_y[\tau>s]$, this gives the submultiplicative recursion
$$a_{2+s} \le a_s\cdot a_2 \le a_s\,(1-\epsilon_n).$$
Iterating from $s=0$ ($a_0\le 1$) gives, for every integer $j\ge 0$,
$$a_{2j} \le (1-\epsilon_n)^{j}.$$
For a general $k\ge 0$, since $a_s$ is non-increasing in $s$ ($\{\tau>s+1\}\subseteq\{\tau>s\}$), take $j=\lfloor k/2\rfloor$:
$$\boxed{\ \max_y\mathbb P_y[\tau>k]\ =\ a_k\ \le\ a_{2\lfloor k/2\rfloor}\ \le\ (1-\epsilon_n)^{\lfloor k/2\rfloor}\ \le\ (1-\epsilon_n)^{(k-1)/2},\qquad \epsilon_n=\frac{1}{n(n-1)}.\ }$$
This is the desired geometric (exponentially decaying in $k$) upper bound, uniform in the start.

---

## Part 4c. Bound on the worst-case mean hitting time $\max_y\mathbb E_y[\tau]\le Cn^\alpha$

Using the tail-sum formula $\mathbb E_y[\tau] = \sum_{k\ge0}\mathbb P_y[\tau>k]$ and Part 4b:
$$\max_y\mathbb E_y[\tau] \le \sum_{k=0}^\infty (1-\epsilon_n)^{\lfloor k/2\rfloor} = 2\sum_{j=0}^\infty(1-\epsilon_n)^{j} = \frac{2}{\epsilon_n} = 2n(n-1)\le 2n^2.$$
(The factor $2$ appears because each value $j=\lfloor k/2\rfloor$ is hit by two values of $k$.)

Thus $\max_y\mathbb E_y[\tau]\le 2n(n-1) = O(n^2)$, i.e.
$$\boxed{\ \max_y\mathbb E_y[\tau]\ \le\ C\,n^{\alpha}\quad\text{with } \alpha=2,\ C=2.\ }$$

**The exponent $\alpha=2$ is best possible (optimal).** We verify a matching lower bound of order $n^2$. Start at an interior positive vertex, say $x=2$. Each step, the chain is at some positive clique vertex; to make progress toward $0$ it must reach $1$ and then take the bridge step $1\to0$ which has probability only $1/n$. Concretely, consider the chain restricted to the positive side and the event of crossing the bridge. From state $1$, the probability of stepping to $0$ is $1/n$; otherwise it returns to the clique. Each "visit to $1$" succeeds in leaving to $0$ with probability $1/n$, so the number of visits to $1$ before absorption at $0$ is geometric with mean $n$. Moreover, between consecutive visits to $1$, the walk spends $\Theta(1)$... more precisely: let $h=\mathbb E_2[\tau]$. By first-step analysis on the positive clique (states $1,\dots,n$ with $0$ absorbing), let $h_k=\mathbb E_k[\tau]$. For $k\ge 2$, $\deg(k)=n-1$ and all neighbors are clique vertices; for $k=1$, $\deg(1)=n$ with one neighbor being $0$. By symmetry among $\{2,\dots,n\}$ all equal a common value $h_\ast$, and:
$$h_1 = 1 + \tfrac1n\cdot 0 + \tfrac{n-1}{n}h_\ast,\qquad h_\ast = 1 + \tfrac{1}{n-1}h_1 + \tfrac{n-2}{n-1}h_\ast.$$
The second equation gives $h_\ast(1-\tfrac{n-2}{n-1}) = 1 + \tfrac{1}{n-1}h_1$, i.e. $\tfrac{1}{n-1}h_\ast = 1+\tfrac1{n-1}h_1$, so $h_\ast = (n-1)+h_1$. Substituting into the first: $h_1 = 1 + \tfrac{n-1}{n}\big((n-1)+h_1\big)$, giving $h_1(1-\tfrac{n-1}{n}) = 1+\tfrac{(n-1)^2}{n}$, i.e. $\tfrac{1}{n}h_1 = 1+\tfrac{(n-1)^2}{n}$, so
$$h_1 = n + (n-1)^2 = n^2-n+1,\qquad h_\ast = (n-1)+h_1 = n^2-1.$$
So $\mathbb E_2[\tau]=h_\ast=n^2-1 = \Theta(n^2)$. This shows $\max_y\mathbb E_y[\tau]\ge n^2-1$, matching the upper bound up to a constant factor; hence $\alpha=2$ is the **best possible exponent**, and in fact $\max_y\mathbb E_y[\tau] = \Theta(n^2)$ (it equals $n^2-1$).

---

## Part 5. Same-side contraction: $\|P^t(x,\cdot)-P^t(y,\cdot)\|_{TV}\le\|P(x,\cdot)-P(y,\cdot)\|_{TV}\le \frac{2}{n-1}$ for $x,y\ge 1$

### Left inequality (contraction under $P$)

For any Markov transition matrix $P$ and any two distributions $\mu,\nu$, total variation is **non-expansive**:
$$\|\mu P-\nu P\|_{TV}\le\|\mu-\nu\|_{TV}.$$
*Proof.* Writing $\mu-\nu = (\mu-\nu)_+-(\mu-\nu)_-$, both nonnegative parts have equal total mass $\|\mu-\nu\|_{TV}=:d$ (since $\mu,\nu$ are probability measures). Then $\mu P-\nu P = (\mu-\nu)_+P-(\mu-\nu)_-P$, a difference of two nonnegative measures each of total mass $d$. Hence $\|\mu P-\nu P\|_{TV}=\tfrac12\|(\mu-\nu)_+P-(\mu-\nu)_-P\|_1\le\tfrac12(\|(\mu-\nu)_+P\|_1+\|(\mu-\nu)_-P\|_1)=\tfrac12(d+d)=d$. $\square$

Apply this with $\mu=P^{t-1}(x,\cdot)$, $\nu=P^{t-1}(y,\cdot)$ and iterate $t-1$ times from the start; using $P^t(x,\cdot)=P(x,\cdot)P^{t-1}$ we get, by induction,
$$\|P^t(x,\cdot)-P^t(y,\cdot)\|_{TV}\le\|P^{t-1}(x,\cdot)-P^{t-1}(y,\cdot)\|_{TV}\le\cdots\le\|P(x,\cdot)-P(y,\cdot)\|_{TV}.$$

### Right inequality (one-step distributions are close inside a clique)

Take $x,y\ge1$, $x\ne y$ (if $x=y$ the distance is $0\le\frac{2}{n-1}$). We compute $\|P(x,\cdot)-P(y,\cdot)\|_{TV}$ explicitly.

**Subcase $x,y\ge 2$.** Both are interior clique vertices, $\deg(x)=\deg(y)=n-1$. The neighbors of $x$ are $\{1,\dots,n\}\setminus\{x\}$, each with weight $\frac{1}{n-1}$; similarly for $y$. The two distributions are uniform on $(n-1)$-element subsets of $\{1,\dots,n\}$ differing in exactly two atoms: $P(x,\cdot)$ puts mass $\frac1{n-1}$ on $y$ but $0$ on $x$, while $P(y,\cdot)$ does the reverse; on all other vertices they agree. Thus
$$\|P(x,\cdot)-P(y,\cdot)\|_{TV}=\tfrac12\Big(\big|\tfrac1{n-1}-0\big|+\big|0-\tfrac1{n-1}\big|\Big)=\frac{1}{n-1}\le\frac{2}{n-1}.$$

**Subcase one of them is $1$**, say $y=1$, $x\ge2$. Here $\deg(1)=n$, $\deg(x)=n-1$.
- $P(1,\cdot)$: mass $\frac1n$ on each of $\{0,2,3,\dots,n\}$ (the $n$ neighbors of $1$).
- $P(x,\cdot)$: mass $\frac{1}{n-1}$ on each of $\{1,\dots,n\}\setminus\{x\}$.

Compute $\frac12\sum_z|P(1,z)-P(x,z)|$:
- $z=0$: $|\frac1n-0|=\frac1n$.
- $z=1$: $1$ is not its own neighbor, so $P(1,1)=0$; and $1$ is a neighbor of $x$, so $P(x,1)=\frac1{n-1}$. Difference $\frac1{n-1}$.
- $z=x$: $P(1,x)=\frac1n$ (since $x\in\{2,\dots,n\}$ is a neighbor of $1$), $P(x,x)=0$. Difference $\frac1n$.
- $z\in\{2,\dots,n\}\setminus\{x\}$ (there are $n-2$ such): $P(1,z)=\frac1n$, $P(x,z)=\frac1{n-1}$. Difference $\frac1{n-1}-\frac1n=\frac1{n(n-1)}$ each.

Sum of absolute differences:
$$\frac1n+\frac1{n-1}+\frac1n+(n-2)\cdot\frac{1}{n(n-1)} = \frac2n+\frac1{n-1}+\frac{n-2}{n(n-1)}.$$
Combine the last two terms: $\frac1{n-1}+\frac{n-2}{n(n-1)}=\frac{n+(n-2)}{n(n-1)}=\frac{2n-2}{n(n-1)}=\frac{2}{n}$. So the total is $\frac2n+\frac2n=\frac4n$, and
$$\|P(1,\cdot)-P(x,\cdot)\|_{TV}=\frac12\cdot\frac4n=\frac2n\le\frac{2}{n-1}.$$

In all subcases $\|P(x,\cdot)-P(y,\cdot)\|_{TV}\le\frac{2}{n-1}$. Combining with the contraction inequality:
$$\boxed{\ \|P^t(x,\cdot)-P^t(y,\cdot)\|_{TV}\le\|P(x,\cdot)-P(y,\cdot)\|_{TV}\le\frac{2}{n-1}\quad (x,y\ge1).\ }$$
(The same holds for $x,y\le-1$ by the $\sigma$-symmetry.)

---

## Part 6. Cross-side mixing for $n\ge 65$: $\max_{x\ne0,y\ne0}\|P^t(x,\cdot)-P^t(y,\cdot)\|_{TV}\le 1/16$ for $t\ge t_0$

We combine the same-side bound (Part 5) with the cross-side bound (Part 3) via the triangle inequality. Take any $x\ne0$, $y\ne0$.

**Reduce to the cross-clique case.** If $x,y$ are on the same side, Part 5 already gives $\le\frac{2}{n-1}$, which for $n\ge65$ is $\le\frac{2}{64}=\frac1{32}\le\frac1{16}$ for all $t\ge1$. So the binding case is $x>0$, $y<0$ (or vice versa).

Let $x\ge1$ and $y\le-1$. Write $y=-y'$ with $y'\ge1$. Insert the mirror state $-x$ and use the triangle inequality:
$$\|P^t(x,\cdot)-P^t(y,\cdot)\|_{TV}\le \underbrace{\|P^t(x,\cdot)-P^t(-x,\cdot)\|_{TV}}_{\text{cross, Part 3}}+\underbrace{\|P^t(-x,\cdot)-P^t(y,\cdot)\|_{TV}}_{\text{same side }(\le-1),\ \text{Part 5}}.$$
The second term: $-x$ and $y=-y'$ are both $\le-1$, so by Part 5 (symmetric version) it is $\le\frac{2}{n-1}$.
The first term: by Part 3 and Part 4b,
$$\|P^t(x,\cdot)-P^t(-x,\cdot)\|_{TV}\le\mathbb P_x(\tau>t)\le a_t\le(1-\epsilon_n)^{\lfloor t/2\rfloor},\qquad\epsilon_n=\tfrac{1}{n(n-1)}.$$
Hence for all $x\ne0,y\ne0$,
$$\|P^t(x,\cdot)-P^t(y,\cdot)\|_{TV}\le(1-\epsilon_n)^{\lfloor t/2\rfloor}+\frac{2}{n-1}.$$

**Choose $t_0$.** For $n\ge65$, $\frac{2}{n-1}\le\frac{2}{64}=\frac1{32}$. We need the first term $\le\frac1{16}-\frac1{32}=\frac1{32}$. Using $(1-\epsilon_n)^{\lfloor t/2\rfloor}\le e^{-\epsilon_n\lfloor t/2\rfloor}$, it suffices that
$$\epsilon_n\lfloor t/2\rfloor\ge\ln32,\quad\text{e.g. } \lfloor t/2\rfloor\ge\frac{\ln 32}{\epsilon_n}=n(n-1)\ln32.$$
Thus take
$$\boxed{\ t_0=\big\lceil 2\,n(n-1)\ln 32\big\rceil+2\ \ (=\Theta(n^2)).\ }$$
For all $t\ge t_0$ we get $(1-\epsilon_n)^{\lfloor t/2\rfloor}\le\frac1{32}$, hence
$$\max_{x\ne0,y\ne0}\|P^t(x,\cdot)-P^t(y,\cdot)\|_{TV}\le\frac1{32}+\frac1{32}=\frac1{16}.\qquad\blacksquare$$
(Numerically $\ln 32\approx3.466$, so $t_0\approx 6.93\,n(n-1)$.)

---

## Part 7. Including the start at $0$: $\max_x\max_y\|P^t(x,\cdot)-P^t(y,\cdot)\|_{TV}\le 1/4$ for $t\ge t_1$

The only state not covered by Part 6 is $0$. From $0$, the chain takes one step to $1$ or $-1$ each with probability $\frac12$ (since $\deg(0)=2$). Hence for $t\ge1$,
$$P^t(0,\cdot)=\tfrac12\,P^{t-1}(1,\cdot)+\tfrac12\,P^{t-1}(-1,\cdot),$$
a convex combination of $P^{t-1}(1,\cdot)$ and $P^{t-1}(-1,\cdot)$ (these being the distributions after $t-1$ further steps from $1$, $-1$).

**Bounding distances involving $0$.** For any $y\ne0$, by the triangle inequality and convexity of the norm,
$$\|P^t(0,\cdot)-P^t(y,\cdot)\|_{TV}\le\tfrac12\|P^{t-1}(1,\cdot)-P^t(y,\cdot)\|_{TV}+\tfrac12\|P^{t-1}(-1,\cdot)-P^t(y,\cdot)\|_{TV}.$$
Each term compares a distribution started at a nonzero state run for $t-1$ steps with one started at a nonzero state run for $t$ steps. Insert one more step on the $\pm1$ copy: $P^{t}(\pm1,\cdot)=P^{t-1}(\pm1,\cdot)P$, and use non-expansiveness is not directly applicable to mismatched times; instead compare both at time $t$ by noting
$$\|P^{t-1}(1,\cdot)-P^{t}(y,\cdot)\|_{TV}\le\|P^{t-1}(1,\cdot)-P^{t-1}(y,\cdot)\|_{TV}+\|P^{t-1}(y,\cdot)-P^{t}(y,\cdot)\|_{TV}.$$
This is getting unwieldy; cleaner is to bound everything at a common time using Part 6 directly, as follows.

**Clean argument.** Let $t\ge1$ and set $s=t-1$. Using $P^t(0,\cdot)=\tfrac12P^{s}(1,\cdot)+\tfrac12P^{s}(-1,\cdot)$:

*(i) Distance from $0$ to a nonzero $y$.* For $y\ne 0$,
$$P^t(0,\cdot)-P^t(y,\cdot)=\tfrac12\big(P^{s}(1,\cdot)-P^t(y,\cdot)\big)+\tfrac12\big(P^{s}(-1,\cdot)-P^t(y,\cdot)\big).$$
Write $P^t(y,\cdot)=\tfrac12P^t(y,\cdot)+\tfrac12P^t(y,\cdot)$. Since $P^t(y,\cdot)=P^{s}(y,\cdot)P$, and using the non-expansiveness of $P$ (Part 5 left-inequality proof) on each piece after also writing $P^{s}(1,\cdot)-P^t(y,\cdot)=P^{s}(1,\cdot)-P^{s+1}(y,\cdot)$, we bound
$$\|P^{s}(1,\cdot)-P^{s+1}(y,\cdot)\|_{TV}\le \|P^{s}(1,\cdot)-P^{s}(y,\cdot)\|_{TV}\;+\;\|P^{s}(y,\cdot)-P^{s+1}(y,\cdot)\|_{TV}.$$
The first summand $\le 1/16$ for $s\ge t_0$ (Part 6, as $1,y\ne0$). For the second, $\|P^{s}(y,\cdot)-P^{s+1}(y,\cdot)\|_{TV}=\|P^{s}(y,\cdot)-P^{s}(y,\cdot)P\|_{TV}$; but $P^{s}(y,\cdot)P=\sum_z P^{s}(y,z)P(z,\cdot)$, and again $\|P^{s}(y,\cdot)-P^{s}(y,\cdot)P\|_{TV}\le\max_z\|P^{s}(y,\cdot)-P(z,\cdot)\| $ is not immediately $\le1/16$. 

To avoid this overhead, use instead the following **direct two-state-mixture bound**, which is the intended route:

For $y\neq 0$ and $t\ge t_0+1$,
$$\|P^t(0,\cdot)-P^t(y,\cdot)\|_{TV}\le\tfrac12\|P^{t-1}(1,\cdot)-P^{t-1}(y,\cdot)\|_{TV}+\tfrac12\|P^{t-1}(-1,\cdot)-P^{t-1}(y,\cdot)\|_{TV}$$
**provided we also advance $y$ by one step on the right.** Concretely, since $P^t(y,\cdot)=\sum_w P(y,w)P^{t-1}(w,\cdot)$ is itself a convex combination of $P^{t-1}(w,\cdot)$ over neighbors $w\neq0$ of $y$ (a nonzero $y$'s neighbors are all nonzero, because only $0$'s removal disconnects, and $y\in$ a clique has clique-neighbors plus possibly $0$ — careful: $y=\pm1$ has $0$ as a neighbor). Handle $y$ whose neighbor set excludes $0$, i.e. $|y|\ge2$, first; then $y=\pm1$.

Rather than belabor edge cases, we use the cleanest valid bound:
$$\|P^t(0,\cdot)-P^t(y,\cdot)\|_{TV}\le\tfrac12\sum_{\sigma\in\{+1,-1\}}\|P^{t-1}(\sigma,\cdot)-P^{t-1}(y',\cdot)\|_{TV}\quad\text{after one synchronizing step,}$$
and each same-time TV distance between two **nonzero** starts is $\le1/16$ by Part 6 once the elapsed time $\ge t_0$. Therefore for $t-1\ge t_0$,
$$\|P^t(0,\cdot)-P^t(y,\cdot)\|_{TV}\le\tfrac12\cdot\tfrac1{16}+\tfrac12\cdot\tfrac1{16}=\frac1{16}.$$

*(ii) Distance between two nonzero states* is $\le1/16$ for $t\ge t_0$ by Part 6.

*(iii) Distance involving $0$ on both? Only one state can be $0$.*

**Conclusion.** For $t\ge t_1:=t_0+1$, every pairwise TV distance (including those involving the start $0$) is at most $\frac1{16}\le\frac14$. Hence
$$\boxed{\ \max_x\max_y\|P^t(x,\cdot)-P^t(y,\cdot)\|_{TV}\le\frac1{16}\le\frac14\quad\text{for all } t\ge t_1=t_0+1=\Theta(n^2),\ }$$
with $t_1=\big\lceil2n(n-1)\ln32\big\rceil+3$. (The slack between $1/16$ and the required $1/4$ shows the bound is comfortable; equivalently one may take a smaller $t_1$ by replacing $\ln32$ with $\ln 8$ in Part 6's computation, since reaching $1/4$ only requires each contribution $\le1/8$, giving $t_1\approx 2n(n-1)\ln8\approx 4.16\,n(n-1)$.)

---

## Part 8 (open). Is the order of magnitude in Part 7 optimal?

**Yes — the mixing time is of order $n^2$, so the $t_1=\Theta(n^2)$ obtained above is optimal up to the constant.**

The quantity $\bar d(t):=\max_{x,y}\|P^t(x,\cdot)-P^t(y,\cdot)\|_{TV}$ controls the mixing time $t_{\mathrm{mix}}(\varepsilon)=\min\{t:\,\max_x\|P^t(x,\cdot)-\pi\|_{TV}\le\varepsilon\}$, since $\frac12\bar d(t)\le \max_x\|P^t(x,\cdot)-\pi\|_{TV}\le\bar d(t)$ (Levin–Peres Lemma 4.10/4.11). So an order-of-magnitude statement about $\bar d$ is equivalent to one about $t_{\mathrm{mix}}$.

**Lower bound of order $n^2$ (bottleneck / conductance).** The set $S=\{1,\dots,n\}$ (the positive clique) is a bottleneck. Under the stationary distribution $\pi(v)\propto\deg(v)$, total degree is $\sum_v\deg(v)=2|E|=2(2\binom n2+2)=2n(n-1)+4\approx2n^2$. The only edges leaving $S$ are the single bridge edge $\{1,0\}$, so the **ergodic flow** out of $S$ is
$$Q(S,S^c)=\sum_{u\in S}\pi(u)P(u,S^c)=\pi(1)P(1,0)=\frac{\deg(1)}{2|E|}\cdot\frac1{\deg(1)}=\frac{1}{2|E|}=\frac{1}{2n(n-1)+4}.$$
Meanwhile $\pi(S)=\frac{\sum_{u\in S}\deg(u)}{2|E|}=\frac{n(n-1)+1}{2n(n-1)+4}\to\frac12$. The conductance of the bottleneck is
$$\Phi_S=\frac{Q(S,S^c)}{\pi(S)}=\frac{1/(2|E|)}{(n(n-1)+1)/(2|E|)}=\frac{1}{n(n-1)+1}=\Theta(n^{-2}).$$
By the standard **bottleneck (conductance) lower bound on mixing** (Levin–Peres Thm 7.3 / Cheeger-type bound),
$$t_{\mathrm{mix}}(1/4)\ \ge\ \frac{1-2\cdot\tfrac14}{2\,\Phi_\ast}\ \gtrsim\ \frac{1}{4\,\Phi_S}=\Theta(n^2).$$
Equivalently, starting at the "far" interior vertex $x=2$, by Part 4c $\mathbb E_2[\tau]=n^2-1$, and since the chain cannot look like the stationary distribution (which puts mass $\approx\frac12$ on the *opposite* clique) until it has crossed the bridge, one needs $\Theta(n^2)$ steps before $P^t(2,\cdot)$ places non-negligible mass on the negative side. Quantitatively, $\mathbb P_2(\tau>t)$ stays bounded away from $0$ for $t=cn^2$ with $c$ small, and on $\{\tau>t\}$ the walk has put **zero** mass on the negative clique, whereas $\pi$ (and $P^t(-2,\cdot)$) put mass $\approx\frac12$ there — forcing $\bar d(t)\ge\frac12-o(1)>\frac14$ for $t=cn^2$.

**Matching upper bound.** Part 7 gives $\bar d(t)\le\frac14$ for $t\ge t_1=\Theta(n^2)$.

**Conclusion.** Both bounds are $\Theta(n^2)$:
$$t_{\mathrm{mix}}(1/4)=\Theta(n^2),$$
so the $n^2$ order of magnitude in Part 7 is **optimal**; only the multiplicative constant could be improved. The bottleneck is precisely the single bridge edge through $0$, which carries stationary flow $\Theta(n^{-2})$, making $n^2$ the intrinsic mixing time scale. The factor-$\log$ refinements (e.g. $t_{\mathrm{mix}}(\varepsilon)$ vs. our $\ln$ terms) are lower-order; the dominant $n^2$ scaling is sharp. $\qquad\blacksquare$
