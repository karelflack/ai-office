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

5. **Update memory after completing any task**
   - Append a note to `## Agent Notes` in `memory/team_memory.md`
   - Update the corresponding field in `memory/team_memory.json`
   - Move the task file to `tasks/completed/`

## Notes
- Do not skip the memory read step — other agents may have left important context
- Do not overwrite another agent's notes — only append
- If you are unsure what to do, leave a note in `## Agent Notes` and stop
