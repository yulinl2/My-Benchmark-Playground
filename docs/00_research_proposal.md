# Research Proposal: A Task Distribution that Separates Softmax from Linear Attention

**Status:** living document · **Branch:** `research/long-context-attention-expressivity-separation`

---

## 1. The question

> Can we find or design a family of long-context task distributions — drawing on
> existing literature and our own construction — for which the attention-score
> distribution required by every optimal solution is **completely solvable from
> the task information itself** (a *self-contained task spec*), yet a current
> monolithic LLM built on **linear attention** has no chance of hitting it with
> high probability — even with multi-head, multi-layer Transformers — because for
> any *fixed* parameter / depth / width budget there is always a task subspace
> rich enough that the architecture (i) lacks the approximation capacity, or
> (ii) cannot simultaneously satisfy pretraining fit and generalization?

We want the separation to be **constructive** (a generator of hard instances,
not one cherry-picked example), **self-contained** (the optimum is a deterministic
function of the prompt, so success cannot be attributed to memorized knowledge),
and **liftable** from numeric functions to natural language, where we validate it
on commercial softmax models.

### 1.1 What "self-contained" buys us

If the target output `y*(x)` is a fixed, simple function of the input tokens `x`
(e.g. "follow the pointer", "copy the value tagged with this key"), then:

- A model that fails **cannot** be excused by "it didn't know the fact" — the
  fact is in the context.
- The **ground-truth attention map** `A*(x)` is known in closed form, so we can
  measure not just task accuracy but *attention-pattern realizability* directly.
- We can dial difficulty by a single knob (context length `N`, number of keys
  `k`) without changing the *kind* of reasoning required, isolating the
  architectural variable.

---

## 2. Architectural model and the locus of the limitation

We compare two attention operators on a length-`N` context with model width `d`.

**Softmax attention (per head):**
$$ A = \operatorname{softmax}\!\big(QK^\top/\sqrt{d}\big),\qquad O = A V, $$
where `Q=XW_Q`, `K=XW_K`, `V=XW_V`. The score matrix `QK^\top` can be full rank
`N`, and softmax can make rows arbitrarily peaked, so `A` can approximate **any
row-stochastic matrix**, including any permutation matrix, to arbitrary accuracy
(given large enough logits, which the temperature `1/\sqrt d` and weight scale
permit).

**Linear / kernelized attention (per head):** replace softmax by a feature map
`φ: ℝ^d → ℝ^m` (`m` = feature dimension):
$$ A_{ij} = \frac{φ(q_i)^\top φ(k_j)}{\sum_{j'} φ(q_i)^\top φ(k_{j'})},\qquad O = AV. $$
The unnormalized score matrix `S = Φ_Q Φ_K^\top` with `Φ_Q,Φ_K ∈ ℝ^{N×m}` has
**`rank(S) ≤ m`**. Crucially, linear attention also admits the equivalent
**recurrent form** with a *fixed-size state* `Z_t = \sum_{j≤t} φ(k_j) v_j^\top ∈
ℝ^{m×d}` and `s_t = \sum_{j≤t} φ(k_j)`, read out as `o_t = φ(q_t)^\top Z_t /
(φ(q_t)^\top s_t)`. This is the SSM / linear-RNN view (RetNet, RWKV, "Based",
and the linear-attention reduction of Katharopoulos et al. 2020). The entire
prefix is compressed into `O(m·d)` numbers **independent of `N`**.

The limitation we exploit lives in **exactly one place**: the per-layer
attention map is **rank-bounded by `m`** (matrix view) ⇔ the recurrence carries a
**state of `N`-independent size** (streaming view). Softmax has neither bound:
its map can be full-rank, and it is non-recurrent (random access).

> Multi-head and multi-layer do **not** remove the bound — they raise the
> constant. `H` heads give an effective rank `≤ H·m` per layer; `L` layers
> compose maps but cannot synthesize an exact high-rank one-hot routing from a
> bounded product of rank-bounded stochastic maps without error that we lower-bound
> below. The whole point is that for **any fixed `(H, L, m, d)`** we can pick `N`
> large enough to break it.

---

## 3. The core construction: routing/gather by in-context pointers

