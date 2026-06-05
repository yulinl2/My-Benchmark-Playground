# harness — response + trajectory collection

Runs models over `question_bank/bank.jsonl` and saves, per (model, question),
the **final answer**, the **extended-thinking trajectory**, token usage, stop
reason, and timing.

**This harness only collects. It does not grade.** Grading and scoring are a
separate concern (see *Grader* below) so we can iterate on prompts/models and on
the rubric independently.

## Usage

```bash
# No-cost: build prompts + write stubs, no API calls
python harness/run_models.py --dry-run --limit 3

# Cheap full pass (pipeline/dataset bootstrap)
python harness/run_models.py --models claude-haiku-4-5-20251001

# Stronger signal (more $$): one or more models, full bank
python harness/run_models.py --models claude-sonnet-4-6
python harness/run_models.py --models claude-sonnet-4-6,claude-opus-4-8

# Subsets
python harness/run_models.py --models claude-sonnet-4-6 --filter-level ms
python harness/run_models.py --models claude-sonnet-4-6 --filter-part probability --filter-year 2024
python harness/run_models.py --models claude-sonnet-4-6 --ids 2024-summer-probability-q1
```

Reads `ANTHROPIC_API_KEY` (and `ANTHROPIC_BASE_URL` if set). Pure stdlib — no
`pip install`. Runs are **resumable**: an existing output file is skipped unless
`--overwrite`. Concurrency via `--concurrency` (default 4).

Key flags: `--max-tokens` (16000), `--thinking-budget` (8000; `0` disables
thinking), `--retries` (3, exp backoff on 429/5xx), `--timeout` (600s),
`--run-id`, `--limit`.

## Output layout

```
harness/runs/<run_id>/
  manifest.json                  # run config + question ids
  results.jsonl                  # one line per (model,question) — the dataset
  summary.json                   # {ok, error, skipped, dry-run}
  <model>/<question_id>.json     # full per-call record
```

### Per-call record

```jsonc
{
  "question_id": "2024-summer-probability-q1",
  "model": "claude-sonnet-4-6",
  "exam": { "year": 2024, "term": "summer", "level": "phd", "part": "probability" },
  "request": { "system": "...", "user": "<rendered problem>",
               "max_tokens": 16000, "thinking_budget": 8000 },
  "response": {
    "id": "msg_...", "stop_reason": "end_turn", "usage": { ... },
    "thinking": "<full reasoning trajectory>",
    "text": "<final answer>",
    "content_blocks": [ /* raw blocks, for fidelity */ ]
  },
  "timing": { "started": "...", "ended": "...", "seconds": 41.2 },
  "error": null
}
```

## Cost notes (ROI-first)

Output tokens dominate. Rough per-full-bank (95 questions, thinking on):
**haiku ≈ a few $, sonnet ≈ low tens of $, opus ≈ ~100+ $.** Start cheap to
bootstrap the dataset and the grader; spend on stronger models only for the
runs you actually want benchmark signal from. Use `--filter-*` to scope.

Collected run outputs are committed (the container is ephemeral, so the dataset
must be in git to survive).

## Grader — separate, not built yet

Scoring lives outside this harness. A grader will read `results.jsonl` +
`question_bank/bank.jsonl` (and, where present, the official `solution`) and emit
scores. Tracked separately; do not couple it into collection.
