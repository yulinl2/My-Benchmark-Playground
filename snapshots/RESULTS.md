# SkillsBench snapshots on Opus 4.8 Max

Running two SkillsBench **contributor PR snapshots** with **Opus 4.8 Max** (`claude-opus-4-8`)
as the model. The contributors only benchmarked older Claude models, so these runs fill in
the 4.8 column. Task definitions, data, skills, and verifiers are taken verbatim from the two
*contributor* PR branches (`refs/pull/570/head`, `refs/pull/372/head`) — not upstream `main`.

Two tracks are recorded:

- **Track B — official `bench` harness** (`uv run bench eval create`, docker sandbox,
  `claude-agent-acp -m claude-opus-4-8`): the model drives the task autonomously end-to-end,
  exactly as SkillsBench evaluates. This is the authoritative number.
- **Track A — direct runs on this machine** (kept as a cross-check): with-skills = the
  contributors' own bundled pipeline driven in place; without-skills = Opus 4.8 Max's own
  from-scratch solution (`solve_noskills_opus48.py`). Graded by each task's own
  `tests/test_outputs.py` via `grade_*.py` (re-applying the fork's P0/P1/P2 weighting).

## Track B — official bench harness on `claude-opus-4-8`

| Snapshot | oracle | claude-skills | claude-noskills |
|---|---|---|---|
| **PR #570** `taxonomy-tree-merge` | **1.0000** | **1.0000** | **0.0000** † |
| **PR #372** `trend-anomaly-causal-inference` | **1.0000** | **0.9500** | **1.0000** ‡ |

† taxonomy without-skills ran under the task's default 500s agent budget and timed out
mid-clustering (see note below). No-skills runs are being re-run with an effectively
unbounded agent timeout (`--agent-timeout-multiplier 500`) so the model isn't killed
mid-solve; results will be updated.

The trend **with-skills** agent (claude-opus-4-8) scored **0.9500** in ~12 min / 37 steps
running the full clean → Prophet → feature-engineering → DiD pipeline.

‡ trend without-skills scored **1.0000** (30 steps, ~11 min) under the unbounded budget —
4.8 wrote the whole pipeline itself and passed all 19 checks, edging out its own with-skills
run. Strong evidence the model can do this task from scratch when not time-limited.

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

† **taxonomy claude-noskills = 0.0**: the agent (no skills) chose to build the embedding+clustering pipeline itself; it was still mid-clustering 10,939 paths when the 500s agent budget expired, so it never wrote the output CSVs (all verifier tests fail → 0). A clear demonstration of skill value under the task's time budget — with skills it reused the pipeline and scored 1.0. Trajectory saved in `harbor_without_skills/`.
