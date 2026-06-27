# Long-Context Attention Expressivity Separation

> An **orphan research line** (no shared history with the playground `main`).
> Root branch: `research/long-context-attention-expressivity-separation`.
> Working branch: `claude/long-context-task-distribution-2iydu1`.

## One-sentence thesis

There exists a family of **long-context, fully self-contained** tasks whose
**optimal attention score distribution is computable from the task input alone**
(no external knowledge), such that a fixed **softmax-attention** Transformer can
realize it, but **any linear-attention model with fixed parameters / layers /
width cannot hit it with high probability** — and as the task space is enriched
(context length, key cardinality), the gap is forced to grow without bound.

The program runs the argument first on **numeric functions** (where the optimal
attention map is a closed-form matrix), then lifts it to **natural-language
tasks**, and validates the NL lift on commercial softmax models (e.g. Haiku) via
in-session sub-agents.

## Why this is interesting

"Linear attention is all you need" claims rest on *empirical* parity at a fixed
scale. The interesting scientific question is **expressivity**: is the parity an
artifact of the benchmark, or fundamental? If we can *design* a self-contained
task distribution that is

1. trivially solvable given the input (the answer is a deterministic function of
   the prompt — no memorized world knowledge),
2. realizable by softmax attention at fixed cost, and
3. provably **not** realizable by linear attention at any fixed cost as the task
   scales,

then "linear == softmax" is false in the strong (worst-case-over-task-family)
sense, and we have a *generator* of adversarial long-context benchmarks rather
than a single hand-picked example.

## Repository map

| Path | Contents |
|------|----------|
| `docs/00_research_proposal.md` | The full proposal: question, formalization, the two separation theorems (rank bound + recurrent-state communication bound), and the falsifiable predictions. |
| `docs/01_task_family_spec.md`  | Formal definitions of the task family `T(N, k, ρ)` and its three concrete members (Gather/Permute, MQAR, Chain-Tracking). |
| `docs/02_experimental_plan.md` | Numeric experiments, NL lift, and the Haiku sub-agent verification protocol. |
| `docs/03_related_work.md`      | Literature anchors (linear attention, SSMs, MQAR/Zoology/Based, expressivity/communication lower bounds) with verified arXiv ids, and what is novel here. |
| `docs/04_findings_generalization.md` | What is established so far: seven-family generator (breadth), multi-layer numeric result, and the Haiku scaling-sweep fingerprint (depth). |
| `src/numeric/`                 | numpy: softmax vs. linear attention, generators with closed-form `A*`, the rank-separation proof (`rank_separation.py`), trained curves (`train.py`), and the multi-layer demo (`depth_separation.py`). |
| `src/nl/`                      | NL generators (`task_generator.py` + `extra_tasks.py`), graders, the base-suite Haiku harness (`run_haiku_verification.py`), and the scaling sweep (`sweep.py`). |
| `results/`                     | Committed run outputs (numeric `.json`, NL `.json`, `sweep_results.json`) + `RESULTS.md`. |
| `app/`                         | Interactive React audit console (Vite). Reads the committed result JSONs; includes an interactive rank explorer and live in-browser task generators. `cd app && npm install && npm run dev` (prebuilt `dist/` also committed). |

## Quick start

```bash
python3 src/numeric/rank_separation.py      # analytic: permutation needs rank N
python3 src/numeric/train.py                 # empirical: linear head plateaus, softmax solves
python3 src/nl/task_generator.py --demo      # print sample NL instances
```

See `docs/02_experimental_plan.md` for the Haiku sub-agent runs and
`results/` for outputs already captured in this branch.
