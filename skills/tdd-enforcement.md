# TDD enforcement

**What this does:** Makes the agent write tests before the implementation, not after. Forces the test to fail first (proving it actually tests something), then writes the code that makes it pass.

**Why it matters:** Tests written after the fact often pass vacuously — they confirm whatever the code already does, not what it *should* do. TDD catches real defects because the test must fail before it can pass.

---

## The cycle

For every behaviour change, follow Red → Green → Refactor:

1. **Red.** Write a failing test that captures the behaviour you want. Run it. Confirm it fails for the *right reason* (the assertion fires; not because of an import error or syntax error).
2. **Green.** Write the simplest code that makes the test pass. No extras. No "while I'm here let me also..."
3. **Refactor.** With tests green, clean up. Re-run tests after each refactor — they must stay green.

## Rules

- **Never write code without a failing test that needs it.** If you can't write a test for it, you don't understand it well enough yet.
- **Never write multiple failing tests at once.** One test at a time. Get it green before writing the next.
- **The test must fail first.** If your new test passes immediately, your implementation already covered it (test is redundant) or your test isn't actually testing what you think it is.
- **Don't modify a test to make it pass.** That's working backwards. If a test fails after a refactor, the refactor broke a behaviour — fix the code, not the test.

## Output format

Show the cycle in your output:

```
### Red — written failing test
[test code]
Ran: pytest tests/test_x.py::test_new_behaviour
Result: FAILED — assertion `x == 5` failed (got 3)

### Green — minimal implementation
[code]
Ran: pytest tests/test_x.py::test_new_behaviour
Result: PASSED

### Refactor — cleaned up duplication
[refactor]
Ran: pytest tests/test_x.py
Result: All tests still pass
```

If a step is skipped (e.g., test passed without an implementation change), explain why.

## Exemptions

You may skip strict TDD only for:
- Pure refactors (no behaviour change) — but tests must still pass before and after
- Throwaway scripts (one-off scaffolding, exploration spikes) — say so explicitly

Never skip TDD because "it's faster" — it isn't, over the lifetime of the code.
