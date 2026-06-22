# Related Work & Positioning

Anchors for each pillar of the argument, and what is new here. (Citations are by
author/title; arXiv ids to be filled during literature pass — flagged `[id?]`.)

## Linear / kernelized attention and SSMs
- **Katharopoulos et al., 2020 — "Transformers are RNNs."** Establishes the
  feature-map form `φ(q)^⊤φ(k)` and the equivalent linear-RNN recurrence with
  fixed-size state. This is the object Theorem II constrains.
- **RetNet, RWKV, GLA, "Based" (Arora et al.).** Modern linear-attention/SSM
  variants; all carry an `N`-independent state, which is the property we exploit.
- **Mamba / S4 (Gu et al.).** Selective SSMs; input-dependent gating softens but
  does not remove the fixed-state bottleneck — still `O(state)` bits at the
  prefix boundary, so Theorem II still applies (with a larger constant).

## Associative recall as a separation diagnostic
- **Arora et al. — "Zoology: Measuring and Improving Recall in Efficient Language
  Models"** and the **MQAR** task. Empirically and theoretically: gap between
  attention and gated-convolution/SSM models on recall scales with the number of
  KV pairs; SSMs need state `∝ k`. We adopt MQAR as a literature anchor and
  generalize it to the single-knob `Gather(N)` permutation kernel.
- **Olsson et al. — "In-context Learning and Induction Heads."** Induction heads
  are the softmax mechanism that solves copy/recall; explains *why* softmax
  realizes the one-hot routing our `A*` requires.

## Expressivity / approximation theory of attention
- **Eckart–Young–Mirsky theorem.** The exact tool behind Theorem I: best rank-`r`
  approximation error of an orthogonal `P_π` is `√(N − r)` in Frobenius norm.
- **Communication / streaming lower bounds** (one-way communication complexity of
  INDEX / set-disjointness flavored arguments). The backbone of Theorem II:
  fixed-state sequence models are streaming algorithms; recall of a random
  permutation requires `Ω(N log N)` bits at the prefix cut.
- **Sanford, Hsu, Telgarsky — "Representational Strengths and Limitations of
  Transformers"** and related depth/width separations for attention. Companion
  results showing softmax attention's representational power on
  sparse/selection tasks; complements our linear-side lower bound.

## Long-context evaluation
- **Needle-in-a-Haystack; RULER; LongBench.** Existing long-context benchmarks.
  Our family differs by being a **generator with a closed-form optimal attention
  matrix** and a tunable rank knob, rather than fixed datasets — enabling the
  *provable* separation rather than only empirical scores.

---

## What is novel here
1. **Single-knob, closed-form-`A*` family.** Reducing the separation to an
   Eckart–Young statement on a permutation matrix (Theorem I) — a three-line
   proof that the relative gather error of any fixed `(H,m)` linear read-out is
   `≥ 1 − Hm/N`.
2. **Overfit-vs-generalize corollary.** Tying the streaming lower bound (Theorem
   II) explicitly to the pretrain-memorization-vs-generalization bind, matching
   the user's framing that fixed capacity cannot balance both as the task space
   grows.
3. **Numeric→NL lift with a self-containedness audit.** Turning the construction
   into a *benchmark generator* whose NL instances are validated on commercial
   softmax models (Haiku) via in-session sub-agents, so that any failure is
   attributable to architecture rather than missing knowledge.

## Open questions / risks
- Do input-dependent SSM gates (Mamba-2) effectively raise the rank ceiling on
  *structured* (non-uniform) `π`? → restrict to `Unif(S_N)` to be safe; study
  structured `π` separately.
- Does softmax's finite logit range cap the realizable peak sharpness, giving a
  *softmax-side* `N`-dependent error too? → quantify the logit/temperature budget
  needed for `A ≈ P_π` (it grows like `log N`, far cheaper than linear's `Hm≥N`).
- Tokenization effects on the NL lift (see experimental plan threats).
