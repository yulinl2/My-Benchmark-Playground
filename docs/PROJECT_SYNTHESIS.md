# 🧭 Project synthesis — one page, everything, linked

> **TL;DR**
> - 📚 Built a **95-problem** question bank from Rutgers Stat qual exams (PhD 2018–2025 + recent MS), every entry linked to its source PDF+page. → [`bank.jsonl`](../question_bank/bank.jsonl)
> - 🤖 Built a **multi-provider collection harness** (GPT-5.5 + Claude, trajectories + cost) and ran a **cross-model hardness screen** — GPT-5.5, Haiku, + Opus sub-agents — (**570 responses, $46**). → [`harness/`](../harness)
> - 🎯 Goal = **filter the best contribution candidates** by cross-model behavior. Top candidates are the **hardest PhD theory problems**. → [issue #8](https://github.com/yulinl2/My-Benchmark-Playground/issues/8) · [interactive demo](../demo/index.html)
> - 🚧 **Gate not yet crossed:** ground-truth **grading** (deferred). The shortlist is a *behavioral prefilter, not a correctness verdict.*

---

## 🔢 By the numbers

| | |
|---|---|
| Questions in bank | **95** (PhD 62 · MS 33) |
| Source PDFs linked | 29 (0 dangling) · 9 carry datasets |
| Screen responses collected | **570** (GPT-5.5 + Haiku × **95** × k=3) |
| Sub-agent solutions (Opus, closed-book) | 8 (top theory candidates) |
| Trajectories captured (free haiku pass) | 95 (`haiku-full-v1`) |
| Total spend to date | **~$54** API (calib $7.6 · screen $46.4) · sub-agents session-billed |
| Output tokens collected | 4.0M (screen) + 0.4M (haiku) |
| AI-audit (vs source text) | **95/95 pass** (3 corrected) |
| Human `verified` | 0 / 95 (reserved for human sign-off) |

---

## 🔭 The pipeline

```
PDFs ──extract──▶ question bank (95) ──┬─▶ audit UI (verify + grade-type)  [human gate, built]
                                       └─▶ harness ──▶ screen (570 resp, 3 models) ──▶ behavioral analysis ──▶ candidate shortlist
                                                                                                         │
                                                                                          GRADER (deferred) ─▶ confirmed-hard ─▶ contribute
```

## 🧰 Artifacts — where to click

| Thing | What it is | Link |
|---|---|---|
| **Bank** | 95 curated questions (JSONL) | [`question_bank/bank.jsonl`](../question_bank/bank.jsonl) |
| Schema | entry contract (+ `grading_type`, `data`, `level`) | [`schema.json`](../question_bank/schema.json) |
| Build/validate | validator + coverage | [`scripts/build_bank.py`](../scripts/build_bank.py) |
| Transcription status | per-exam table + backlog | [`docs/transcription_status.md`](./transcription_status.md) |
| **Harness** | multi-provider collector (GPT + Claude, cost) | [`harness/run_models.py`](../harness/run_models.py) |
| Analysis | behavioral candidate scorer | [`harness/analyze_screen.py`](../harness/analyze_screen.py) |
| **Audit UI** | browser review tool (verify, grade-type) | [`audit/index.html`](../audit/index.html) |
| **Demo** | interactive results explorer | [`demo/index.html`](../demo/index.html) |
| Screen shortlist | ranked tables | [`analysis.md`](../harness/runs/screen-v1/analysis.md) · [`analysis_theory.json`](../harness/runs/screen-v1/analysis_theory.json) |

## 🧪 What we ran

**Calibration** ([`calib-v1`](../harness/runs/calib-v1), [issue #7 comment](https://github.com/yulinl2/My-Benchmark-Playground/issues/7#issuecomment-4640787118)) — 10 problems × {GPT-5.5, Opus 4.7} × k=1, high effort. Confirmed availability + measured cost. Two fixes it forced:
- 🩹 **Opus adaptive thinking**: `thinking.type=enabled` is rejected by Opus 4.7; needs `thinking.type=adaptive` + `output_config.effort`. ([commit `e3b4339`](https://github.com/yulinl2/My-Benchmark-Playground/commit/e3b4339))
- 🩹 **`--k`** repetitions were missing. ([commit `1bebc14`](https://github.com/yulinl2/My-Benchmark-Playground/commit/1bebc14))

| model | $/run | out mean | reasoning mean |
|---|---|---|---|
| GPT-5.5 | $0.145 | 9,485 | 7,077 |
| Opus 4.7 | $0.613 | 8,025 | 6,215 |
| Haiku 4.5 | ~$0.02 | 4,414 | 2,390 |

**Screen** ([`screen-v1`](../harness/runs/screen-v1)) — GPT-5.5 + Haiku × **95** × k=3, high effort. **570/570 ok, $46.43.** Plus a third model — **Claude Opus sub-agents, closed-book (no web)** — on the top 8 theory candidates (session-billed; final solutions in [`subagent-v1/raw`](../harness/runs/subagent-v1/raw)). Every problem (incl. the 9 dataset-backed ones) is collected and accessible — nothing hidden.

## 🎯 Candidate shortlist (theory) — [explore interactively »](../demo/index.html)

Re-ranked within the 60 theory problems (applied is **down-weighted for ranking but never hidden** — every problem stays accessible in the [demo](../demo/index.html); see finding below). A third test model — **Claude sub-agents (Opus tier, closed-book)** — is captured for the top candidates. Full results: [issue #8](https://github.com/yulinl2/My-Benchmark-Playground/issues/8).

| # | qid | why it's a candidate |
|---|---|---|
| 1 | `2021-summer-math-stat-q2` | GPT burned **18.6k** reasoning tokens, **truncated 1/3**, answers drift |
| 2 | `2018-summer-math-stat-q2` | instability **0.56** (logistic-efficiency proof) |
| 3 | `2018-summer-probability-q2` | instability 0.55 (random-walk mixing) |
| 4 | `2018-summer-probability-q1` | instability 0.60 (Hájek / survey sampling) |
| 5 | `2022-fall-math-stat-q4` | top **MS** candidate (hidden confounders / IV) |

🧠 **17 of the top 18 are PhD** — MS comprehensive problems mostly get solved consistently.

## 📐 Scoring logic (declared + linked)

Implemented in [`harness/analyze_screen.py`](../harness/analyze_screen.py) (see `zscores()` and the `score =` line). Per problem, each signal is **z-scored across problems**, then:

```
score = 1.0·z(gpt_reasoning_tokens)     # frontier effort
      + 1.5·z(answer_instability)       # 1 − self-consistency of final answer across k=3 (number-set Jaccard)
      + 1.0·z(truncation_rate)          # frontier hit the output cap
      + 0.5·z(output_bulk)              # gpt+haiku output length
      + 0.5·z(hedging)                  # uncertainty markers
```
Theory view re-z-scores the same signals **within the 60 theory problems**. **Proxy hardness — not a correctness verdict.**

## 💸 Costs & budget

Plan + measured: [issue #7](https://github.com/yulinl2/My-Benchmark-Playground/issues/7). Funnel ≈ $106–137 ($53–68 batched). Spent so far **~$54** API (+ sub-agents, session-billed). Ceiling **~$150 Anthropic + ~$50 OpenAI**.

## 🔑 Key findings & decisions

- ⚠️ **Proxy confound:** open-ended *applied* problems score high just for lacking a crisp answer → **down-weighted in the ranking but kept fully accessible** in the demo (not hidden); they're not auto-gradable anyway. ([commit `4ca2c69`](https://github.com/yulinl2/My-Benchmark-Playground/commit/4ca2c69))
- 🧾 **Attribution:** all AI commits authored `Claude (AI assistant)` + session trailer. ([issue #2](https://github.com/yulinl2/My-Benchmark-Playground/issues/2))
- 🧠 **No autonomous loop exists** — progress runs on background-task notifications only; no `send_later`, no Routine set up.

## 🚧 Open gates / next

1. **Grader** (deferred) — confirm which shortlisted problems the frontier fails **0/3**. The real candidate gate.
2. **Parked Opus confirmation run** — only after grading (gates on GPT-5.5 misses). ~$53–68 batched.
3. **Audit** the 95 (all `verified:false`) via [`audit/index.html`](../audit/index.html).
4. **MS backlog** (older + scanned exams) — [issue #6](https://github.com/yulinl2/My-Benchmark-Playground/issues/6).

## 🗂️ Index — issues & PRs

| # | title |
|---|---|
| [PR #1](https://github.com/yulinl2/My-Benchmark-Playground/pull/1) | Question bank |
| [PR #3](https://github.com/yulinl2/My-Benchmark-Playground/pull/3) | routine-bot scaffold |
| [#2](https://github.com/yulinl2/My-Benchmark-Playground/issues/2) | Design: reliable event-triggered runs |
| [#6](https://github.com/yulinl2/My-Benchmark-Playground/issues/6) | Backlog: older MS exams |
| [#7](https://github.com/yulinl2/My-Benchmark-Playground/issues/7) | Budget plan + measured |
| [#8](https://github.com/yulinl2/My-Benchmark-Playground/issues/8) | Screen results / shortlist |

<sub>🤖 Generated with Claude Code — https://claude.ai/code/session_011sN6e4S2uhqzeoxSTPh1Mp</sub>
