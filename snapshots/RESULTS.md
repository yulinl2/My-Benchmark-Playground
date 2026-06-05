# SkillsBench snapshots on Opus 4.8 Max

Running two SkillsBench **contributor PR snapshots** with **Opus 4.8 Max** (`claude-opus-4-8`)
as the model. The contributors only benchmarked older Claude models, so these runs fill in
the 4.8 column. Task definitions, data, skills, and verifiers are taken verbatim from the two
*contributor* PR branches (`refs/pull/570/head`, `refs/pull/372/head`) — not upstream `main`.

Two tracks are recorded:

- **Track B — official `harbor` harness** (`harbor run -a claude-code -m claude-opus-4-8`,
  docker sandbox): the model drives the task autonomously end-to-end, exactly as SkillsBench
  evaluates. This is the authoritative number.
- **Track A — direct runs on this machine** (kept as a cross-check): with-skills = the
  contributors' own bundled pipeline driven in place; without-skills = Opus 4.8 Max's own
  from-scratch solution (`solve_noskills_opus48.py`). Graded by each task's own
  `tests/test_outputs.py` via `grade_*.py` (re-applying the fork's P0/P1/P2 weighting).

## Track B — official bench harness on `claude-opus-4-8`

| Snapshot | oracle | claude-skills | claude-noskills |
|---|---|---|---|
| **PR #570** `taxonomy-tree-merge` | **1.0000** | **1.0000** | **0.7846** † (17/22) |
| **PR #372** `trend-anomaly-causal-inference` | **1.0000** | **0.9500** | **1.0000** ‡ |

All agent cells use `claude-code -m claude-opus-4-8`. No-skills cells use an effectively
unbounded agent timeout (`--agent-timeout-multiplier 500`) so the model isn't killed
mid-solve.

† taxonomy without-skills: under the task's **default 500s** budget the agent was still
building embeddings + clustering 10,939 paths when it was killed → never wrote the CSVs →
**0.0**. With the **unbounded** budget it finished (89 steps) and scored **0.7846 (17/22)** —
it gets the structure/format right but misses some of the harder clustering-quality
constraints. (Contributor-reported without-skills for this task on older models: 62%.)

The trend **with-skills** agent (claude-opus-4-8) scored **0.9500** in ~12 min / 37 steps
running the full clean → Prophet → feature-engineering → DiD pipeline.

‡ trend without-skills scored **1.0000** (30 steps, ~11 min) under the unbounded budget —
4.8 wrote the whole pipeline itself and passed all 19 checks, edging out its own with-skills
run. Strong evidence the model can do this task from scratch when not time-limited.

### Per-cell run metadata (Track B, claude-opus-4-8)

| Cell | reward | wall time | steps | tools (Bash/Read/Write+Edit) | out tok | cost | key libs |
|---|---|---|---|---|---|---|---|
| trend with-skills | 0.9500 | 11m49s | 37 | 22 / 8 / 5 | 30.8k | $2.49 | prophet, sklearn, statsmodels (used the skill) |
| trend without-skills | 1.0000 | 11m15s | 30 | 19 / 0 / 5 | 40.4k | $2.11 | statsmodels DiD (own pipeline, no prophet) |
| taxonomy without-skills | 0.7846 | 39m34s | 89 | 56 / 7 / 24 | 87.1k | $6.59 | sentence-transformers, KMeans, sklearn, networkx |

(Cost is mostly cached input — e.g. taxonomy read 7.22M cached of 7.35M prompt tokens. Oracle
and the two with-skills/with-skills cells that ran before a mid-task sandbox reset are recorded
at reward only; the three cells above were re-run after the reset and carry full `job_result.json`.)

### Failure analysis (the non-1.0 cells)

**trend with-skills = 0.9500** — 18/19 tests pass; the *only* miss is `test_cross_file_consistency`
(a **P2**, the lowest-weight bucket: 3 P2 tests, losing one = 0.15→0.10 → 0.95). The skill's
Prophet pipeline emitted a cleaned *extensive* purchase file missing **228 respondent IDs** that
exist in the cleaned survey file (`Missing: 228, Extra: 0`). The from-scratch run kept the two
files ID-consistent, so without-skills actually scored **1.0** here — the bundled skill is not
strictly better on every check.

**taxonomy without-skills = 0.7846** — 17/22 pass; the 5 failures are **3 P0 + 2 P1**
(`(10/13)·0.5 + (5/7)·0.35 + (2/2)·0.15 = 0.7846`). They are all *output-contract* details, not
clustering quality:
- `test_prefix_removal` — kept full ancestor-prefixed leaf names (27,875 violations); spec wants the
  parent prefix stripped at each level.
- `test_hierarchy_coverage` — the 15 invented `unified_level_1` labels (`Apparel | Accessories`, …)
  have 0% path coverage because they don't prefix their child paths.
- `test_depth_filtering` — some branches exceed the max depth of 5.
- `test_full_mapping_format`, `test_path_representativeness` — related format/representativeness.
The clustering, naming constraints, lemmatization, dedup, sibling-distinctiveness, balance and
no-empty-cluster checks all pass — i.e. 4.8 builds a sound taxonomy from scratch but diverges on the
precise path-encoding convention that the **skill** spells out (with-skills = 1.0).

### Reference / harness notes
The repo ships no custom agent — harbor's built-in `claude-code` adapter drives the model from each
task's `instruction.md`. The **oracle** cell runs the task's `solution/solve.sh` (a deterministic
reference pipeline) → 1.0. `claude-skills` mounts `environment/skills`; `claude-noskills` uses a
skills-stripped image. All taken verbatim from the contributor PR branches.

Harbor: `harbor run -p tasks/<task> -a claude-code -m claude-opus-4-8` (docker sandbox).
`claude-skills` deploys the fork's skills via `--skills`; `claude-noskills` uses a
skills-stripped image variant. Host-fit note: taxonomy `task.toml` was capped from
8 CPU / 16 GB to 4 CPU / 12 GB to match this 4-CPU / 15 GB host (no logic/test change).
The egress proxy's MITM CA was baked into a local `python:3.11-slim` base so in-container
pip/npm/HTTPS work; this is an environment fix, not a task change.

## Track A — direct runs (cross-check)

| Snapshot | with-skills (contributor pipeline) | without-skills (4.8 from-scratch) |
|---|---|---|
| **PR #570** `taxonomy-tree-merge` | **1.0000** (22/22) | **0.8231** (P0 11/13, P1 5/7, P2 2/2) |
| **PR #372** `trend-anomaly-causal-inference` | **1.0000** (19/19) | **1.0000** (19/19) |

Reward = `P0_frac*0.50 + P1_frac*0.35 + P2_frac*0.15` (each task's own formula).

### Track A notes
- **Taxonomy without-skills (0.82):** 4.8's from-scratch clustering left a couple of
  top-level clusters unnamed, so some rows lack `unified_level_1` — failing
  `test_depth_filtering`, `test_hierarchical_structure`, `test_mapping_completeness`,
  `test_source_balance`. Everything else passes.
- **Trend without-skills (1.00):** 4.8's from-scratch clean → Prophet → DiD pipeline passes
  all 19 checks, vs. the contributors' reported 84% (12/15) without-skills on their older model.
- Both trend conditions independently surface plausible COVID-era anomalies — surges in
  protective gloves / toilet paper / drink concentrate, slumps in shoes / candy.

## Files
- `pr570-taxonomy-tree-merge/`, `pr372-trend-anomaly-causal-inference/`
  - `task/` — verbatim task from the contributor PR branch
  - `solve_noskills_opus48.py` — 4.8 from-scratch solution (Track A, without-skills)
  - `output_with_skills/`, `output_without_skills/` — graded deliverables (large CSVs gitignored)
- `grade_taxonomy.py`, `grade_trend.py` — invoke each task's own verifier + weighting
- Large/re-creatable artifacts (raw 76MB data, 70MB filtered CSVs, venvs) are gitignored.
- `harbor_oracle/`, `harbor_with_skills/`, `harbor_without_skills/` — Track B reward + trajectory per cell.
