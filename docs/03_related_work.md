# Related Work & Positioning

Anchors for each pillar of the argument, and what is new here. arXiv ids verified
during the literature pass (June 2026).

## Linear / kernelized attention and SSMs
- **Katharopoulos, Vyas, Pappas, Fleuret, 2020 — "Transformers are RNNs: Fast
  Autoregressive Transformers with Linear Attention"** (arXiv:2006.16236).
  Establishes the feature-map form `φ(q)^⊤φ(k)` and the equivalent linear-RNN
  recurrence with fixed-size state — the object Theorem II constrains.
- **RWKV (Peng et al., arXiv:2305.13048), RetNet (Sun et al., arXiv:2307.08621),
  Gated Linear Attention (Yang et al., arXiv:2312.06635), "Based" (Arora et al.,
  arXiv:2402.18668).** Modern linear-attention/SSM variants; all carry an
  `N`-independent recurrent state, the property we exploit. Based explicitly
  frames a **recall–throughput tradeoff** governed by state size — the empirical
  shadow of our lower bound.
- **Mamba / S4 (Gu & Dao, arXiv:2312.00752).** Selective SSMs; input-dependent
  gating softens but does not remove the fixed-state bottleneck — still
  `O(state)` bits at the prefix boundary, so Theorem II still applies (larger
  constant).

## Associative recall as a separation diagnostic
- **Arora et al., 2023 — "Zoology: Measuring and Improving Recall in Efficient
  Language Models"** (arXiv:2312.04927) and the **MQAR** task. Across 17 models,
  ~82% of the attention-vs-gated-convolution quality gap is explained by
  in-context recall; the gap scales with the number of KV pairs and SSMs need
  state `∝ k`. We adopt MQAR as a literature anchor and generalize it to the
  single-knob `Gather(N)` permutation kernel.
- **Jelassi, Brandfonbrener, Kakade, Malach, 2024 — "Repeat After Me:
  Transformers are Better than State Space Models at Copying"**
  (arXiv:2402.01032). **Closest prior art to this program** (added during
  self-audit): proves a 2-layer transformer copies exponentially long strings
  while any fixed-state GSSM is information-theoretically limited, and
  validates on pretrained LLMs. This is the Theorem-II separation shape applied
  to a copy task (≈ `Gather` with identity routing), including the
  pretrained-model validation strategy. Our novelty claims are tempered
  accordingly — see `docs/05_self_audit.md` (C1): what remains distinct here is
  the per-layer Eckart–Young rank framing on a permutation target, the
  closed-form `A*` as a measurable artifact, and the generator packaging.
- **Olsson et al., 2022 — "In-context Learning and Induction Heads"**
  (arXiv:2209.11895). Induction heads are the softmax mechanism that solves
  copy/recall; explains *why* softmax realizes the one-hot routing our `A*`
  requires. Consistent with our sweep: Haiku stays ~perfect on recall (mqar/chain/
  kv) even at high difficulty.

## Expressivity / approximation theory of attention
- **Eckart–Young–Mirsky theorem.** The exact tool behind Theorem I: best rank-`r`
  approximation error of an orthogonal `P_π` is `√(N − r)` in Frobenius norm.
- **Communication / streaming lower bounds** (one-way communication complexity of
  INDEX / set-disjointness flavored arguments). The backbone of Theorem II:
  fixed-state sequence models are streaming algorithms; recall of a random
  permutation requires `Ω(N log N)` bits at the prefix cut.
- **Sanford, Hsu, Telgarsky, 2023 — "Representational Strengths and Limitations of
  Transformers"** (arXiv:2306.02896). Directly relevant: their sparse-averaging
  (softmax cheap) vs. triple-detection (linear cost) separations use **the same
  communication-complexity proof technique** that powers our Theorem II, and they
  argue communication complexity is *the* lens for these models. Strong external
  support for both the positive (softmax) and negative (fixed-state) sides.

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
