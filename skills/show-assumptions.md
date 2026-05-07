# Show assumptions

**What this does:** Forces the agent to list its assumptions out loud at the start of a task, instead of burying them in the work. If an assumption is wrong, you can correct it before time is wasted on the wrong thing.

**Why it matters:** Most rework happens because an agent guessed at an unstated requirement and got it wrong. Stated assumptions are a free quality check — they catch mismatches before code is written, not after.

---

## When to use

At the start of any task where the brief is not 100% explicit. That's almost every task.

## How to apply

Before doing the work, write a short **Assumptions** block at the top of your output. Each line is one specific assumption you're making.

Good examples:
- "Assuming Postgres ≥ 14 — I'll use `gen_random_uuid()` instead of the uuid-ossp extension."
- "Assuming the API is internal-only — I won't add rate limiting or API keys."
- "Assuming users are authenticated by an upstream proxy — no login flow needed in this service."
- "Assuming 'fast' means p99 < 100ms based on the rest of the codebase's SLOs."

Bad examples (too vague to be useful):
- "Assuming standard practices."
- "Assuming the requirements are clear."
- "Following best practices."

## What counts as an assumption

If a downstream agent or a reviewer could look at your output and disagree with a choice you made, that choice is an assumption. Examples:
- Stack/library choices when the brief didn't specify
- Performance targets, scaling expectations
- Security model (who's authenticated, what's trusted)
- User personas or volume estimates
- Edge case behaviour (what happens on empty input, errors, retries)

## Format

Lead your output with:

```
## Assumptions
- [assumption 1]
- [assumption 2]
- [assumption 3]
```

If you have zero assumptions because the brief is fully explicit, say so:

```
## Assumptions
None — the brief specified [X, Y, Z] which fully determined the approach.
```

Don't pad the list. Three real assumptions beats ten generic ones.
