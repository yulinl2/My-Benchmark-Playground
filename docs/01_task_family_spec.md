# Task Family Specification

We define a parametric family `T(N, k, ρ)` of long-context, self-contained tasks.
`N` = context length (number of items), `k` = number of queries, `ρ` =
distractor / noise density. Every member has a **closed-form optimal attention
map** `A*(x)`, which is what makes the architectural separation measurable.

A task instance is a tuple `(x, y*, A*)`:
- `x` — the input (tokens for NL, vectors for numeric),
- `y*` — the deterministic optimal output (a function of `x` only),
- `A*` — the optimal attention matrix that an attention layer must realize to
  map the value stream to `y*` in one read-out.

"Self-contained" is the invariant: `y* = f(x)` with `f` a fixed, simple routing
function; no world knowledge, no ambiguity, exactly one correct answer.

---

## 1. `Gather(N)` — pointer permutation (the kernel)

**Numeric form.**
- Value stream `V ∈ ℝ^{N×d_v}`, rows `v_1,…,v_N` (e.g. random unit vectors or
  one-hot symbol embeddings).
- Permutation `π ∼ Unif(S_N)`, encoded as positional pointers `p_i = π(i)`.
- Input token `x_i = [ v_i ‖ onehot(i) ‖ onehot(p_i) ]` (value, its own position,
  the source pointer for slot `i`).
- **Output:** `y*_i = v_{π(i)}`, i.e. `Y* = P_π V`.
- **Optimal attention:** `A* = P_π` (one-hot rows). `rank(A*) = N`.

This is the worst case for linear attention by Theorem I: `A*` is an orthogonal
matrix with all singular values `1`, so the best rank-`r` approximation has
relative error `1 − r/N`.

**Difficulty knob.** Increasing `N` increases `rank(A*)` linearly; nothing else
about the task changes. This isolates *attention rank* as the sole hardness axis.

---

## 2. `MQAR(N, k)` — multi-query associative recall (literature anchor)

Adopted from Arora et al. (*Zoology*, *Based*) as a recognized SSM/linear-
attention diagnostic, recast in our notation.

- `k` key→value pairs `(κ_j, ν_j)` with distinct random keys, scattered among
  `N` positions (the rest are distractor tokens, density `ρ`).
- Then `k` query tokens, each repeating some `κ_j`.
- **Output:** for each query `q` with key `κ_j`, emit `ν_j`.
- **Optimal attention** (query→key layer): the `k×N` partial permutation
  matching each query to the unique position of its key; `rank = k`.

**Difficulty knob.** `k` controls the required rank / recurrent state. Published
results: fixed-state models need state `∝ k`; softmax solves with `O(1)` layers
independent of `k`. We reproduce the *shape* of this curve and connect it to
Theorem II.

---

## 3. `Chain-Tracking(N, L_chain)` — pointer-chain composition

- Assignment statements `s_t`: either `var = literal` or `var = other_var`.
- A designated query variable resolves through a chain of length `L_chain`:
  `z = y, y = x, …, a = 5` ⇒ `z = 5`. Interspersed with `ρ`-fraction distractor
  assignments to unrelated variables.
- **Output:** the literal value of the query variable.
- **Optimal attention:** a composition of `L_chain` one-hot pointer hops; a
  single softmax layer realizes one hop, `O(L_chain)` layers (or `log`-depth
  pointer-jumping) realize the chain. Linear attention must carry the entire
  live binding table in fixed state.

**Difficulty knob.** `L_chain` (depth of indirection) and `N` (table size).

---

## 4. NL lifts (same instances, rendered as text)

Each numeric instance has a deterministic NL rendering with the **identical
answer key**, so the numeric grader and NL grader agree by construction.

### 4.1 `Gather` → "reorder by table"
```
Lines:
[1] mango
[2] cedar
...
[N] violet
Output order (read line at): 7, 3, N, 1, ...
Task: print the line contents in the given output order, one per line.
```

### 4.2 `MQAR` → "in-context dictionary"
```
Facts:
- The access code for Lisbon is 4F2.
- The access code for Cairo is 9Qd.
... (k facts among N lines, with distractors)
Questions: access code for Cairo? access code for Lisbon? ...
```

### 4.3 `Chain` → "variable tracking"
```
Let q = m.   Let m = t.   ...   Let a = 5.
(plus distractor assignments to unrelated names)
Question: What is the value of q?
```

All three are **open-book on the prompt, closed-book on the world**: a model with
faithful random access to the context answers perfectly; a model that compresses
the prompt into fixed state cannot, once `N`/`k`/`L_chain` exceed its budget.

---

## 5. Generator contract (implemented in `src/`)

A generator `gen(task, N, k, ρ, seed) -> Instance` must guarantee:
1. **Uniqueness:** exactly one correct `y*`.
2. **Self-containedness:** `y*` is computable from `x` by the reference solver
   `f` with no external data.
3. **Closed-form `A*`:** the optimal attention matrix is returned alongside.
4. **Reproducibility:** fully determined by `seed`.
5. **Numeric/NL parity:** `numeric_instance` and `nl_instance` share one answer
   key.

These contracts are enforced by `assert`s in the generators and by a
self-containedness audit (a reference solver must score 100%).