**`Gather(N)`.** The prompt encodes a value stream `v_1,…,v_N` and a routing spec
that names, for each output slot `i`, a source index `π(i) ∈ {1,…,N}`. The
optimal output is
$$ y^*_i = v_{π(i)},\qquad\text{i.e.}\qquad Y^* = P_π V, $$
where `P_π` is the `N×N` permutation matrix of `π`. The **optimal read-out
attention is exactly `P_π`** — one-hot rows pointing at the source.

This is the canonical *self-contained* task: `π` is written in the prompt, the
values are in the prompt, the answer is a pure lookup. The required attention map
is a uniformly random permutation matrix when `π ∼ Unif(S_N)`.

Two more members (formalized in `docs/01_task_family_spec.md`) inherit the same
difficulty signature:
- **MQAR(N, k)** — multi-query associative recall: `k` key→value pairs scattered
  in the context, then `k` queries; the optimal attention is a (partial)
  permutation matching queries to their keys. (This is the Zoology/Based
  diagnostic; we adopt it as a literature anchor.)
- **Chain-Tracking(N, L_chain)** — variable-assignment chains `a=5; b=a; …; z=y`
  with distractors; the optimum follows a pointer chain of length `L_chain`.

---

## 4. Separation Theorem I — the rank bound (single read-out layer)

**Setup.** Restrict attention to the read-out: the model must produce `Ŷ = A V`
approximating `Y^* = P_π V`, where `V` is full column rank (`N ≥ d`, generic
values) and `A` is the model's attention matrix.

**Theorem 1 (linear attention cannot realize a random permutation).**
Let `A` be produced by `H` linear-attention heads with feature dim `m`, so
`A = \sum_{h} D_h^{-1} Φ_Q^{(h)} Φ_K^{(h)\top}` has `rank(A) ≤ H·m`. Then for
the gather error `\mathcal E = \mathbb E_{V}\,\|AV - P_π V\|_F^2 / \|V\|_F^2`,
$$ \mathcal E \;\ge\; \frac{1}{N}\sum_{i=N-r}^{N}\sigma_i(A-P_π)^2 \;\ge\; \frac{N - H m}{N}, $$
because `P_π` is orthogonal (all singular values `=1`) and the best rank-`r`
approximation in Frobenius norm leaves the bottom `N−r` unit singular values
(Eckart–Young), with `r = rank(A) ≤ Hm`. Hence for any fixed `H, m`,
$$ \boxed{\;\mathcal E \;\ge\; 1 - \frac{Hm}{N}\;\xrightarrow[N\to\infty]{}\; 1.\;} $$

So as the context grows, a fixed-capacity linear read-out's *relative* gather
error tends to 1 (it learns essentially nothing of a fresh random permutation),
while a softmax read-out drives `A → P_π` and `\mathcal E → 0`. This is the
clean, fully provable kernel of the separation, demonstrated numerically in
`src/numeric/rank_separation.py`.

