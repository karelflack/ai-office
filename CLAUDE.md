# AI Office — Agent Entry Point

Welcome. If you are a Claude Code agent starting a session in this repository, follow these steps before doing anything else.

---

## Session Startup Protocol

1. **Read your role**
   Find your role file at `agents/{your-agent-id}.md`. Read it fully. It defines your responsibilities, tools, memory categories, and peer review assignments.

2. **Read project memory**
   Load `projects/{slug}/memory/project_memory.json`. Check:
   - `description` — what is this project?
   - `agent_notes` — have previous agents left context?

3. **Read your memory categories**
   Your role file specifies which `projects/{slug}/memory/decisions/{category}.md` files to read before starting. These contain structured decisions from agents who ran before you. Do not skip this step.

4. **Read your task file**
   Find your task at `projects/{slug}/tasks/active/YYYY-MM-DD-<slug>.md`. Read it fully, including any `depends_on` or required upstream outputs listed.

5. **Do the work**
   Follow the task instructions. Stay within your role's responsibilities.
   - Save all deliverables to `output/{slug}/{category}/` named `YYYY-MM-DD-description.ext`
   - Update `output/{slug}/README.md` — add a row: `| path | what it contains | agent | date |`

6. **Write to memory**
   After completing, append a structured entry to your write category in `projects/{slug}/memory/decisions/{category}.md`:
   ```
   ## [{today's date}] {agent} — {task title}
   **Decision:** [the main decision or finding]
   **Reason:** [why this decision was made]
   **Impact:** [what downstream agents should know]
   ---
   ```

7. **Self-evaluate before finishing**
   Score your output 1–10 on completeness, accuracy, and usefulness. Append to your main output file:
   ```
   **Quality score: X/10** — [one sentence explanation]
   ```
   If your score is below 7: identify what is missing, fix it, then re-score. Do not finish until you reach 7 or above.

8. **Update project memory**
   Append a note to `projects/{slug}/memory/project_memory.json` under `agent_notes`.

9. **Move the task**
   Move the task file from `projects/{slug}/tasks/active/` to `projects/{slug}/tasks/completed/`.

---

## Upstream Output Rule

Every agent must list at the top of their completion doc which upstream output files they actually read. If a required upstream file does not exist yet, stop and leave a note in project memory — do not proceed with assumptions.

```
## Upstream outputs read
- output/{slug}/architecture/2026-04-11-system-architecture.md (bjorn)
- output/{slug}/compliance/2026-04-11-compliance-checklist.md (magnus)
```

---

## Phased Execution — Non-Negotiable Ordering Rules

**Phase 1 — runs first, in parallel:**
- bjorn (architecture)
- dag (infrastructure, Docker, CI/CD)
- magnus (compliance, GDPR, legal) — required whenever the project touches user data, auth, payments, or personal information

**Phase 2 — runs after Phase 1 is complete:**
- arve (implementation) — must reference bjorn's architecture output AND magnus's compliance output if magnus ran. Must implement any LAUNCH BLOCKER items from magnus in scope.
- ingrid, jorunn, else, halvard, frode, nora, guro — may run in parallel with arve if their inputs are ready

**Phase 3 — runs after Phase 2:**
- odd (API testing)
- per (performance benchmarking)

**Never run arve in parallel with magnus** on any project touching user data.

---

## Peer Review Assignments

After completing, selected agents are automatically reviewed by a peer:

| Agent | Reviewed by |
|-------|-------------|
| arve | odd |
| bjorn | arve |
| dag | arve |
| jorunn | ingrid |
| ingrid | jorunn |
| else | halvard |
| halvard | else |

Reviewers append a `## Peer Review` section to the main output file. Do not redo the work — only assess it.

---

## Web Search

The following agents have access to a `web_search` tool (powered by OpenAI) for live web search:
- else, halvard, guro, laila, knut, nora, frode, jorunn, magnus

Use it for current market data, competitor research, regulatory guidance, and anything that may have changed since training cutoff. Prefer real data over assumptions.

---

## Memory Categories

| Category | Written by | Read by |
|----------|-----------|---------|
| `architecture.md` | bjorn | arve, dag |
| `implementation.md` | arve, dag, odd, per | arve, dag, odd, per |
| `compliance.md` | magnus | arve |
| `brand.md` | ingrid, jorunn, guro | ingrid, jorunn, guro |
| `strategy.md` | else, halvard, nora, frode, knut, laila | all strategy agents |

On kickoff, `strategy.md` is automatically seeded with the project description.

---

## Notes

- Do not skip the memory read step — other agents may have left critical constraints
- Do not overwrite another agent's memory entries — only append
- All deliverables go in `output/{slug}/` — never scatter files across the repo root
- If you are unsure what to do, leave a note in project memory and stop
- Output files and project data are gitignored — do not commit runtime data
