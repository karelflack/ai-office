# AI Office — Agent Entry Point

Welcome. If you are a Claude Code agent starting a session in this repository, follow these steps before doing anything else.

## Session Startup Protocol

1. **Read team memory**
   Load `memory/team_memory.json`. This is the authoritative state of the team. Check:
   - `project_status` — what phase is the project in?
   - `active_decisions` — are there constraints that affect your work?
   - `agent_notes` — has a previous agent left you a message?

2. **Identify your role**
   Find your role file in `agents/`. Read it fully. Your role defines:
   - What you are responsible for
   - Which tools you may use
   - How you should read and write team memory

3. **Check for assigned work**
   Look in `tasks/active/` for any task file assigned to your role. Task files are named `YYYY-MM-DD-<slug>.md` and contain a role header. Only pick up tasks assigned to you.

4. **Do the work**
   Follow the instructions in the task file. Stay within your role's responsibilities.
   - Save all deliverables (documents, plans, research, content, code) to `output/`
   - Name files clearly: `YYYY-MM-DD-<short-description>.<ext>`

5. **Update memory after completing any task**
   - Append a note to `## Agent Notes` in `memory/team_memory.md`
   - Update the corresponding field in `memory/team_memory.json`
   - Move the task file from `tasks/active/` to `tasks/completed/`
   - Update the table in `output/README.md` with your new file

6. **Commit and push your work**
   Run the following after completing a task:
   ```
   git add -A
   git commit -m "agent(<your-role>): <short description of what was done>"
   git push
   ```

## Notes
- Do not skip the memory read step — other agents may have left important context
- Do not overwrite another agent's notes — only append
- All deliverables go in `output/` — never scatter files across the root of the repo
- If you are unsure what to do, leave a note in `## Agent Notes` and stop

## Upstream Output Rule
Every agent must list at the top of their completion doc which upstream output files they actually read. If a required upstream file does not exist yet, stop and leave a note — do not proceed with assumptions.

Example:
```
## Upstream outputs read
- projects/my-project/output/2026-04-01-system-architecture.md (bjorn)
- projects/my-project/output/2026-04-01-compliance-checklist.md (magnus)
```

## Phased Execution — Non-Negotiable Ordering Rules

These rules exist because parallel agents cannot read each other's output. Violating them causes silent coordination failures.

**Phase 1 — runs first, in parallel:**
- bjorn (architecture)
- dag (infrastructure, Docker, CI/CD)
- magnus (compliance, GDPR, legal) — required whenever the project touches user data, auth, or personal information

**Phase 2 — runs after Phase 1 is complete:**
- arve (implementation) — must explicitly reference bjorn's architecture output AND magnus's compliance output if magnus ran. Must implement any LAUNCH BLOCKER items from magnus's checklist that are in scope.
- ingrid, jorunn, else, frode — may run in parallel with arve if their inputs are ready

**Phase 3 — runs after Phase 2:**
- odd (API testing)
- per (performance benchmarking)

**Never run arve in parallel with magnus on any project touching user data.** Magnus's compliance output is an input to arve's implementation, not a parallel concern.
