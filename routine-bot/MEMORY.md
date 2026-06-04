# routine-bot memory

Append-only long-term memory for the email-triggered routine. Each run reads this
file before acting and appends a dated entry after acting. Newest entries at the
bottom. Keep entries terse but quote the salient request text verbatim.

Format per entry:

```
## YYYY-MM-DD — <short title>
- Request (verbatim): "<the key ask>"
- Did: <what happened>
- Links: <PR / session / connector item>
- Decisions/assumptions: <anything chosen under ambiguity>
- Open follow-ups: <if any>
```

---

## 2026-06-04 — seed
- Request (verbatim): "(scaffold seed — no real request yet)"
- Did: Initialized memory file. First real run replaces this with its own entry.
- Links: routine-bot/README.md
- Decisions/assumptions: Memory persisted via the durable branch (option A in README).
- Open follow-ups: Decide A (durable branch) vs B (connector store) before relying on this in production.
