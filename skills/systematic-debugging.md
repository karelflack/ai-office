# Systematic debugging

**What this does:** Replaces guess-and-check debugging with a methodology. Bisect, hypothesise, isolate, verify. Same approach senior engineers use when a bug doesn't yield to staring at the code.

**Why it matters:** Hard bugs aren't solved by reading code harder. They're solved by narrowing the search space until the bug has nowhere to hide. This skill lays out the moves.

---

## The pipeline

When a bug resists the obvious fix, work through these in order:

### 1. Reproduce reliably

You cannot debug what you cannot reproduce. Build a minimal reproduction:
- Smallest input that triggers it
- Cleanest environment (no unrelated state)
- Shortest path from start to bug

If you can't reproduce it consistently, that *is* the first bug to solve. Intermittent failures usually mean a hidden state — race, cache, timezone, environment.

### 2. Bisect

Narrow the location:
- **Time bisect** — `git bisect` to find the commit that introduced it.
- **Code bisect** — disable half the code, see if the bug remains. Halve again.
- **Input bisect** — strip the input until the bug stops. The last thing you removed is involved.

Bisecting turns a 1000-possibility search into 10 binary questions.

### 3. Hypothesis-driven

Don't change code at random. State a hypothesis, then design a test that distinguishes it from alternatives:
- Hypothesis: "The cache is returning stale data."
- Test that confirms: add logging at the cache read site; trigger the bug; check timestamps.
- Test that disconfirms: bypass the cache entirely; if the bug remains, the cache wasn't the cause.

If your test can't distinguish your hypothesis from another, design a better test.

### 4. Isolate

Once you've narrowed to a small region:
- Reduce to a unit test that captures the bug
- Run it in the smallest possible context (no test framework, no fixtures, just the function)
- Vary one input at a time

### 5. Fix and verify

The fix should:
- Make the unit test (from step 4) pass
- Address the cause, not the symptom (see `root-cause-first` skill)
- Not break other tests — re-run the full suite

## Anti-patterns

- **Stack-overflow-driven fixes.** Copying a fix without understanding what was wrong.
- **"It works on my machine."** Differences between environments are debugging signal, not noise.
- **Stop debugging when symptom goes away.** A bug that "stopped happening" without explanation is a bug waiting to happen.

## Output format

Document what you did so the next person doesn't repeat it:

```
## Debug log
- Reproduced with: [minimal repro]
- Bisected to: [commit / file / region]
- Hypothesis: [what I thought was wrong]
- Confirmed by: [evidence]
- Root cause: [actual cause]
- Fix: [what changed and why]
```
