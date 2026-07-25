## 1. Restatement

$X$ takes values in $[-1,1]$ with a **symmetric** density $f$ ($f(x)=f(-x)$).
$Y\in\{\pm1\}$ with $P(Y=1\mid X=x)=\sigma(x):=\dfrac{1}{1+e^{-x}}$.
Find the density of $V=YX$ on $[-1,1]$.

## 2. Assumptions

- $f$ is a genuine density on $[-1,1]$, symmetric.
- $Y$ depends on $X$ only through the stated conditional probability.

## 3. Derivation

Condition on $X=v$. Then $V=v$ when $Y=1$, which happens with probability $\sigma(v)$.
So the density of $V$ at $v$ is the density of $X$ at $v$ weighted by that probability:

$$f_V(v)=f(v)\,\sigma(v)=\frac{f(v)}{1+e^{-v}},\qquad v\in[-1,1].$$

This is the original symmetric density *tilted* by the logistic weight: mass is pushed
toward positive $v$, which is the expected qualitative behaviour since $Y=1$ is more
likely when $X>0$.

## 4. Final answer

$$\boxed{\ f_V(v)=\frac{f(v)}{1+e^{-v}},\qquad v\in[-1,1].\ }$$

## 5. Grading criteria

Must condition on $X$ and apply the logistic weight. Near-miss: answering $f_V=f$
(claiming $V$ is symmetric) without justification.

## 6. Self-assessed confidence

**medium.** Biggest reason it might be wrong: I have only tracked the $Y=+1$ route to
$\{V=v\}$ and should check whether $Y=-1$ also contributes.
