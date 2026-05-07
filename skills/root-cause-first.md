# Root cause first

**What this does:** Forces the agent to diagnose the underlying problem before patching anything. No more "let me try changing this and see if it works." Instead: figure out *why* it's broken, then fix the actual cause.

**Why it matters:** Most bugs that come back are bugs that were patched at the symptom, not the cause. A surface fix often hides the real issue and makes it harder to find next time.

---

## The rule

Before writing any fix, you must produce a written root-cause analysis. The fix comes after.

## Diagnosis steps (in order)

1. **State the symptom precisely.** What was expected, what actually happened. Include the exact error or unexpected behaviour.
2. **Reproduce it.** Confirm you can trigger it on demand. If you can't reproduce, that's the first problem to solve.
3. **Trace the path.** Where in the code does the symptom originate? Walk back through the call chain.
4. **Hypothesis.** What do you think the cause is? Be specific — "a race condition" is not a hypothesis; "X writes before Y reads because there's no lock around Z" is.
5. **Test the hypothesis.** Does adding a log, a breakpoint, or a small experiment confirm it? If not, your hypothesis is wrong — go back to step 4.
6. **Only now: fix.** And the fix should target the cause, not the symptom.

## Anti-patterns to avoid

- **Try-and-see.** Changing code and re-running to see if it helps, without a hypothesis.
- **Blanket exception handlers.** Wrapping the failing block in `try/except: pass` is a symptom fix, never a root-cause fix.
- **Adding retries to flakiness.** Retries hide the real cause; find why it's flaky first.
- **Tweaking until tests pass.** If you don't know why your change made the test pass, you don't know if you fixed it.

## Output format

Your fix output must include this section before the code changes:

```
## Root cause
**Symptom:** [what was observed]
**Cause:** [the underlying reason]
**Evidence:** [how you confirmed it]
**Fix approach:** [how you'll address the cause, not the symptom]
```

If you cannot identify the root cause, say so — and propose what additional information would let you find it. Do not patch blind.