**Remark (why depth doesn't save it cheaply).** A depth-`L` linear network
composes `A = A_L⋯A_1`. Each `A_ℓ` is row-stochastic with `rank ≤ Hm`. A product
of `L` rank-`(Hm)` matrices has rank `≤ Hm`, so the read-out map handed to `V`
still has rank `≤ Hm` — depth alone does not raise the rank ceiling. (Depth helps
only by *recomputing* keys/queries from intermediate features; that is the regime
Theorem II addresses.)

---

## 5. Separation Theorem II — the recurrent-state / communication bound

Theorem I freezes the keys/values. To cover *adaptive* multi-layer linear models
(which recompute features per layer), use the streaming view.

**Theorem 2 (informal; streaming lower bound).** Consider answering, after
reading the whole prompt, an arbitrary query "what is `v_{π(i)}`?" Any
linear-attention/SSM stack with total recurrent state of `B` bits processes the
prompt left-to-right and must, at the boundary just before the queries, have
summarized the prefix into `B` bits. Specifying a uniformly random `π ∈ S_N`
together with `Θ(\log b)`-bit values requires `Θ(N\log N)` bits to answer
arbitrary subsequent gather queries. By a standard one-way communication /
streaming argument (the same shape as the associative-recall lower bounds of
Arora et al., *Zoology*), if `B = o(N\log N)` the expected number of correctly
answered queries is bounded away from the maximum; the per-query error is
`≥ 1 − B/Θ(N\log N)`. Softmax attention is **non-recurrent** (random access over
the KV cache) and therefore is not subject to this prefix-compression bound — it
pays memory `O(N)` (the KV cache) by design.

For a fixed model, `B = O(H·m·d·\text{(precision)})` is constant, so for
`N` large the bound bites: **fixed-state linear attention provably loses
information about long self-contained routing tasks.**

**Pretrain-fit vs. generalization corollary.** One could try to beat Theorem I by
*memorizing* the finite training set (overfitting `π`'s seen in pretraining). But
the task family is parameterized so the number of distinct routings `|S_N| = N!`
explodes; any finite linear model can memorize only `2^B / poly` of them. Driving
`N` up forces the model off the memorized set, where Theorem II applies. Thus the
linear model faces a genuine **overfit-vs-generalize bind**: enough capacity to
memorize the pretrain routings is still `o(N\log N)` short of generalizing to
fresh ones. Softmax has no such bind because it *computes* the routing rather
than storing it.

---

## 6. From numeric functions to natural language

The numeric `Gather/MQAR/Chain` tasks lift to NL while preserving
self-containedness and the attention signature:

| Numeric task | NL lift | Optimal attention |
|---|---|---|
| `Gather(N)` | "Reorder these `N` lines according to the priority table above." | permutation `P_π` |
| `MQAR(N,k)` | "Here are `N` `〈city → code〉` facts. Give the code for: …(k queries)." | partial permutation (query→key match) |
| `Chain(N,L)` | "Let a=5. Let b=a. … What is `z`?" with distractors | pointer-chain composition |

These are **closed-book on the world but open-book on the prompt**: the answer is
fully determined by the text shown. That is precisely the property that makes a
failure attributable to *architecture*, not *knowledge*.

---

## 7. Verification plan (commercial softmax models via sub-agents)

We cannot run a *linear-attention* commercial model, so the commercial-model
experiments serve three specific, falsifiable purposes (detailed in
`docs/02_experimental_plan.md`):

1. **Self-containedness audit (positive control).** A strong softmax model
   (Haiku) given the full prompt should solve `Gather/MQAR/Chain` at high
   accuracy *up to its context limit*, confirming the tasks are solvable from the
   spec alone. We run this with **in-session Haiku sub-agents** (Max-plan
   covered) as the solver, and a deterministic grader.
2. **Difficulty-scaling fingerprint.** Measure accuracy vs. `N`/`k`/distractor
   density. The theory predicts softmax degrades only near its *context budget*,
   not because of the routing rank — a qualitatively different curve than the
   `1 − Hm/N` floor predicted for fixed-state linear models.
3. **Cross-architecture separation (future / local-GPU).** The decisive test runs
   the same generated instances against open linear-attention/SSM checkpoints
   (RWKV, Mamba, RetNet, Based) and contrasts the accuracy-vs-`N` curve with
   softmax. This needs GPU and is specified as the next milestone.

---

## 8. Falsifiable predictions

- **P1 (numeric, provable+empirical).** A linear-attention read-out's relative
  gather error is `≥ 1 − Hm/N`; a softmax read-out reaches `≈ 0`. → tested in
  `src/numeric/`.
- **P2 (numeric, training).** Trained end-to-end on a fresh-`π` distribution, a
  fixed linear model's accuracy is capped and *decreases* as `N` grows past
  `Hm`; softmax stays high. → `src/numeric/train.py`.
- **P3 (NL, sub-agent).** Haiku solves the NL lifts at high accuracy while `N`
  is within context budget (self-containedness holds); accuracy falls only as
  `N` approaches the budget, not at a fixed small `N`. → `src/nl/` + `results/`.
- **P4 (cross-arch, future).** Open SSM/linear models show the `N`-dependent
  collapse on the *same* instances where softmax does not. → next milestone.

If P1 fails, the theory is wrong. If P3 shows Haiku failing at small `N` on a
self-contained spec, the task is not actually self-contained (a bug in the
generator) and must be fixed.

---

## 9. Novelty vs. prior art

MQAR/Zoology/Based already show SSMs need state `∝ k` for associative recall.
Our additions: (a) a **single knob `N`** family with a **closed-form optimal
attention matrix** (the permutation), turning the separation into an
*Eckart–Young rank* statement (Theorem I) that is provable in three lines; (b) an
explicit **overfit-vs-generalize corollary** tying the lower bound to the
pretrain/generalization trade-off; (c) a **numeric→NL lift** with a self-
containedness audit on commercial softmax models, making the construction a
*benchmark generator* rather than a fixed dataset. See `docs/03_related_work.md`.
