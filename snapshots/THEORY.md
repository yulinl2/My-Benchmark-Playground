# Why the skill-impact splits: a theory from the two SkillsBench drafts

Scope: PR #570 `taxonomy-tree-merge` and PR #372 `trend-anomaly-causal-inference`
(both authored by Jianheng Hou; #372 co-authored by Yulin Li). The contributors
benchmarked on a **Claude 4.5-class model + Codex** (the PR pages label #570 as
"opus-4.5" and #372 as "sonnet-4-5"/Codex "gpt-5.2" — exact IDs are WebFetch-unreliable);
this repo fills the **opus-4.8** column. The capability gap between those generations
(a tier **and** a generation jump) is the actual scientific signal — see
`ENV_AND_SOURCES.md` for the full env/timeout comparison, sourced eval records, and the
two confounds (CPU cap, unbounded no-skills budget).

---

## 1. What the contributors did behind the scenes (reconstructed)

From the PR write-ups, task files, oracle `solve.sh`, tests, and the shipped skills:

- **Both tasks ship the skill as an executable reference pipeline, not docs.**
  - taxonomy: `hierarchical-taxonomy-clustering/scripts/{pipeline,step1_preprocess,step2_weighted_embedding,step3_recursive_clustering_naming,step4_result_assignments}.py`
  - trend: four skills, each with a `scripts/*.py` (`data_cleaning`, `time_series_anomaly_detection`, `feature_engineering`, `did_causal_analysis`).
  So **"with skills" ≈ "handed a working implementation"**; "without skills" measures whether the model can *re-derive both the method and the exact output contract*.
- **`instruction.md` is deliberately outcome-only, "no skill hints"** (a SkillsBench rule). The precise output contract (column schemas, depth ≤ 5, per-level prefix removal, `unified_level_1` ≥70% path coverage; the intensive/extensive margin convention) is therefore **unguessable from the prompt** — it lives only in the skill.
- **The DiD skill encodes one decisive econometric discriminator.** `did_causal_analysis/SKILL.md` spells out *intensive margin = purchasers only* vs *extensive margin = complete panel with `fillna(0)`*, and warns: *"Including zeros for non-participants dilutes the effect and changes the research question."*
- **Budgets/resources were tuned per task.** taxonomy: `agent.timeout=500s`, `allow_internet=true` (the skill downloads `all-MiniLM-L6-v2` from HF), **8 CPU / 16 GB**. trend: `agent.timeout=900s`, `reasoning_effort=high`, 2 CPU / 8 GB, and it *mounts* `ANTHROPIC_API_KEY`/`OPENAI_API_KEY` that **no grader code actually uses** (vestigial → standard-track, deterministic).

### Contributors' reported numbers (from the PR pages)

> Provenance: extracted from the GitHub PR discussions (#570, #372) via WebFetch
> summarization — treat the exact decimals as PR-reported, not re-verified by me.

**#570 taxonomy** (opus-4.5): oracle 22/22; **with skills 22/22 (100%, 101 output tokens)**;
**without skills 12/22 (62%, 371 tokens)**; Codex with 100%, **Codex without 0% (timeout)**.
Reviewer: *"Skills provide substantial value: +38% for Claude, +100% for Codex."*

**#372 trend** (opus-4.5): oracle 15/15; **with skills 100%** (Codex 95%);
**without skills 84.44% (12/15)** for *both* Claude and Codex; *"+15.56% Claude, +10.56% Codex."*
Root cause without skills: *"Both agents incorrectly zero-filled intensive margin dataset"* →
*"201,080 rows (should be ~4,226)"* → *"unrealistic p-values (median=0.015 vs expected 0.05–0.8)."*
Token tell: with-skills read **4,243,203** input tokens vs **1,313,020** without ("read skill documentation").

---

## 2. The opus-4.8 column (this repo) vs the opus-4.5 column

(Contributor column = the 4.5-class model per the PR pages; see model-ID caveat above.)

| Task | config | 4.5-class (contributor) | opus-4.8 (here, harbor) |
|---|---|---|---|
| **trend** | oracle | 100% (15/15 fn) | 100% |
| | with skills | **100%** | **95%** (18/19 cases; P2 `test_cross_file_consistency`) |
| | without skills | **84.44%** (12/15 fn) | **100%** (19/19) |
| | skill Δ | **+15.6pp** | **−5pp (NO-OP)** |
| **taxonomy** | oracle | 100% (22/22) | 100% |
| | with skills | **100%** | **100%** |
| | without skills | **62%** (12/22, *finished* in 500s @ 8 CPU) | **0%** @500s/4 CPU (timeout) · **78%** (17/22) unbounded |
| | skill Δ | **+38pp** | **+∞ @budget · +21.5pp unbounded** |

The two tasks moved in **opposite directions** across one model generation:
trend's skill went from large-positive to ~zero; taxonomy's skill stayed large-positive.

---

## 3. The theory

**A skill's measured value is the gap between what the grader demands and what the
base model supplies unaided, evaluated under a fixed compute budget. Both terms move
with model generation, so skill value is a moving target — and the *kind* of value a
skill carries migrates as models improve.**

Decompose what a skill supplies into four layers:

| Layer | What it gives | Erosion as models improve |
|---|---|---|
| **L1 — Method / domain knowledge** | "use Prophet for the counterfactual"; "intensive vs extensive margin" | **Fast.** Absorbed into the base model. |
| **L2 — Output-contract spec** | exact schemas, depth≤5, prefix-removal, ≥70% coverage | **Slow / never** — instruction hides it by design, so it's unguessable regardless of capability. |
| **L3 — Compute/efficiency shortcut** | an optimized pipeline that *fits the budget* | **Persists while the budget binds.** |
| **L4 — Implementation reliability** | fewer integration bugs across steps | **Partial** — the agent still wires the steps, so variance remains. |

**Trend is an L1-dominant skill.** Its decisive value was the econometric discriminator
(L1). opus-4.5 lacked it → zero-filled the intensive margin → 84%. opus-4.8 already
*has* it → solves from scratch at 100% → **L1 value ≈ 0**. L2 is light (plain CSV
schemas the model gets right) and L3 doesn't bind (900s is ample). So the skill
collapses to a NO-OP, and at n=1 even reads −5pp from an **L4 hiccup**: the with-skills
run dropped 228 survey IDs from the extensive file (a join/merge bug on a *P2* check) —
implementation variance, not a systematic regression. **Capability absorbed the skill.**

**Taxonomy is an L2+L3-dominant skill.** Its value is an *arbitrary path-encoding
contract* (L2) plus an *embedding/clustering pipeline that fits a tight budget* (L3) —
neither erodes with capability:
- **L2:** opus-4.8 from scratch builds a *semantically sound* taxonomy (clustering,
  naming, lemmatization, dedup, balance all PASS) yet still misses **3 P0 + 2 P1**
  contract tests (kept full ancestor prefixes → 27,875 violations; `unified_level_1`
  labels at 0% coverage; depth>5). The contract is unguessable from the prompt, so a
  smarter model still can't infer it → **skill persists** (+21.5pp even unbounded).
- **L3:** full sentence-transformer embeddings of 10,939 paths don't fit 500s; the skill
  ships an optimized pipeline (and reuses it with ~101 output tokens). Under budget the
  skill is the difference between *finishing* and *timing out*.

This also explains the **token tell**: with-skills emits *fewer* output tokens (it
*runs* the shipped scripts) while reading *more* input tokens (it *ingests* the skill).
Low-output + high-input is the signature of "executing a reference," not "deriving."

---

## 4. The budget/compute inversion (and the confound I introduced)

At the task's *intended* 500s budget, the **newer, more capable** opus-4.8 scored
**worse** without skills (0%, timeout) than opus-4.5 did (62%, finished). Two causes:

1. **I capped taxonomy from 8 CPU/16 GB → 4 CPU/12 GB** to fit this host. Embedding
   10,939 paths on half the cores is the likely reason my run blew the 500s budget where
   theirs didn't. **My "0% @500s" is partly my resource cap, not a clean capability
   result.** The capability-clean number is the unbounded **78%**.
2. opus-4.8 chose a *more thorough* (slower) from-scratch approach (89 steps, 24 edits,
   sentence-transformers + KMeans + networkx) — "smarter" can mean "does more work,"
   which loses under a wall-clock cap. **Capability and compute-efficiency-under-budget
   are different axes.**

Corollary: a benchmark that holds the time budget fixed across model generations is
partly measuring *efficiency*, not just *capability* — and is sensitive to the harness's
per-step overhead.

---

## 5. Observations & caveats (every confound between the two columns)

1. **Model generation** (opus-4.5 → 4.8): the headline confound — and the finding.
2. **Harness**: contributor used `bench eval create -a claude-agent-acp`; I used
   `harbor run -a claude-code`. Different code style *and* per-step overhead (matters for L3/budget).
3. **Resource cap** (taxonomy 8/16 → 4/12): likely caused my 500s timeout; breaks
   comparability of the @budget taxonomy no-skills cell.
4. **Denominator drift from parametrization, not new tests**: contributor counts test
   *functions* (trend 15, tax 22); harbor counts *parametrized cases* (trend **19**, tax 22).
   Trend percentages are not directly comparable (15-fn vs 19-case); taxonomy is (22=22).
5. **trend with-skills 0.95 is single-trial L4 noise** (228-ID join on a P2); |Δ|=5pp is
   below the rubric's 30pp noise floor. Not a "skill hurts" result.
6. **n = 1 everywhere**; Prophet, KMeans init, and embedding all carry stochasticity.
7. **trend API keys are vestigial** (no LLM in grader) → standard-track, deterministic.
8. **`allow_internet=true` (taxonomy)** → live HF model download inside the budget — adds
   network-latency variance to the L3/timeout story.
9. **Both skills ship runnable scripts** → "without skills" is a *re-derivation* test
   (method **and** contract), not a "did it read a tip" test. This is what makes L2 value real.

---

## 6. Falsifiable predictions

- **P1.** Restore taxonomy to 8 CPU at 500s → opus-4.8 without-skills *finishes* and lands
  ≈62–78% (not 0). (Tests the resource confound.)
- **P2.** As base models improve further, **trend without-skills stays ≈100%** (L1 saturated)
  while **taxonomy without-skills rises but plateaus below 100%** — pinned by the L2 contract
  gap — *unless* `instruction.md` is made contract-explicit. Skill value asymptotes to the
  unguessable-contract gap, not to zero.
- **P3.** Multi-trial trend with-skills → the −5pp regresses toward 0 (L4 variance).
- **P4.** Make the taxonomy instruction specify depth/prefix/coverage explicitly → the
  no-skills score jumps and the skill Δ shrinks toward the pure L3 (compute) residual.

**One-line thesis:** *skills don't have a fixed value; they have a value that decays
fastest where they teach (L1) and persists where they specify an unguessable contract
(L2) or buy compute under a binding budget (L3). Trend is L1; taxonomy is L2+L3 — which
is exactly why one became a no-op for opus-4.8 and the other didn't.*
