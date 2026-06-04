# routine-bot — email → fresh Claude Code run

A minimal, working scaffold for "send an email, a Claude Code run wakes up and
does the full task." It uses **Claude Code Routines** (research preview) as the
execution layer — no self-hosting, runs on Anthropic's cloud with your laptop
closed.

## How it works

```
email  →  Gmail label  →  Apps Script poller (1 min)  →  POST /fire (text = email body)
                                                              │
                                              fresh Claude Code cloud session
                                                              │
                                  reads MEMORY.md → does task (PROMPT.md) → appends MEMORY.md → reports
```

The routine config is the persistent "master bot." Each fire is a **fresh
session** (the docs confirm the repo is re-cloned every run), so continuity
lives in `MEMORY.md` in the repo, not in any warm session.

## One-time setup

1. **Create the routine** at <https://claude.ai/code/routines> → **New routine**:
   - **Prompt:** paste [`PROMPT.md`](./PROMPT.md) verbatim.
   - **Repository:** this repo. Enable **Allow unrestricted branch pushes** so the
     run can commit `MEMORY.md` back to the durable branch (see *Memory* below).
   - **Trigger:** add an **API** trigger → **Generate token** (shown once — copy it).
2. **Wire the bridge:** open [`bridge/gmail-appscript.gs`](./bridge/gmail-appscript.gs)
   in a Google Apps Script project. Set `FIRE_URL` and store the token via
   *Project Settings → Script properties* (`ROUTINE_TOKEN`). Add a 1-minute
   time-driven trigger on `poll`.
3. **Gmail filter:** create a filter that applies the label `claude-task` to the
   mail you want to act on (e.g. `to:tasks+claude@yourgmail.com`). The poller only
   reads that label.

Send an email → within ~1 minute a new session appears in your routine's run list.

## Memory (the part that's a real decision, not solved magic)

A routine run can only persist state if its writes land somewhere the *next* run
reads. By default routines push to `claude/`-prefixed branches, which diverge
per run. Pick one:

- **A. Durable branch (this scaffold's default):** enable *Allow unrestricted
  branch pushes* and have the run commit `MEMORY.md` to `main`. Simple, but the
  bot writes to `main`.
- **B. Connector store:** keep memory in a connector (Google Doc, Linear, a DB)
  the routine reads/writes. No repo writes; better isolation. Swap the memory
  protocol in `PROMPT.md` to read/write the connector instead.

`PROMPT.md` is written for **A**; switching to **B** is a prompt edit only.

## Honest limits

- Research-preview API: the `/fire` shape ships under
  `anthropic-beta: experimental-cc-routine-2026-04-01` and may change.
- Runs draw down your subscription usage and a per-account daily routine cap.
- **Prompt injection:** the run acts autonomously (no approval prompts) on
  whatever arrives in `text`. Inbound email is attacker-controllable. Scope the
  repo, connectors, and network access to the minimum, and keep the Gmail filter
  tight so only trusted senders reach the label.
