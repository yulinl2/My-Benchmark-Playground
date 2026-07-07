# Test-environment & timeout comparison + sourced eval records

Pulls together the env/timeout setup of both SkillsBench drafts, compares it to what I
actually ran, and links the contributor eval records. Read alongside `THEORY.md`.

## Sources (linked)

- PR #570 `taxonomy-tree-merge`: https://github.com/benchflow-ai/skillsbench/pull/570
  — merged Jan 23 2026 (commit `aa42d73`), **reverted by #610 Jan 24 2026, re-added Apr 20 2026**.
  Author JianhengHou; approver **yulinl2**.
- PR #372 `trend-anomaly-causal-inference`: https://github.com/benchflow-ai/skillsbench/pull/372
  — merged Jan 23 2026; author JianhengHou + Yulin Li; approver **yulinl2**.
- Repo review tooling: `.agents/skills/task-review/` (gotcha table), `MAINTAINER.md`.
- Task files (verbatim, fetched branches): `tasks/<id>/{task.toml,environment/Dockerfile,tests/test.sh}`.

> Provenance caveat: PR-comment numbers were extracted from the **rendered HTML pages via
> WebFetch** (the `api.github.com` JSON is 403/rate-limited and my GitHub MCP scope is this
> repo only). Treat exact decimals — and especially **model IDs** — as PR-reported, not
> independently re-verified. The two pages disagree on the contributor model (see below).

---

## 1. Declared environment & timeouts (from `task.toml`)

