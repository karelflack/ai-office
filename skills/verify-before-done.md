# Verify before done

**What this does:** Stops the agent from saying "done" without actually checking. Instead of trusting that code looks right, the agent has to run it — build, test, smoke-check — and only declares the task complete after seeing it work.

**Why it matters:** The most common Claude failure is shipping code that looks correct but breaks at runtime. Reading code is not the same as running code.

---

## Rules

Before declaring any task complete, you MUST do at least one of the following — and report the result in your output:

1. **Run the build.** If there's a build step (`npm run build`, `tsc`, `cargo build`, `go build`), run it. Capture the exit code and any errors.
2. **Run the tests.** If tests exist, run them. Report which passed and which failed. Do not say "tests pass" without showing the output.
3. **Run the program.** For a CLI: invoke it with realistic input and capture output. For a server: start it and hit a health endpoint or a real route.
4. **Render the UI.** For a frontend change: open the page (in a browser, a screenshot, or via Playwright/Puppeteer) and confirm the change is visible and not throwing console errors.

If you cannot run the verification (missing tooling, sandbox limitation, environment unavailable), say so explicitly. Never claim the work is done while skipping verification silently.

## Forbidden phrases

Do not write any of these unless you have actually verified them:
- "This should work."
- "I believe this is correct."
- "This will fix the issue."
- "Tests should pass now."

Replace with what you actually observed:
- "I ran X and saw Y."
- "Build succeeded with no errors."
- "3 of 4 tests pass; the 4th fails because Z."

## Self-check before submitting

End your output with a one-line verification summary:

```
**Verification:** ran `npm test` — 14 passed, 0 failed. Started dev server, /health returned 200.
```

If the verification line is missing, the task is not done.