| Setting | taxonomy (#570) | trend (#372) |
|---|---|---|
| `agent.timeout_sec` | **500** | **900** |
| `agent.reasoning_effort` | (unset) | **high** |
| `verifier.timeout_sec` | 180 | 200 |
| `environment.build_timeout_sec` | 200 | 200 |
| `cpus` | **8** (PR page; "8 CPU/16GB for embeddings") | 2 |
| `memory_mb` | **16384** (PR) | 8192 |
| `storage_mb` | 10240 | 10240 |
| `allow_internet` | **true** (downloads `all-MiniLM-L6-v2` + nltk) | (unset) |
| `environment.env` | — | mounts `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` |
| reward weights | P0/13·.50 + P1/7·.35 + P2/2·.15 | P0/9·.50 + P1/7·.35 + P2/3·.15 |

Notes from `Dockerfile` / `tests/test.sh`:
- **Skills are baked into the image** in BOTH tasks: `COPY skills /root(/app)/.claude/skills`
  plus `.codex / .opencode / .goose / .factory / .agents`. This is the documented
  no-op antipattern (`task-review` SKILL.md gotcha #1: *"the without-skills experiment
  becomes a no-op — agent sees the skill regardless of whether -s was passed"*).
  **Resolution:** the PR #372 page states the without-skills runs had the *"skills
  directories temporarily disabled, confirming true comparison."* The lower no-skills
  scores (below) corroborate that the baked skills were not effectively used — so the
  baseline was clean in practice, with the Dockerfile carrying only a latent risk.
- **No per-test timeouts** anywhere (no `pytest-timeout`, no `signal.alarm`); a whole
  test file is bounded only by `verifier.timeout_sec`.
- taxonomy `test.sh` runs pytest via `uvx` (isolated) and contains a stray `sleep 120`
  after scoring — must fit inside the 180s verifier window.
- trend `test.sh` installs pytest at runtime (`pip install` in test.sh — itself a minor
  antipattern the review flags) and has a vestigial "sleep 10 minutes" comment but
  `exit 0`s immediately.
- trend downloads its dataset at **build** time (`download_data.py`), so the agent budget
  isn't spent on data fetch; taxonomy fetches the embedding model at **agent run** time
  (counts against the 500s).
- Stale comments reveal iteration: taxonomy "removed `test_no_duplicate_category_names`,
  `test_parent_child_semantic_coherence`"; trend test.sh still cites an old "P0/5" formula
  (now P0/9). Test *cases* are parametrized: trend 15 functions → **19 cases**; tax 22 = 22.

---

## 2. What I actually ran (harbor) vs declared

| Dimension | Declared | What I ran | Comparable? |
|---|---|---|---|
| Harness/agent | `bench eval create -a claude-agent-acp` (+ codex) | `harbor run -a claude-code` (Claude only) | ⚠️ different adapter & token accounting |
| Model | 4.5-class Claude + Codex (see §3) | `claude-opus-4-8` | ⚠️ newer/stronger; the core confound |
| **taxonomy cpus/mem** | **8 / 16384** | **4 / 12288** (capped to host) | ❌ halved cores — slows embeddings |
| trend cpus/mem | 2 / 8192 | host 4-CPU (≥ asked) | ✅ |
| **agent timeout** | tax 500 / trend 900 | **overridden** via `--agent-timeout-multiplier`: trend-skills ×20, **all no-skills ×500** (≈unbounded) | ❌ deliberately removed the binding constraint for no-skills |
| verifier timeout | 180 / 200 | unchanged (verifiers completed) | ✅ |
| reasoning_effort | trend=high | harbor default for claude-code | ⚠️ |
| skills (with) | `-s` flag + baked dirs | `--skills` + original image | ✅ effectively |
| skills (without) | dirs *temporarily disabled* | **skills-stripped image** (COPY removed + dir deleted) | ✅ mine is definitively clean |
| trend API keys | mounted, **unused by grader** | mounted noop | ✅ vestigial either way |

The two intentional deviations that matter most: **(a)** I capped taxonomy to 4 CPU, and
**(b)** I gave the no-skills runs an effectively unbounded agent budget. Both directly
affect the headline taxonomy-no-skills cell.

---

## 3. Contributor eval records (verbatim, from the PR pages)

### #570 taxonomy (PR page model label: "Claude opus-4.5")
| config | result |
|---|---|
| oracle | 22/22 (100%) |
| with skills | **22/22 (100%)**, **101 output tokens** |
| without skills | **12/22 (62%)**, 371 tokens, "Incomplete" |
| Codex with skills | 100% (10m 50s) |
| Codex without skills | **0% (timeout)** |
Reviewer (yulinl2, Jan 23): *"lgtm, scanned thru the traj's… merge after fixing pre-commit."*
Without-skills failure detail: **27,785 prefix-removal violations**, 4,043 special-char
violations, 56/80 sibling pairs >30% overlap, 5 categories <70% coverage.

### #372 trend (PR page model labels: "claude-sonnet-4-5", Codex "gpt-5.2")
| agent | skills | accuracy | tests |
|---|---|---|---|
| oracle | — | 100% | 15/15 |
| Claude | yes | 100% | 15/15 |
| Claude | no | **84.44%** | 12/15 |
| Codex | yes | 95% | 14/15 |
| Codex | no | **84.44%** | 12/15 |
Per-priority (Claude **without** skills): P0 8/9, P1 7/7, **P2 1/3**.
Tokens/runtime: with-skills **4,243,203 in / 844 out / 7m59s**; without **1,313,020 in /
170 out / 8m20s**. Codex both **timed out at ~15 min** (still 95% with skills) →
reviewer recommended **`timeout_multiplier` 1.5–2.0**. Root cause without skills:
*"both agents incorrectly zero-filled intensive margin data."*

---

## 4. Timeout analysis — the decisive axis

1. **taxonomy 500s is the binding constraint, and CPU count moves the cutoff.** Contributor
   (8 CPU) finished no-skills in time → 62%. I (4 CPU) timed out → 0%. Halving cores roughly
   doubles the embedding wall-clock on 10,939 paths, pushing a borderline run over 500s. So
   **my "0% @budget" is an artifact of the CPU cap, not a capability result** — the clean
   capability number is the unbounded **78%** (17/22, same failure categories as the
   contributor's 62%: prefix removal, depth, coverage).
2. **Codex timed out at ~15 min on trend even with skills** (still 95%) — i.e., the 900s budget
   was already tight for a *thorough* agent before opus-4.8 existed. My no-skills ×500
   multiplier removes this ceiling entirely, which is why I measure capability, not
   capability-under-budget.
3. **No per-test timeouts** means a single slow test can't be isolated; only the whole-file
   `verifier.timeout_sec` (180/200s) bounds grading — fine here since verifiers completed.
4. **Net:** holding the agent budget fixed across model generations measures *efficiency +
   capability*; my unbounded no-skills runs deliberately isolate *capability*. The two
   questions have different answers for taxonomy (0% vs 78%) and the same answer for trend.

---

## 5. Corrections this forces on `THEORY.md`

- **Model ID:** THEORY.md said "opus-4.5" uniformly. The PR pages actually label
  taxonomy as opus-4.5 but **trend as sonnet-4-5** (Codex gpt-5.2 vs my note of gpt-5.5).
  So the contributor→me comparison spans **both a tier and a generation jump** (≥ sonnet-4-5
  → opus-4-8), which *strengthens* "capability absorbed the skill" but means it is **not a
  clean single-generation delta.** Exact IDs are WebFetch-unreliable.
- **trend with-skills P2 (cross_file_consistency):** the contributor's same-skill run scored
  **P2 3/3**, mine scored **2/3**. Identical skill, different outcome ⇒ confirms my −5pp is
  **L4 implementation variance at n=1**, not a skill regression.
- **Baseline cleanliness:** add that the baked-skills antipattern was present but neutralized
  by disabling the dirs for no-skills (per #372 page); my stripped image is independently clean.
- **History:** #570 was merged, **reverted (#610), then re-added** — the task itself churned,
  another reason to treat single snapshots cautiously.
