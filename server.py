#!/usr/bin/env python3
"""
AI Office HTTP server.
Serves static files from project root and provides a REST API under /api/.
Run with: python3 server.py
"""

import hashlib
import hmac
import http.server
import json
import os
import re
import secrets
import subprocess
import threading
import time
import urllib.request
import urllib.error
from pathlib import Path

# Load .env before anything else
_env_path = Path(__file__).parent / ".env"
if _env_path.exists():
    for _line in _env_path.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

from core import agents as agent_registry
from core import memory as mem
from core import tasks as task_mgr
from core import projects as project_mgr
from core import teams as team_mgr
from core import skills as skill_mgr
from core import tokens as token_tracker
from core.memory import update_project_memory as _update_project_memory
from integrations import n8n as _n8n
from integrations import github as _github
from integrations import linear as _linear
from integrations import notion as _notion

# Back-compat aliases for callers inside server.py — the integration bodies
# now live in integrations/*.py. Keep the old private names pointing at them
# so the rest of this file reads the same.
_notify_n8n            = _n8n.notify
_push_to_github        = _github.push
_linear_api            = _linear.api
_get_linear_state_id   = _linear.get_state_id
_linear_create_issues  = _linear.create_issues
_linear_update_issue   = _linear.update_issue
_linear_add_pr_comment = _linear.add_pr_comment
_write_to_notion       = _notion.write_summary
_init_tokens_db        = token_tracker.init_db
_read_claude_code_usage = token_tracker.read_claude_code_usage
_record_token_usage    = token_tracker.record_usage

PORT = 8000
BASE_DIR = Path(__file__).parent.resolve()
TOKENS_DB = token_tracker.TOKENS_DB

# Tracks live subprocess references keyed by (project_slug, filename).
_live_procs: dict = {}
_live_procs_lock = threading.Lock()
# Tracks retry counts keyed by (project_slug, filename).
_retry_counts: dict = {}
_retry_counts_lock = threading.Lock()
# In-memory session tokens — wiped on server restart (user re-logs in)
_sessions: set = set()
_sessions_lock = threading.Lock()
SESSION_COOKIE = "office_session"
# API paths that skip the session check. Webhooks are authed via HMAC; login
# is how sessions are issued in the first place.
_AUTH_EXEMPT_API = {"/api/login", "/api/logout", "/api/webhook/linear", "/api/webhook/jira"}

# Feature flags
_peer_review_enabled: bool = True
# Webhook handlers (still in this file) need their secrets at request time.
LINEAR_WEBHOOK_SECRET = os.environ.get("LINEAR_WEBHOOK_SECRET", "")
JIRA_WEBHOOK_SECRET   = os.environ.get("JIRA_WEBHOOK_SECRET", "")
WEBHOOK_TRIGGER_LABEL = os.environ.get("WEBHOOK_TRIGGER_LABEL", "ai-office")
# Per-project spend ceiling in USD. 0 disables the guard.
PROJECT_BUDGET_USD = float(os.environ.get("PROJECT_BUDGET_USD", "0") or 0)

# Project slug validation — URL-safe characters only. Blocks path traversal via
# ".." or "/" in any /api/projects/{slug}/... route.
_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,99}$")


def _valid_slug(slug: str) -> bool:
    return bool(_SLUG_RE.match(slug or ""))

# Reviewer assignments — who reviews whose output
REVIEWER_MAP = {
    "arve":    "odd",
    "bjorn":   "arve",
    "dag":     "arve",
    "jorunn":  "ingrid",
    "ingrid":  "jorunn",
    "else":    "halvard",
    "halvard": "else",
}

# Structured memory — which categories each agent reads and writes
AGENT_MEMORY = {
    "bjorn":   {"read": ["architecture"],                       "write": "architecture"},
    "arve":    {"read": ["architecture", "implementation"],     "write": "implementation"},
    "dag":     {"read": ["architecture", "implementation"],     "write": "implementation"},
    "magnus":  {"read": ["compliance"],                         "write": "compliance"},
    "ingrid":  {"read": ["brand", "strategy"],                  "write": "brand"},
    "jorunn":  {"read": ["brand", "strategy"],                  "write": "brand"},
    "guro":    {"read": ["brand", "strategy"],                  "write": "brand"},
    "else":    {"read": ["strategy"],                           "write": "strategy"},
    "halvard": {"read": ["strategy"],                           "write": "strategy"},
    "nora":    {"read": ["strategy"],                           "write": "strategy"},
    "frode":   {"read": ["strategy", "implementation"],         "write": "strategy"},
    "odd":     {"read": ["implementation"],                     "write": "implementation"},
    "per":     {"read": ["implementation"],                     "write": "implementation"},
    "knut":    {"read": ["strategy", "implementation"],         "write": "strategy"},
    "laila":   {"read": ["strategy"],                           "write": "strategy"},
}


# Agents that get web search via Perplexity MCP
WEB_SEARCH_AGENTS = {"else", "halvard", "guro", "laila", "knut", "nora", "frode", "jorunn", "magnus"}

MCP_SEARCH_CONFIG = BASE_DIR / "mcp_search.json"

# Maps agent → output subfolder
AGENT_OUTPUT_DIR = {
    "bjorn":    "architecture",
    "dag":      "architecture",
    "magnus":   "compliance",
    "arve":     "implementation",
    "odd":      "tests",
    "per":      "tests",
    "else":     "strategy",
    "halvard":  "strategy",
    "nora":     "strategy",
    "frode":    "strategy",
    "jorunn":   "brand",
    "ingrid":   "brand",
    "guro":     "brand",
    "laila":    "support",
    "knut":     "support",
    "orchestrator": "strategy",
}


def _parse_stream_event(line: str):
    try:
        event = json.loads(line)
    except Exception:
        return line if line.strip() else None
    t = event.get("type")
    if t == "assistant":
        for item in event.get("message", {}).get("content", []):
            if item.get("type") == "text" and item.get("text", "").strip():
                return item["text"].strip()
            elif item.get("type") == "tool_use":
                name = item.get("name", "")
                inp = item.get("input", {})
                if name == "Read":       return f"> Read: {inp.get('file_path', '')}"
                if name == "Write":      return f"> Write: {inp.get('file_path', '')}"
                if name == "Edit":       return f"> Edit: {inp.get('file_path', '')}"
                if name == "Bash":       return f"> $ {inp.get('command', '')[:80]}"
                if name == "Glob":       return f"> Glob: {inp.get('pattern', '')}"
                if name == "Grep":       return f"> Grep: {inp.get('pattern', '')}"
                if name == "web_search": return f"[OpenAI] web_search: {inp.get('query', '')[:80]}"
                return f"> {name}()"
    elif t == "result":
        cost = event.get("total_cost_usd", 0)
        if event.get("subtype") == "success":
            return f"✓ Done  (${cost:.4f})"
        else:
            return f"✗ Error: {event.get('result', '')}"
    return None


def _project_paused(slug: str) -> bool:
    """Return True if the project's memory has paused=True set."""
    mem_path = BASE_DIR / "projects" / slug / "memory" / "project_memory.json"
    if not mem_path.exists():
        return False
    try:
        data = json.loads(mem_path.read_text(encoding="utf-8"))
        return bool(data.get("paused"))
    except Exception:
        return False


def _enforce_budget(slug: str, filename: str) -> bool:
    """Gate a spawn on the project's spend.
    Returns True if the spawn may proceed. When the budget is first crossed,
    pauses the project and fires an n8n notification."""
    if _project_paused(slug):
        return False
    if PROJECT_BUDGET_USD <= 0:
        return True
    spent = token_tracker.project_total_usd(slug)
    if spent < PROJECT_BUDGET_USD:
        return True
    _update_project_memory(slug, {
        "paused": True,
        "paused_reason": f"Token budget ${PROJECT_BUDGET_USD:.2f} exceeded (spent ${spent:.2f})",
        "paused_at": int(time.time()),
    })
    _notify_n8n(slug, "system", filename,
                f"⚠ Budget ${PROJECT_BUDGET_USD:.2f} exceeded (spent ${spent:.2f}) — project paused")
    return False


def _spawn_agent_task(slug: str, filename: str, agent: str,
                      retry_count: int = 0, retry_context: str = "", **kwargs) -> bool:
    """Spawn a Claude subprocess for an active task. Returns False if already running,
    paused, or over budget."""
    key = (slug, filename)
    with _live_procs_lock:
        if key in _live_procs:
            return False
    if not _enforce_budget(slug, filename):
        return False

    # Read model and title from task file, fall back to sonnet
    from datetime import date as _date
    task_path = BASE_DIR / "projects" / slug / "tasks" / "active" / filename
    try:
        task_content = task_path.read_text(encoding="utf-8")
        model = task_mgr.parse_model(task_content) or "claude-sonnet-4-6"
        _title_match = re.search(r'^#\s+(.+)$', task_content, re.MULTILINE)
        task_title = _title_match.group(1).strip() if _title_match else filename
    except Exception:
        model = "claude-sonnet-4-6"
        task_title = filename
    today_str = _date.today().isoformat()

    output_subdir = AGENT_OUTPUT_DIR.get(agent, "strategy")
    output_path = f"output/{slug}/{output_subdir}"

    # Build memory read/write instructions
    mem_cfg = AGENT_MEMORY.get(agent, {})
    read_cats = mem_cfg.get("read", [])
    write_cat = mem_cfg.get("write", "strategy")
    mem_base = f"projects/{slug}/memory/decisions"

    if read_cats:
        read_list = "\n".join(
            f"   - {mem_base}/{cat}.md (if it exists)" for cat in read_cats
        )
        memory_read_step = (
            "2.5. Read project memory (context from previous agents):\n"
            f"{read_list}\n"
            "   These files contain decisions made by agents before you. Use them as context.\n"
        )
    else:
        memory_read_step = ""

    memory_write_step = (
        "8.5. Append your key decisions to project memory:\n"
        f"   File: {mem_base}/{write_cat}.md\n"
        "   Create it if it doesn't exist. Append (do NOT overwrite):\n"
        f"   ## [{today_str}] {agent} — {task_title}\n"
        "   **Decision:** [the main decision or finding]\n"
        "   **Reason:** [why this decision was made]\n"
        "   **Impact:** [what downstream agents should know]\n"
        "   ---\n"
    )

    retry_note = ""
    if retry_count > 0:
        retry_note = (
            f"\n\nRETRY #{retry_count}: Your previous attempt did not meet quality standards.\n"
            f"Issues identified: {retry_context}\n"
            "Fix these issues specifically before submitting.\n"
        )

    search_note = ""
    if agent in WEB_SEARCH_AGENTS and os.environ.get("OPENAI_API_KEY"):
        search_note = (
            "You have access to a web_search tool (Perplexity). "
            "Use it to find current information — market data, competitor research, "
            "pricing benchmarks, trends. Prefer real data over assumptions.\n\n"
        )

    prompt = (
        f"You are the {agent} agent in the ai-office multi-agent framework.\n\n"
        f"You are working on project: '{slug}'\n\n"
        f"{search_note}"
        "Steps to follow:\n"
        "1. Read CLAUDE.md for session protocol\n"
        f"2. Read agents/{agent}.md for your full role definition\n"
        f"{memory_read_step}"
        f"3. Read projects/{slug}/memory/project_memory.json for project context\n"
        f"4. Read the task file at projects/{slug}/tasks/active/{filename}\n"
        "5. Complete the task as described\n"
        f"6. Write all deliverables to {output_path}/ — name files clearly (YYYY-MM-DD-description.ext)\n"
        f"7. Update output/{slug}/README.md — add a row: | path/to/file | what it contains | {agent} | today's date |\n"
        f"8. Update projects/{slug}/memory/project_memory.json with your notes under agent_notes\n"
        f"{memory_write_step}"
        f"9. Move the task to projects/{slug}/tasks/completed/ and delete it from active/\n"
        "10. SELF-EVALUATION — before you finish:\n"
        "    a. Re-read the original task description\n"
        "    b. Review every deliverable you produced\n"
        "    c. Score your output 1-10 on completeness, accuracy, and usefulness\n"
        "    d. Append this exact line to your main output file:\n"
        "       **Quality score: X/10** — [one sentence explaining the score]\n"
        "    e. If your score is below 7: do NOT finish — identify what is missing, fix it, then re-score\n\n"
        f"{retry_note}"
        "Work autonomously. Use your tools. Produce real, useful output."
    )

    cmd = ["claude", "--print", "--dangerously-skip-permissions",
           "--verbose", "--output-format", "stream-json", "--model", model]
    use_mcp = (agent in WEB_SEARCH_AGENTS and MCP_SEARCH_CONFIG.exists()
               and os.environ.get("OPENAI_API_KEY") and not kwargs.get("skip_mcp"))
    if use_mcp:
        cmd += ["--mcp-config", str(MCP_SEARCH_CONFIG)]
    cmd += ["-p", prompt]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL, text=True, cwd=str(BASE_DIR),
    )
    with _live_procs_lock:
        _live_procs[key] = proc
    mem.write_run(filename, [], False, project_slug=slug)

    def _reader():
        lines = []
        succeeded = False
        eval_score = None
        eval_reason = ""
        try:
            for line in proc.stdout:
                line = line.rstrip("\n")
                if not line:
                    continue
                try:
                    formatted = _parse_stream_event(line)
                    if formatted:
                        lines.append(formatted)
                        mem.write_run(filename, lines, False, project_slug=slug)
                        # Parse quality score from agent output
                        m = re.search(r'\*\*Quality score:\s*(\d+)/10\*\*\s*[—\-]+\s*(.+)', formatted)
                        if m:
                            eval_score = int(m.group(1))
                            eval_reason = m.group(2).strip()
                    # Track success/failure and token usage from the result event
                    try:
                        event = json.loads(line)
                        if event.get("type") == "result":
                            succeeded = event.get("subtype") == "success"
                            usage = event.get("usage", {})
                            _record_token_usage(
                                project=slug,
                                agent=agent,
                                task=filename,
                                input_tokens=usage.get("input_tokens", 0),
                                output_tokens=usage.get("output_tokens", 0),
                                cache_read_tokens=usage.get("cache_read_input_tokens", 0),
                                cache_creation_tokens=usage.get("cache_creation_input_tokens", 0),
                                cost_usd=event.get("total_cost_usd", 0),
                            )
                    except Exception:
                        pass
                except Exception:
                    pass
        finally:
            exit_code = proc.wait()
            # A non-zero exit or an explicit error result means failure
            failed = (exit_code != 0) or (not succeeded and exit_code == 0 and any("✗ Error" in l for l in lines))
            mem.write_run(filename, lines, True, project_slug=slug)
            with _live_procs_lock:
                _live_procs.pop(key, None)

            if failed:
                # If MCP config caused the failure, retry without it
                mcp_error = any("Invalid MCP" in l or "ENAMETOOLONG" in l for l in lines)
                if mcp_error and use_mcp:
                    lines.append("⚠ MCP config failed — retrying without web search")
                    mem.write_run(filename, lines, False, project_slug=slug)
                    # Move back to active if needed
                    comp_path = BASE_DIR / "projects" / slug / "tasks" / "completed" / filename
                    active_path = BASE_DIR / "projects" / slug / "tasks" / "active" / filename
                    failed_path = BASE_DIR / "projects" / slug / "tasks" / "failed" / filename
                    for p in (comp_path, failed_path):
                        if p.exists():
                            active_path.parent.mkdir(parents=True, exist_ok=True)
                            p.rename(active_path)
                            break
                    _spawn_agent_task(slug, filename, agent,
                                      retry_count=retry_count,
                                      retry_context=retry_context,
                                      skip_mcp=True)
                    return
                # Trigger replan before cascading failure
                reason = lines[-1] if lines else f"Process exited with code {exit_code}"
                failure_context = f"Exit code {exit_code}. Reason: {reason}\n\n" + "\n".join(lines[-20:])
                with _retry_counts_lock:
                    _retry_counts.pop(key, None)
                _linear_update_issue(slug, filename, "Cancelled")
                _replan_task(slug, filename, agent, failure_context)
                return

            # Evaluation-based retry: if score < 7 and retries remaining, re-run
            if eval_score is not None and eval_score < 7:
                with _retry_counts_lock:
                    current_retries = _retry_counts.get(key, 0)
                if current_retries < 2:
                    with _retry_counts_lock:
                        _retry_counts[key] = current_retries + 1
                    msg = (f"⚡ Quality score {eval_score}/10 — retrying "
                           f"(attempt {current_retries + 2}/3): {eval_reason}")
                    lines.append(msg)
                    mem.write_run(filename, lines, False, project_slug=slug)
                    # Move task back to active if agent already completed it
                    comp_path = BASE_DIR / "projects" / slug / "tasks" / "completed" / filename
                    active_path = BASE_DIR / "projects" / slug / "tasks" / "active" / filename
                    if comp_path.exists() and not active_path.exists():
                        active_path.parent.mkdir(parents=True, exist_ok=True)
                        comp_path.rename(active_path)
                    _spawn_agent_task(slug, filename, agent,
                                      retry_count=current_retries + 1,
                                      retry_context=f"Score {eval_score}/10 — {eval_reason}")
                    return
                else:
                    lines.append(f"⚠ Score {eval_score}/10 after 3 attempts — triggering replan")
                    mem.write_run(filename, lines, True, project_slug=slug)
                    failure_context = f"Quality score {eval_score}/10 after 3 attempts.\nReason: {eval_reason}\n\n" + "\n".join(lines[-20:])
                    _replan_task(slug, filename, agent, failure_context)
                    return

            with _retry_counts_lock:
                _retry_counts.pop(key, None)
            _notify_n8n(slug, agent, filename, "completed")
            _linear_update_issue(slug, filename, "Done")

            # Check if this agent has a peer reviewer (and peer review is enabled).
            # If the project is bound to a team, only review when the reviewer
            # is also a team member — otherwise hard-restrict means no review.
            reviewer = REVIEWER_MAP.get(agent)
            if reviewer:
                _team = _team_for_project(slug)
                if _team is not None and reviewer not in team_mgr.all_agents_in_team(_team):
                    reviewer = None
            if reviewer and _peer_review_enabled:
                lines.append(f"👁 Sending to {reviewer} for peer review…")
                mem.write_run(filename, lines, False, project_slug=slug)
                _spawn_peer_review(slug, filename, agent, reviewer, lines)
            else:
                _dispatch_dependents(slug, filename)

    threading.Thread(target=_reader, daemon=True).start()
    return True


def _all_tasks_done(slug: str) -> bool:
    """Return True if backlog and active are both empty for this project."""
    dirs = task_mgr._get_task_dirs(slug)
    for bucket in ("backlog", "active"):
        d = dirs[bucket]
        if d.exists() and any(d.glob("*.md")):
            return False
    return True


def _snapshot_output(slug: str) -> None:
    """Copy current output/{slug}/ into output/{slug}/.runs/{timestamp}/ before a new run."""
    import shutil
    from datetime import datetime
    output_dir = BASE_DIR / "output" / slug
    if not output_dir.exists():
        return
    # Only snapshot if there are real output files (not just README)
    real_files = [
        f for f in output_dir.rglob("*")
        if f.is_file() and f.name != "README.md" and ".runs" not in f.parts
    ]
    if not real_files:
        return
    ts = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    snap_dir = output_dir / ".runs" / ts
    snap_dir.mkdir(parents=True, exist_ok=True)
    for f in real_files:
        rel = f.relative_to(output_dir)
        dest = snap_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dest)


def _agent_short_desc(agent_id: str) -> str:
    """Backwards-compat shim — delegates to core.agents.role()."""
    return agent_registry.role(agent_id) or "(custom agent)"


def _team_for_project(slug: str) -> dict | None:
    """Return the team dict bound to this project, or None if no team set."""
    pj = BASE_DIR / "projects" / slug / "project.json"
    try:
        team_slug = json.loads(pj.read_text(encoding="utf-8")).get("team")
    except Exception:
        return None
    if not team_slug:
        return None
    try:
        return team_mgr.get_team(team_slug)
    except FileNotFoundError:
        return None


def _build_kickoff_prompt(description: str, team: dict | None) -> str:
    """Build the orchestrator prompt — full 16 if no team, otherwise restricted
    to the team's phased agents. Custom agents are described by reading their
    .md. Phase ordering replaces the canon dependency rules when team is set."""
    if team is None:
        return f"""You are a project planner for an AI agent office. Your job is to assign every relevant agent a task.

Project: "{description}"

AGENTS (assign all that are relevant — do not leave agents idle if they have work to do):
- bjorn: system architecture, tech stack, data models, Mermaid diagrams
- arve: writing code, scaffolding projects, implementing features
- dag: DevOps, Docker, CI/CD pipelines, deployment config
- magnus: legal, compliance, GDPR, PCI, privacy policy
- ingrid: UI/UX design, wireframes, user flows, component specs
- else: research, market analysis, competitor landscape
- jorunn: brand identity, naming, tone of voice, visual guidelines
- halvard: growth strategy, acquisition channels, onboarding funnel
- frode: sprint planning, backlog breakdown, story points
- nora: pricing model, revenue streams, unit economics
- guro: social media content, launch copywriting, tweet threads
- knut: project milestones, timeline, progress tracking
- laila: customer support docs, onboarding guides, FAQs
- odd: API testing, endpoint validation, test suites
- per: performance benchmarking, load testing, optimization analysis

MANDATORY INCLUSIONS:
- Software projects MUST include: bjorn, arve, dag, odd, per
- Projects with user data / payments MUST include: magnus
- Products going to market MUST include: jorunn, halvard, guro, nora, laila
- Projects with a roadmap MUST include: frode, knut
- Projects researching a market MUST include: else

DEPENDENCY RULES (use exact task title in depends_on field):
- arve depends on bjorn's architecture task
- dag depends on bjorn's architecture task
- odd depends on arve's implementation task
- per depends on arve's implementation task
- nora depends on else's research task (if else runs)
- jorunn, halvard, guro may depend on else's research (if relevant)
- All other tasks: depends_on = null (run immediately in parallel)

MODEL ASSIGNMENT:
- "claude-sonnet-4-6": coding, architecture, system design, compliance, security, DevOps
- "claude-haiku-4-5-20251001": research, writing, branding, social media, sprint planning, docs, pricing, milestones

TASK DESCRIPTIONS must be specific: exactly what to produce, what format, what decisions to make, what to reference from other agents.

Reply with ONLY a JSON array — no markdown, no explanation, no code fences:
[{{"agent":"bjorn","title":"System Architecture","description":"...","depends_on":null,"model":"claude-sonnet-4-6"}},{{"agent":"arve","title":"Backend Implementation","description":"...","depends_on":"System Architecture","model":"claude-sonnet-4-6"}}]"""

    # Team-scoped: a fixed canon skeleton (orchestrator + bjorn/arve/odd) plus
    # a flat list of deputies. The orchestrator decides which canon agents and
    # deputies fire and which phase each fires in — no fixed phase per deputy.
    deputy_lines = []
    for d in team_mgr.deputies_in_team(team):
        deputy_lines.append(f"- {d}: {_agent_short_desc(d)}")
    deputies_block = "\n".join(deputy_lines) if deputy_lines else "(no deputies — only the canon team is available)"
    team_name = team.get("name") or team.get("slug")

    return f"""You are a project planner for an AI agent office. Your job is to assign each relevant agent a task. Skip agents the project does not need.

Project: "{description}"

TEAM: "{team_name}".

CANON (fixed skeleton, always available — fire only when the project needs them):
- bjorn  (Phase 1 — foundation): {_agent_short_desc('bjorn')}
- arve   (Phase 2 — build):      {_agent_short_desc('arve')}
- odd    (Phase 3 — verify):     {_agent_short_desc('odd')}

DEPUTIES (specialists for this team — you decide which fire and which phase each fits in):
{deputies_block}

PHASE MEANING:
- Phase 1 — foundation, planning, research, requirements. No prerequisites.
- Phase 2 — building deliverables. Depends on Phase 1 outputs.
- Phase 3 — verification, testing, validation. Depends on Phase 2 outputs.

Place each deputy you assign into the phase that makes sense for THIS project. The same deputy can land in different phases on different projects.

DEPENDENCY RULES — strict:
- Phase 1 tasks: depends_on = null
- Phase 2 tasks: depends_on = exact title of a Phase 1 task (or null only if no Phase 1 task exists)
- Phase 3 tasks: depends_on = exact title of a Phase 2 task (or null only if no Phase 2 task exists)

OUTPUT FORMAT — every task object MUST include "phase" (1, 2, or 3):

MODEL ASSIGNMENT:
- "claude-sonnet-4-6": coding, architecture, system design, compliance, security, DevOps
- "claude-haiku-4-5-20251001": research, writing, branding, social media, sprint planning, docs, pricing, milestones

TASK DESCRIPTIONS must be specific: exactly what to produce, what format, what decisions to make, what to reference from other agents.

Reply with ONLY a JSON array — no markdown, no explanation, no code fences:
[{{"agent":"bjorn","phase":1,"title":"System Architecture","description":"...","depends_on":null,"model":"claude-sonnet-4-6"}},{{"agent":"jorunn","phase":2,"title":"Brand Guidelines","description":"...","depends_on":"System Architecture","model":"claude-haiku-4-5-20251001"}}]"""


def _do_kickoff(slug: str, description: str) -> tuple:
    """Run orchestrator to plan tasks for a project. Returns (created_list, error_str)."""
    team = _team_for_project(slug)
    prompt = _build_kickoff_prompt(description, team)

    try:
        proc = subprocess.run(
            ["claude", "--print", "--dangerously-skip-permissions",
             "--output-format", "json", prompt],
            capture_output=True, text=True,
            cwd=str(BASE_DIR), timeout=300,
        )
    except subprocess.TimeoutExpired:
        return None, "Planning timed out"
    except FileNotFoundError:
        return None, "claude CLI not found"

    try:
        outer = json.loads(proc.stdout)
        text = outer.get("result", "")
    except (json.JSONDecodeError, AttributeError):
        text = proc.stdout

    match = re.search(r'\[[\s\S]*\]', text)
    if not match:
        return None, "Could not parse plan from orchestrator"

    try:
        plan = json.loads(match.group())
    except json.JSONDecodeError:
        return None, "Orchestrator returned malformed plan"

    # Hard-restrict: when a team is set, drop any task assigned to an agent
    # not in the team (canon + deputies). The team is a whitelist.
    team_member_ids = set(team_mgr.all_agents_in_team(team)) if team else None

    # First pass: validate + collect with phase info so we can patch missing
    # depends_on after we know which titles belong to which phase.
    parsed = []
    for item in plan:
        agent = str(item.get("agent", "orchestrator")).strip().lower()
        title = str(item.get("title", "Untitled")).strip()
        desc  = str(item.get("description", "")).strip()
        raw_dep = item.get("depends_on")
        model = str(item.get("model", "claude-sonnet-4-6")).strip() or "claude-sonnet-4-6"
        try:
            phase = int(item.get("phase") or 0) or None
        except (TypeError, ValueError):
            phase = None
        if not agent_registry.is_valid(agent):
            agent = "orchestrator"
        if team_member_ids is not None and agent not in team_member_ids:
            continue  # off-team — drop
        # Canon agents have a known phase if the orchestrator forgot to set one.
        if not phase and agent in team_mgr.CANON_PHASE:
            phase = int(team_mgr.CANON_PHASE[agent])
        parsed.append({"agent": agent, "title": title, "desc": desc,
                       "raw_dep": raw_dep, "model": model, "phase": phase})

    # Phase-ordering safety net (only when a team is set): a Phase 2 task whose
    # depends_on doesn't point at a Phase 1 title gets force-attached to one;
    # same for Phase 3 → Phase 2. The orchestrator can slip on this field, and
    # without enforcement the task would auto-start in the wrong order.
    if team is not None:
        title_phase = {p["title"]: p["phase"] for p in parsed if p["phase"]}
        phase1_titles = [p["title"] for p in parsed if p["phase"] == 1]
        phase2_titles = [p["title"] for p in parsed if p["phase"] == 2]
        for p in parsed:
            if p["phase"] == 2:
                dep_phase = title_phase.get(p["raw_dep"]) if p["raw_dep"] else None
                if dep_phase != 1 and phase1_titles:
                    p["raw_dep"] = phase1_titles[0]
            elif p["phase"] == 3:
                dep_phase = title_phase.get(p["raw_dep"]) if p["raw_dep"] else None
                if dep_phase != 2:
                    p["raw_dep"] = phase2_titles[0] if phase2_titles else (phase1_titles[0] if phase1_titles else None)

    created = []
    title_to_filename: dict = {}
    for p in parsed:
        depends_on = title_to_filename.get(p["raw_dep"]) if p["raw_dep"] else None
        filename = task_mgr.create_task(p["title"], p["agent"], p["desc"],
                                        project_slug=slug, depends_on=depends_on, model=p["model"])
        title_to_filename[p["title"]] = filename
        created.append({"filename": filename, "agent": p["agent"], "title": p["title"],
                        "description": p["desc"], "depends_on": depends_on})

    _update_project_memory(slug, {
        "kickoff_description": description,
        "kickoff_plan": [{"agent": t["agent"], "title": t["title"]} for t in created],
    })

    from datetime import date as _date
    decisions_dir = BASE_DIR / "projects" / slug / "memory" / "decisions"
    decisions_dir.mkdir(parents=True, exist_ok=True)
    strategy_seed = decisions_dir / "strategy.md"
    today_str = _date.today().isoformat()
    seed_content = (
        f"# Project Memory — {slug}\n\n"
        f"## [{today_str}] kickoff — Project Brief\n"
        f"**Decision:** {description}\n"
        "**Reason:** Initial project kickoff — this is the primary brief\n"
        "**Impact:** All agents should read this to understand what we are building\n"
        "---\n"
    )
    if not strategy_seed.exists():
        strategy_seed.write_text(seed_content, encoding="utf-8")
    else:
        existing = strategy_seed.read_text(encoding="utf-8")
        strategy_seed.write_text(existing + "\n" + seed_content, encoding="utf-8")

    _linear_create_issues(slug, created)
    return created, None


def _run_webhook_project(name: str, description: str):
    """Background: create project, run kickoff, auto-start Phase 1 tasks."""
    try:
        slug = project_mgr.create_project(name, description)
    except ValueError:
        slug = project_mgr.create_project(f"{name}-{int(time.time())}", description)

    created, err = _do_kickoff(slug, description)
    if err or not created:
        return

    backlog_dir = BASE_DIR / "projects" / slug / "tasks" / "backlog"
    for task_file in sorted(backlog_dir.glob("*.md")):
        try:
            content = task_file.read_text(encoding="utf-8")
            dep = task_mgr.parse_depends_on(content)
            if dep:
                continue
            m = re.search(r'^\*\*Agent:\*\*\s*(.+)$', content, re.MULTILINE)
            agent = m.group(1).strip() if m else "orchestrator"
            if not agent_registry.is_valid(agent):
                agent = "orchestrator"
            task_mgr.assign_task(task_file.name, agent, project_slug=slug)
            _spawn_agent_task(slug, task_file.name, agent)
        except Exception:
            pass


def _find_docker_compose(slug: str) -> Path | None:
    """Find a docker-compose.yml anywhere in output/{slug}/."""
    output_dir = BASE_DIR / "output" / slug
    for p in output_dir.rglob("docker-compose.yml"):
        return p
    return None


def _verify_docker_build(slug: str, attempt: int = 0):
    """Try to build and boot the project with Docker. Runs in a background thread."""
    compose_file = _find_docker_compose(slug)
    if not compose_file:
        return  # No docker-compose — nothing to verify

    compose_dir = compose_file.parent
    max_attempts = 2

    def _run():
        _notify_n8n(slug, "system", f"docker-verify-attempt-{attempt+1}.md",
                    f"Docker build started (attempt {attempt+1}/{max_attempts+1})")

        # Tear down any previous run first
        subprocess.run(
            ["docker", "compose", "-f", str(compose_file), "down", "--remove-orphans", "--volumes"],
            cwd=str(compose_dir), capture_output=True, timeout=60,
        )

        # Build and start
        build_result = subprocess.run(
            ["docker", "compose", "-f", str(compose_file), "up", "--build", "-d"],
            cwd=str(compose_dir), capture_output=True, text=True, timeout=300,
        )

        if build_result.returncode != 0:
            # Build failed — grab last 20 lines of stderr
            error_lines = (build_result.stderr or build_result.stdout or "").splitlines()
            error_summary = "\n".join(error_lines[-20:])
            _handle_docker_failure(slug, compose_file, error_summary, attempt, max_attempts)
            return

        # Wait for healthchecks (up to 90s)
        healthy = False
        for _ in range(18):
            time.sleep(5)
            ps = subprocess.run(
                ["docker", "compose", "-f", str(compose_file), "ps", "--format", "json"],
                cwd=str(compose_dir), capture_output=True, text=True,
            )
            output = ps.stdout.strip()
            if output and '"health"' in output:
                try:
                    services = json.loads(f"[{output}]") if not output.startswith("[") else json.loads(output)
                    if all(s.get("Health", "") in ("healthy", "") for s in services):
                        healthy = True
                        break
                except Exception:
                    pass
            elif ps.returncode == 0 and output:
                healthy = True
                break

        if healthy:
            _notify_n8n(slug, "system", "docker-verify-passed.md", "Docker build passed")
            # Clean up
            subprocess.run(
                ["docker", "compose", "-f", str(compose_file), "down", "--remove-orphans", "--volumes"],
                cwd=str(compose_dir), capture_output=True, timeout=60,
            )
        else:
            # Get last 20 lines of logs from failed services
            logs = subprocess.run(
                ["docker", "compose", "-f", str(compose_file), "logs", "--tail", "20"],
                cwd=str(compose_dir), capture_output=True, text=True, timeout=30,
            )
            error_summary = "\n".join(logs.stdout.splitlines()[-20:])
            subprocess.run(
                ["docker", "compose", "-f", str(compose_file), "down", "--remove-orphans", "--volumes"],
                cwd=str(compose_dir), capture_output=True, timeout=60,
            )
            _handle_docker_failure(slug, compose_file, error_summary, attempt, max_attempts)

    threading.Thread(target=_run, daemon=True).start()


def _handle_docker_failure(slug: str, compose_file: Path, error_summary: str,
                            attempt: int, max_attempts: int):
    """Send error to Arve for fixing, then re-verify. Give up after max_attempts."""
    if attempt >= max_attempts:
        _notify_n8n(slug, "system", "docker-verify-failed.md",
                    f"Docker build failed after {max_attempts+1} attempts — needs manual review")
        return

    _notify_n8n(slug, "system", f"docker-verify-attempt-{attempt+1}.md",
                "Docker build failed — sending to Arve for fix")

    # Create a repair task for Arve
    fix_title = f"Fix Docker build error (attempt {attempt+1})"
    description = (
        f"The Docker build for this project failed. Fix the code so it builds and boots.\n\n"
        f"## Error (last 20 lines)\n\n```\n{error_summary}\n```\n\n"
        f"Focus on the error above. Do not rewrite working code."
    )
    fix_filename = task_mgr.create_task(fix_title, "arve", description=description, project_slug=slug)
    task_mgr.assign_task(fix_filename, "arve", project_slug=slug)
    _spawn_agent_task(slug, fix_filename, "arve",
                      retry_context=f"Docker fix attempt {attempt+1}")

    # After Arve finishes this fix task, _dispatch_dependents will check _all_tasks_done
    # and trigger _verify_docker_build again — but we need to pass the next attempt count.
    # Store it so _dispatch_dependents knows to re-verify.
    _docker_verify_attempts[slug] = attempt + 1


_docker_verify_attempts: dict = {}
_ci_test_attempts: dict = {}
_replan_attempts: dict = {}  # (slug, filename) -> attempt count


def _replan_task(slug: str, filename: str, agent: str, failure_context: str):
    """Call orchestrator to replan a failed task. Max 1 replan per task."""
    key = (slug, filename)
    with _retry_counts_lock:
        if _replan_attempts.get(key, 0) >= 1:
            # Already replanned once — accept failure
            task_mgr.fail_task(filename, reason="Failed after replan", project_slug=slug)
            task_mgr.cascade_fail(filename, project_slug=slug)
            _notify_n8n(slug, agent, filename, "failed — gave up after replan")
            return
        _replan_attempts[key] = 1

    # Read task content
    task_content = ""
    for bucket in ("active", "failed", "backlog", "completed"):
        p = BASE_DIR / "projects" / slug / "tasks" / bucket / filename
        if p.exists():
            try:
                task_content = p.read_text(encoding="utf-8")
            except Exception:
                pass
            break

    # Read project strategy for context
    strategy = ""
    try:
        sp = BASE_DIR / "projects" / slug / "memory" / "decisions" / "strategy.md"
        if sp.exists():
            strategy = sp.read_text(encoding="utf-8")[:1500]
    except Exception:
        pass

    prompt = f"""You are the orchestrator for an AI agent office. A task has failed after multiple retries and needs replanning.

Project: {slug}

Failed task:
{task_content[:2000]}

Failure context:
{failure_context[:1500]}

Project brief:
{strategy}

Available agents: bjorn, arve, dag, else, frode, nora, magnus, ingrid, jorunn, halvard, knut, laila, odd, per

Choose the best recovery. Reply with ONLY a JSON object, no markdown:

Rewrite (same agent, clearer instructions):
{{"action":"rewrite","agent":"{agent}","title":"...","description":"...","model":"claude-sonnet-4-6"}}

Split into smaller tasks (sequential):
{{"action":"split","tasks":[{{"agent":"...","title":"...","description":"...","model":"claude-sonnet-4-6"}}]}}

Reroute to a better-suited agent:
{{"action":"reroute","agent":"...","title":"...","description":"...","model":"claude-sonnet-4-6"}}

Add a missing prerequisite first:
{{"action":"prerequisite","pre":{{"agent":"...","title":"...","description":"...","model":"claude-sonnet-4-6"}},"then":{{"agent":"{agent}","title":"...","description":"...","model":"claude-sonnet-4-6"}}}}

Accept failure (task is out of scope or impossible):
{{"action":"accept"}}"""

    def _run():
        _notify_n8n(slug, "orchestrator", filename, "replanning")
        try:
            proc = subprocess.run(
                ["claude", "--print", "--dangerously-skip-permissions",
                 "--output-format", "json", prompt],
                capture_output=True, text=True, cwd=str(BASE_DIR), timeout=90,
            )
            try:
                text = json.loads(proc.stdout).get("result", "")
            except (json.JSONDecodeError, AttributeError):
                text = proc.stdout

            # Strip markdown code fences before searching for JSON
            text = re.sub(r'```(?:json)?\s*', '', text).strip()

            plan = None
            for match in re.finditer(r'\{[\s\S]*?\}(?=\s*$|\s*\n)', text) or []:
                try:
                    plan = json.loads(match.group())
                    break
                except json.JSONDecodeError:
                    continue
            if plan is None:
                # Fallback: grab everything between first { and last }
                start, end = text.find('{'), text.rfind('}')
                if start != -1 and end > start:
                    try:
                        plan = json.loads(text[start:end + 1])
                    except json.JSONDecodeError:
                        pass
            if plan is None:
                task_mgr.fail_task(filename, reason="Replan parse failed", project_slug=slug)
                task_mgr.cascade_fail(filename, project_slug=slug)
                return
            action = plan.get("action", "accept")
            _notify_n8n(slug, "orchestrator", filename, f"replan → {action}")

            # Remove the original failed task file
            def _remove_original():
                for bucket in ("active", "failed", "backlog", "completed"):
                    p = BASE_DIR / "projects" / slug / "tasks" / bucket / filename
                    if p.exists():
                        p.unlink()

            if action == "accept":
                task_mgr.fail_task(filename, reason="Accepted failure after replan", project_slug=slug)
                task_mgr.cascade_fail(filename, project_slug=slug)

            elif action in ("rewrite", "reroute"):
                new_agent = plan.get("agent", agent)
                new_fn = task_mgr.create_task(
                    plan.get("title", "Replanned task"), new_agent,
                    plan.get("description", ""), project_slug=slug,
                    model=plan.get("model", "claude-sonnet-4-6"),
                )
                _remove_original()
                task_mgr.assign_task(new_fn, new_agent, project_slug=slug)
                _spawn_agent_task(slug, new_fn, new_agent, retry_context=f"Replan: {action}")

            elif action == "split":
                tasks = plan.get("tasks", [])
                if not tasks:
                    task_mgr.fail_task(filename, reason="Replan split had no tasks", project_slug=slug)
                    return
                _remove_original()
                prev_fn = None
                first_fn, first_agent = None, None
                for t in tasks:
                    t_agent = t.get("agent", agent)
                    new_fn = task_mgr.create_task(
                        t.get("title", "Split task"), t_agent,
                        t.get("description", ""), project_slug=slug,
                        depends_on=prev_fn, model=t.get("model", "claude-sonnet-4-6"),
                    )
                    if first_fn is None:
                        first_fn, first_agent = new_fn, t_agent
                    prev_fn = new_fn
                task_mgr.assign_task(first_fn, first_agent, project_slug=slug)
                _spawn_agent_task(slug, first_fn, first_agent, retry_context="Replan: split")

            elif action == "prerequisite":
                pre  = plan.get("pre",  {})
                then = plan.get("then", {})
                _remove_original()
                pre_agent = pre.get("agent", agent)
                pre_fn = task_mgr.create_task(
                    pre.get("title", "Prerequisite"), pre_agent,
                    pre.get("description", ""), project_slug=slug,
                    model=pre.get("model", "claude-sonnet-4-6"),
                )
                task_mgr.create_task(
                    then.get("title", "Main task"), then.get("agent", agent),
                    then.get("description", ""), project_slug=slug,
                    depends_on=pre_fn, model=then.get("model", "claude-sonnet-4-6"),
                )
                task_mgr.assign_task(pre_fn, pre_agent, project_slug=slug)
                _spawn_agent_task(slug, pre_fn, pre_agent, retry_context="Replan: prerequisite")

        except Exception:
            task_mgr.fail_task(filename, reason="Replan error", project_slug=slug)
            task_mgr.cascade_fail(filename, project_slug=slug)

    threading.Thread(target=_run, daemon=True).start()


def _detect_test_command(output_dir: Path) -> tuple:
    """Return (command_list, cwd) for the first test suite found, or (None, None)."""
    for root, dirs, files in os.walk(str(output_dir)):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "__pycache__", ".venv")]
        root_path = Path(root)
        filenames = set(files)

        if any(f.startswith("test_") and f.endswith(".py") for f in filenames) or \
           any(f.endswith("_test.py") for f in filenames) or \
           "pytest.ini" in filenames or "setup.cfg" in filenames:
            return (["python3", "-m", "pytest", "--tb=long", "-v"], root_path)

        if "package.json" in filenames:
            try:
                pkg = json.loads((root_path / "package.json").read_text(encoding="utf-8"))
                if "test" in pkg.get("scripts", {}):
                    return (["npm", "test", "--", "--watchAll=false", "--passWithNoTests"], root_path)
            except Exception:
                pass

    return None, None


def _after_ci_pass(slug: str):
    """Run Docker verify + GitHub push + Notion write after CI passes (or is skipped)."""
    attempt = _docker_verify_attempts.get(slug, 0)
    _docker_verify_attempts[slug] = attempt
    _verify_docker_build(slug, attempt=attempt)
    _push_to_github(slug)
    _linear_add_pr_comment(slug)
    threading.Thread(target=_write_to_notion, args=(slug,), daemon=True).start()


def _parse_test_failures(error_output: str, test_cwd: Path) -> str:
    """
    Turn raw pytest/npm output into a structured brief for arve.
    Extracts failing test names, assertion details, and reads the test source
    for each failing test so arve knows exactly what to fix.
    """
    lines = error_output.splitlines()

    # --- pytest: extract FAILED lines ---
    # Format: "FAILED path/test_file.py::TestClass::test_name - AssertionError: ..."
    failed_entries = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("FAILED "):
            failed_entries.append(stripped[7:].strip())

    # --- npm/jest: extract failing test names ---
    if not failed_entries:
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("✕ ") or stripped.startswith("× ") or stripped.startswith("FAIL "):
                failed_entries.append(stripped.lstrip("✕×").strip())

    if not failed_entries:
        # No structured failures found — return full output, middle-first
        # (pytest puts assertion details in the middle, summary at end)
        mid = max(0, len(error_output) // 2 - 1500)
        return error_output[mid:mid + 3000] if len(error_output) > 3000 else error_output

    # Build per-test sections
    sections = []
    seen_files: set = set()

    for entry in failed_entries[:10]:  # cap at 10
        parts = entry.split(" - ", 1)
        test_id = parts[0].strip()
        reason = parts[1].strip() if len(parts) > 1 else ""

        section = f"### `{test_id}`\n"
        if reason:
            section += f"**Error:** {reason}\n\n"

        # Read test file source for failing tests
        if "::" in test_id:
            file_part = test_id.split("::")[0]
            test_file = test_cwd / file_part
            if test_file.exists() and str(test_file) not in seen_files:
                seen_files.add(str(test_file))
                try:
                    src = test_file.read_text(encoding="utf-8")
                    section += f"**Test source** (`{file_part}`):\n```python\n{src[:2500]}\n```\n"
                except Exception:
                    pass

        sections.append(section)

    # Extract detailed assertion blocks from pytest output
    # pytest wraps each test's detail in "_ test_name _" underlines
    detail_blocks: list = []
    current_block: list = []
    in_block = False
    for line in lines:
        if line.startswith("_ ") and line.endswith(" _"):
            if current_block:
                detail_blocks.append("\n".join(current_block))
            current_block = [line]
            in_block = True
        elif in_block:
            if line.startswith("="):
                detail_blocks.append("\n".join(current_block))
                current_block = []
                in_block = False
            else:
                current_block.append(line)
    if current_block:
        detail_blocks.append("\n".join(current_block))

    result = f"## {len(failed_entries)} failing test(s)\n\n"
    result += "\n".join(sections) + "\n"

    if detail_blocks:
        combined = "\n\n".join(detail_blocks[:10])
        result += f"\n## Assertion details\n```\n{combined[:3000]}\n```\n"
    else:
        result += f"\n## Full test output\n```\n{error_output[:3000]}\n```\n"

    return result


def _handle_ci_failure(slug: str, error_output: str, attempt: int, max_attempts: int,
                       test_cwd: Path = None):
    """Send test failure to Arve. Give up and proceed after max_attempts."""
    if attempt >= max_attempts:
        _notify_n8n(slug, "system", "ci-tests-failed.md",
                    f"CI tests failed after {max_attempts + 1} attempts — proceeding to GitHub")
        _after_ci_pass(slug)
        return

    _notify_n8n(slug, "system", f"ci-fix-attempt-{attempt + 1}.md",
                "CI tests failed — sending to Arve for fix")

    structured = _parse_test_failures(error_output, test_cwd or Path("."))
    fix_title = f"Fix failing tests (attempt {attempt + 1})"
    description = (
        f"The automated test suite is failing. Fix the implementation so all tests pass.\n\n"
        f"{structured}\n\n"
        f"Rules:\n"
        f"- Fix the implementation code, not the tests\n"
        f"- Do not delete or weaken any assertions\n"
        f"- Run the tests mentally against your fix before finishing\n"
    )
    fix_filename = task_mgr.create_task(fix_title, "arve", description=description, project_slug=slug)
    task_mgr.assign_task(fix_filename, "arve", project_slug=slug)
    _ci_test_attempts[slug] = attempt + 1
    _spawn_agent_task(slug, fix_filename, "arve", retry_context=f"CI fix attempt {attempt + 1}")


def _run_ci_tests(slug: str, attempt: int = 0):
    """Detect and run tests in output/{slug}/. Background thread."""
    def _run():
        output_dir = BASE_DIR / "output" / slug
        test_cmd, test_cwd = _detect_test_command(output_dir)

        if not test_cmd:
            _after_ci_pass(slug)
            return

        _notify_n8n(slug, "system", "ci-tests-started.md",
                    f"Running CI: {' '.join(test_cmd)}")
        try:
            result = subprocess.run(
                test_cmd, cwd=str(test_cwd),
                capture_output=True, text=True, timeout=300,
            )
        except subprocess.TimeoutExpired:
            _handle_ci_failure(slug, "Test run timed out after 5 minutes", attempt, 2)
            return
        except Exception as e:
            _handle_ci_failure(slug, str(e), attempt, 2)
            return

        if result.returncode == 0:
            _notify_n8n(slug, "system", "ci-tests-passed.md", "CI tests passed")
            _after_ci_pass(slug)
        else:
            error_output = (result.stdout + "\n" + result.stderr).strip()
            _handle_ci_failure(slug, error_output, attempt, 2, test_cwd=test_cwd)

    threading.Thread(target=_run, daemon=True).start()


def _dispatch_dependents(slug: str, filename: str):
    """Activate and spawn tasks that were waiting on filename."""
    newly_activated = task_mgr.resolve_handoffs(filename, project_slug=slug)
    to_run = set(newly_activated)
    active_dir = BASE_DIR / "projects" / slug / "tasks" / "active"
    if active_dir.exists():
        for f in active_dir.glob("*.md"):
            try:
                content = f.read_text(encoding="utf-8")
                dep = task_mgr.parse_depends_on(content)
                if dep and dep == filename:
                    to_run.add(f.name)
            except Exception:
                pass
    for dep_filename in to_run:
        dep_path = active_dir / dep_filename
        dep_content = dep_path.read_text(encoding="utf-8") if dep_path.exists() else ""
        m = re.search(r'^\*\*Agent:\*\*\s*(.+)$', dep_content, re.MULTILINE)
        dep_agent = m.group(1).strip() if m else "orchestrator"
        if not agent_registry.is_valid(dep_agent):
            dep_agent = "orchestrator"
        _spawn_agent_task(slug, dep_filename, dep_agent)

    # If no more tasks remain, run CI tests → Docker → GitHub
    if not to_run and _all_tasks_done(slug):
        attempt = _ci_test_attempts.get(slug, 0)
        _run_ci_tests(slug, attempt=attempt)


def _spawn_peer_review(slug: str, filename: str, original_agent: str,
                       reviewer: str, parent_lines: list):
    """Spawn a reviewer subprocess. On approval dispatch dependents; on revision re-run original."""
    if not _enforce_budget(slug, filename):
        return
    output_subdir = AGENT_OUTPUT_DIR.get(original_agent, "strategy")
    output_path = f"output/{slug}/{output_subdir}"

    prompt = (
        f"You are {reviewer}, the peer reviewer in the ai-office framework.\n\n"
        f"You are reviewing work produced by {original_agent} on project '{slug}'.\n\n"
        f"Task file:       projects/{slug}/tasks/completed/{filename}\n"
        f"Output folder:   {output_path}/\n\n"
        "Your job:\n"
        "1. Read the completed task file to understand what was asked\n"
        "2. Read the output files produced for this task\n"
        "3. Evaluate: does the output fully satisfy the task description?\n"
        "4. Append your review to the MAIN output file using exactly this format:\n\n"
        "   ## Peer Review\n"
        f"   **Reviewer:** {reviewer}\n"
        "   **Status:** Approved\n"
        "   **Score:** X/10\n"
        "   [2-4 sentences: what was done well, what (if anything) is missing]\n\n"
        "   OR if the work needs fixing:\n\n"
        "   ## Peer Review\n"
        f"   **Reviewer:** {reviewer}\n"
        "   **Status:** Revision Requested\n"
        "   **Score:** X/10\n"
        "   [Specific issues: list exactly what must be fixed]\n\n"
        "Rules:\n"
        "- Do NOT redo the work yourself\n"
        "- Only append the review section — do not modify other content\n"
        "- Be specific: vague feedback is useless\n"
        "- Approve if the work is solid even if imperfect (score ≥ 7)\n"
        "- Request revision only for genuinely incomplete or incorrect work\n"
    )

    proc = subprocess.Popen(
        ["claude", "--print", "--dangerously-skip-permissions",
         "--verbose", "--output-format", "stream-json",
         "--model", "claude-sonnet-4-6", prompt],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL, text=True, cwd=str(BASE_DIR),
    )

    def _review_reader():
        review_lines = list(parent_lines)
        approved = True
        revision_notes = ""
        try:
            for line in proc.stdout:
                line = line.rstrip("\n")
                if not line:
                    continue
                try:
                    formatted = _parse_stream_event(line)
                    if formatted:
                        review_lines.append(f"[{reviewer}] {formatted}")
                        mem.write_run(filename, review_lines, False, project_slug=slug)
                        if "Revision Requested" in formatted:
                            approved = False
                        if not approved and len(formatted) > 20:
                            revision_notes += " " + formatted
                    try:
                        event = json.loads(line)
                        if event.get("type") == "result":
                            usage = event.get("usage", {})
                            _record_token_usage(
                                project=slug, agent=reviewer, task=f"review:{filename}",
                                input_tokens=usage.get("input_tokens", 0),
                                output_tokens=usage.get("output_tokens", 0),
                                cache_read_tokens=usage.get("cache_read_input_tokens", 0),
                                cache_creation_tokens=usage.get("cache_creation_input_tokens", 0),
                                cost_usd=event.get("total_cost_usd", 0),
                            )
                    except Exception:
                        pass
                except Exception:
                    pass
        finally:
            proc.wait()
            if approved:
                review_lines.append(f"✓ Peer review passed ({reviewer})")
                mem.write_run(filename, review_lines, True, project_slug=slug)
                _dispatch_dependents(slug, filename)
            else:
                review_lines.append(f"↺ Revision requested by {reviewer} — re-running {original_agent}")
                mem.write_run(filename, review_lines, False, project_slug=slug)
                # Move task back to active for revision
                comp_path = BASE_DIR / "projects" / slug / "tasks" / "completed" / filename
                active_path = BASE_DIR / "projects" / slug / "tasks" / "active" / filename
                if comp_path.exists() and not active_path.exists():
                    active_path.parent.mkdir(parents=True, exist_ok=True)
                    comp_path.rename(active_path)
                _spawn_agent_task(slug, filename, original_agent,
                                  retry_count=1,
                                  retry_context=f"Peer review by {reviewer}: {revision_notes.strip()}")

    threading.Thread(target=_review_reader, daemon=True).start()


class AIOfficeHandler(http.server.SimpleHTTPRequestHandler):

    def translate_path(self, path):
        import urllib.parse
        path = urllib.parse.unquote(path)
        path = path.split("?", 1)[0].split("#", 1)[0]
        path = os.path.normpath(path)
        return str(BASE_DIR / path.lstrip("/"))

    def end_headers(self):
        # Disable caching for HTML so dashboard edits show up on next reload
        # without users having to hard-refresh. Static assets (PNG, SVG, etc.)
        # keep default caching.
        bare = self.path.split("?", 1)[0].split("#", 1)[0]
        if bare.endswith(".html") or bare in ("/", "/dashboard/"):
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
        super().end_headers()

    # ------------------------------------------------------------------
    # Response helpers
    # ------------------------------------------------------------------

    def do_OPTIONS(self):
        # No CORS — the dashboard is same-origin. Respond 200 so preflight
        # from the same origin still works for non-simple requests.
        self.send_response(200)
        self.end_headers()

    def _json_response(self, data, status=200, extra_headers: list = None):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        for k, v in (extra_headers or []):
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _text_response(self, text, status=200):
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _error(self, status, message):
        self._json_response({"error": message}, status)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(length)

    # ------------------------------------------------------------------
    # Session auth
    # ------------------------------------------------------------------

    def _session_token(self) -> str | None:
        raw = self.headers.get("Cookie", "")
        for part in raw.split(";"):
            k, _, v = part.strip().partition("=")
            if k == SESSION_COOKIE:
                return v
        return None

    def _is_authed(self) -> bool:
        tok = self._session_token()
        if not tok:
            return False
        with _sessions_lock:
            return tok in _sessions

    def _require_auth(self) -> bool:
        """Return True if request may proceed. On failure, writes a 401 and returns False."""
        path = self.path.split("?", 1)[0]
        if not path.startswith("/api/"):
            return True
        if path in _AUTH_EXEMPT_API:
            return True
        if self._is_authed():
            return True
        self._error(401, "Not authenticated")
        return False

    # ------------------------------------------------------------------
    # Routing
    # ------------------------------------------------------------------

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if not self._require_auth():
            return

        if path == "/api/projects":
            projects = project_mgr.list_projects()
            for p in projects:
                mem_path = BASE_DIR / "projects" / p.get("slug", "") / "memory" / "project_memory.json"
                if mem_path.exists():
                    try:
                        m = json.loads(mem_path.read_text(encoding="utf-8"))
                        if m.get("paused"):
                            p["paused"] = True
                            p["paused_reason"] = m.get("paused_reason", "")
                    except Exception:
                        pass
            self._json_response(projects)
        elif path.startswith("/api/projects/"):
            self._handle_project_get(path[len("/api/projects/"):])
        elif path == "/api/tasks":
            self._json_response(task_mgr.list_tasks())
        elif path.startswith("/api/tasks/"):
            self._handle_get_task_file(path[len("/api/tasks/"):])
        elif path == "/api/memory":
            self._handle_get_memory()
        elif path == "/api/run/output":
            self._handle_get_run_output()
        elif path == "/api/run/status":
            self._json_response(mem.list_runs())
        elif path == "/api/tokens":
            self._handle_get_tokens()
        elif path == "/api/settings":
            self._json_response({"peer_review_enabled": _peer_review_enabled})
        elif path == "/api/health":
            self._handle_get_health()
        elif path == "/api/agents":
            self._json_response(agent_registry.list_all())
        elif path.startswith("/api/agents/"):
            self._handle_get_agent(path[len("/api/agents/"):])
        elif path == "/api/teams":
            self._json_response(team_mgr.list_teams())
        elif path.startswith("/api/teams/"):
            self._handle_get_team(path[len("/api/teams/"):])
        elif path == "/api/skills":
            self._json_response(skill_mgr.list_skills())
        elif path.startswith("/api/skills/"):
            self._handle_get_skill(path[len("/api/skills/"):])
        elif path == "/" or path == "":
            self.send_response(302)
            self.send_header("Location", "/dashboard/menu.html")
            self.end_headers()
        else:
            super().do_GET()

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        if not self._require_auth():
            return

        if path == "/api/login":
            self._handle_post_login()
        elif path == "/api/logout":
            self._handle_post_logout()
        elif path == "/api/projects":
            self._handle_post_project_create()
        elif path.startswith("/api/projects/"):
            self._handle_project_post(path[len("/api/projects/"):])
        elif path == "/api/tasks":
            self._handle_post_task()
        elif path == "/api/tasks/assign":
            self._handle_post_assign()
        elif path == "/api/tasks/done":
            self._handle_post_done()
        elif path == "/api/run":
            self._handle_post_run()
        elif path == "/api/tokens/record":
            self._handle_post_token_record()
        elif path == "/api/settings/peer-review":
            self._handle_post_toggle_peer_review()
        elif path == "/api/webhook/linear":
            self._handle_webhook_linear()
        elif path == "/api/webhook/jira":
            self._handle_webhook_jira()
        elif path == "/api/agents":
            self._handle_post_agent_create()
        elif path == "/api/teams":
            self._handle_post_team_create()
        elif path == "/api/skills":
            self._handle_post_skill_create()
        elif path == "/api/sandbox/run":
            self._handle_post_sandbox_run()
        else:
            self.send_error(404, "Not found")

    def do_DELETE(self):
        path = self.path.split("?", 1)[0]
        if not self._require_auth():
            return
        if path.startswith("/api/agents/"):
            self._handle_delete_agent(path[len("/api/agents/"):])
        elif path.startswith("/api/teams/"):
            self._handle_delete_team(path[len("/api/teams/"):])
        elif path.startswith("/api/skills/"):
            self._handle_delete_skill(path[len("/api/skills/"):])
        else:
            self.send_error(404, "Not found")

    # ------------------------------------------------------------------
    # Project routing helpers
    # ------------------------------------------------------------------

    def _handle_project_get(self, sub):
        """Route GET /api/projects/{slug}/... requests."""
        parts = sub.split("/", 1)
        slug = parts[0]
        rest = parts[1] if len(parts) > 1 else ""

        if not slug:
            self._error(400, "Missing project slug")
            return
        if not _valid_slug(slug):
            self._error(400, "Invalid project slug")
            return

        if rest == "tasks":
            self._json_response(task_mgr.list_tasks(project_slug=slug))
        elif rest.startswith("tasks/"):
            filename = rest[len("tasks/"):]
            self._handle_get_project_task_file(slug, filename)
        elif rest == "output":
            self._handle_get_project_output_list(slug)
        elif rest.startswith("output/"):
            self._handle_get_project_output_file(slug, rest[len("output/"):])
        elif rest == "runs":
            self._handle_get_project_runs(slug)
        elif rest.startswith("runs/"):
            run_rest = rest[len("runs/"):]
            run_parts = run_rest.split("/", 1)
            run_id = run_parts[0]
            run_sub = run_parts[1] if len(run_parts) > 1 else ""
            if run_sub == "output":
                self._handle_get_project_run_snapshot_list(slug, run_id)
            elif run_sub.startswith("output/"):
                self._handle_get_project_run_snapshot_file(slug, run_id, run_sub[len("output/"):])
        elif rest == "memory":
            self._handle_get_project_memory(slug)
        elif rest == "memory/decisions":
            self._handle_get_project_decisions(slug)
        elif rest.startswith("memory/decisions/"):
            category = rest[len("memory/decisions/"):]
            self._handle_get_project_decision_category(slug, category)
        elif rest == "run/output":
            self._handle_get_project_run_output(slug)
        elif rest == "run/status":
            self._json_response(mem.list_runs(project_slug=slug))
        elif rest == "github":
            self._handle_get_project_github(slug)
        elif rest == "linear":
            self._handle_get_project_linear(slug)
        else:
            # Return project info for /api/projects/{slug}
            try:
                self._json_response(project_mgr.get_project(slug))
            except FileNotFoundError:
                self._error(404, f"Project not found: {slug}")

    def _handle_project_post(self, sub):
        """Route POST /api/projects/{slug}/... requests."""
        parts = sub.split("/", 1)
        slug = parts[0]
        rest = parts[1] if len(parts) > 1 else ""

        if not slug:
            self._error(400, "Missing project slug")
            return
        if not _valid_slug(slug):
            self._error(400, "Invalid project slug")
            return

        if rest == "tasks":
            self._handle_post_project_task(slug)
        elif rest == "tasks/assign":
            self._handle_post_project_assign(slug)
        elif rest == "tasks/done":
            self._handle_post_project_done(slug)
        elif rest == "run":
            self._handle_post_project_run(slug)
        elif rest == "tasks/delete":
            self._handle_post_project_task_delete(slug)
        elif rest == "tasks/retry":
            self._handle_post_project_retry(slug)
        elif rest == "kickoff":
            self._handle_post_project_kickoff(slug)
        elif rest == "run/all":
            self._handle_post_project_run_all(slug)
        elif rest == "output/clear":
            self._handle_post_project_output_clear(slug)
        elif rest == "delete":
            self._handle_post_project_delete(slug)
        elif rest == "resume":
            self._handle_post_project_resume(slug)
        else:
            self._error(404, f"Not found: /api/projects/{sub}")

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------

    def _handle_post_login(self):
        try:
            body = json.loads(self._read_body())
        except (json.JSONDecodeError, ValueError):
            self._error(400, "Invalid JSON")
            return
        expected_user = os.environ.get("OFFICE_USER", "admin")
        expected_pass = os.environ.get("OFFICE_PASS", "")
        if not expected_pass:
            self._json_response(
                {"ok": False, "error": "Server misconfigured: OFFICE_PASS not set."},
                status=500)
            return
        u_match = hmac.compare_digest(str(body.get("username", "")), expected_user)
        p_match = hmac.compare_digest(str(body.get("password", "")), expected_pass)
        if u_match and p_match:
            token = secrets.token_urlsafe(32)
            with _sessions_lock:
                _sessions.add(token)
            cookie = (f"{SESSION_COOKIE}={token}; HttpOnly; SameSite=Strict; "
                      f"Path=/; Max-Age=2592000")
            self._json_response({"ok": True}, extra_headers=[("Set-Cookie", cookie)])
        else:
            self._json_response({"ok": False, "error": "Invalid credentials."}, status=401)

    def _handle_post_logout(self):
        """Invalidate the caller's session cookie. Safe to call when not logged in."""
        token = self._session_token()
        if token:
            with _sessions_lock:
                _sessions.discard(token)
        # Expire the cookie on the client too.
        cookie = f"{SESSION_COOKIE}=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0"
        self._json_response({"ok": True}, extra_headers=[("Set-Cookie", cookie)])

    # ------------------------------------------------------------------
    # Project CRUD
    # ------------------------------------------------------------------

    def _handle_post_project_create(self):
        try:
            body = json.loads(self._read_body())
        except (json.JSONDecodeError, ValueError):
            self._error(400, "Invalid JSON")
            return
        name = (body.get("name") or "").strip()
        description = (body.get("description") or "").strip()
        team = (body.get("team") or "").strip().lower()
        if not name:
            self._error(400, "name is required")
            return
        if team:
            try:
                team_mgr.get_team(team)
            except FileNotFoundError:
                self._error(400, f"Team not found: {team}")
                return
        try:
            slug = project_mgr.create_project(name, description)
        except ValueError as e:
            self._error(409, str(e))
            return
        if team:
            # Persist the team binding on the project so kickoff can read it.
            pj = BASE_DIR / "projects" / slug / "project.json"
            data = json.loads(pj.read_text(encoding="utf-8"))
            data["team"] = team
            pj.write_text(json.dumps(data, indent=2), encoding="utf-8")
        self._json_response({"slug": slug})

    # ------------------------------------------------------------------
    # Agents / teams / skills handlers
    # ------------------------------------------------------------------

    def _handle_get_agent(self, agent_id: str):
        agent_id = agent_id.strip().lower()
        if not agent_registry.is_valid(agent_id):
            self._error(404, f"Agent not found: {agent_id}")
            return
        try:
            self._text_response(agent_registry.read_agent(agent_id))
        except FileNotFoundError:
            self._error(404, f"Agent file missing: {agent_id}")

    def _handle_post_agent_create(self):
        try:
            body = json.loads(self._read_body())
        except (json.JSONDecodeError, ValueError):
            self._error(400, "Invalid JSON")
            return
        agent_id = (body.get("id") or "").strip().lower()
        md_body = body.get("body") or ""
        if not agent_registry.AGENT_ID_RE.match(agent_id):
            self._error(400, "id must be lowercase letters/digits/dashes (start with a letter)")
            return
        if not md_body.strip():
            self._error(400, "body is required")
            return
        target = agent_registry.AGENTS_DIR / f"{agent_id}.md"
        if target.exists():
            self._error(409, f"Agent already exists: {agent_id}")
            return
        agent_registry.AGENTS_DIR.mkdir(parents=True, exist_ok=True)
        target.write_text(md_body, encoding="utf-8")
        self._json_response({"id": agent_id, "builtin": False, "exists": True})

    def _handle_delete_agent(self, agent_id: str):
        agent_id = agent_id.strip().lower()
        if agent_id in agent_registry.BUILTIN_AGENTS:
            self._error(403, "Built-in agents cannot be deleted")
            return
        if not agent_registry.AGENT_ID_RE.match(agent_id):
            self._error(400, "Invalid agent id")
            return
        target = agent_registry.AGENTS_DIR / f"{agent_id}.md"
        if not target.exists():
            self._error(404, f"Agent not found: {agent_id}")
            return
        target.unlink()
        self._json_response({"ok": True})

    def _handle_get_team(self, slug: str):
        slug = slug.strip().lower()
        try:
            self._json_response(team_mgr.get_team(slug))
        except FileNotFoundError:
            self._error(404, f"Team not found: {slug}")

    def _handle_post_team_create(self):
        try:
            body = json.loads(self._read_body())
        except (json.JSONDecodeError, ValueError):
            self._error(400, "Invalid JSON")
            return
        name = (body.get("name") or "").strip()
        description = (body.get("description") or "").strip()
        deputies = body.get("deputies") or []
        if not isinstance(deputies, list):
            self._error(400, "deputies must be a list")
            return
        try:
            data = team_mgr.create_team(name, description, deputies)
            self._json_response(data)
        except ValueError as e:
            self._error(400, str(e))

    def _handle_delete_team(self, slug: str):
        slug = slug.strip().lower()
        if not team_mgr.TEAM_SLUG_RE.match(slug):
            self._error(400, "Invalid team slug")
            return
        team_mgr.delete_team(slug)
        self._json_response({"ok": True})

    def _handle_get_skill(self, name: str):
        name = name.strip().lower()
        try:
            self._text_response(skill_mgr.read_skill(name))
        except FileNotFoundError:
            self._error(404, f"Skill not found: {name}")

    def _handle_post_skill_create(self):
        try:
            body = json.loads(self._read_body())
        except (json.JSONDecodeError, ValueError):
            self._error(400, "Invalid JSON")
            return
        name = (body.get("name") or "").strip().lower()
        md_body = body.get("body") or ""
        try:
            data = skill_mgr.create_skill(name, md_body)
            self._json_response(data)
        except ValueError as e:
            self._error(400, str(e))

    def _handle_delete_skill(self, name: str):
        name = name.strip().lower()
        if not skill_mgr.SKILL_NAME_RE.match(name):
            self._error(400, "Invalid skill name")
            return
        skill_mgr.delete_skill(name)
        self._json_response({"ok": True})

    # ------------------------------------------------------------------
    # Sandbox — run a single agent ad-hoc, no project state, no memory
    # ------------------------------------------------------------------

    def _handle_post_sandbox_run(self):
        try:
            body = json.loads(self._read_body())
        except (json.JSONDecodeError, ValueError):
            self._error(400, "Invalid JSON")
            return
        agent = (body.get("agent") or "").strip().lower()
        task  = (body.get("task") or "").strip()
        if not agent_registry.is_valid(agent):
            self._error(400, f"Unknown agent: {agent}")
            return
        if not task:
            self._error(400, "Task is required")
            return
        try:
            role_md = agent_registry.read_agent(agent)
        except FileNotFoundError:
            self._error(404, f"Agent file missing: {agent}")
            return

        prompt = (
            f"You are {agent}. Your role definition follows — read it fully and act in that role.\n\n"
            f"--- ROLE ---\n{role_md}\n--- END ROLE ---\n\n"
            f"This is a SANDBOX run — no project context, no other agents, no memory writes. "
            f"Just produce the deliverable for the task below.\n\n"
            f"TASK:\n{task}\n"
        )
        model = "claude-sonnet-4-6"
        start = time.time()
        try:
            proc = subprocess.run(
                ["claude", "--print", "--dangerously-skip-permissions",
                 "--output-format", "json", "--model", model, "-p", prompt],
                capture_output=True, text=True,
                cwd=str(BASE_DIR), timeout=300,
            )
        except subprocess.TimeoutExpired:
            self._error(504, "Agent run timed out (5 min)")
            return
        except FileNotFoundError:
            self._error(500, "claude CLI not found on this server")
            return
        elapsed_ms = int((time.time() - start) * 1000)

        text = proc.stdout
        cost = None
        try:
            outer = json.loads(proc.stdout)
            text = outer.get("result", proc.stdout) or proc.stdout
            cost = outer.get("total_cost_usd")
        except (json.JSONDecodeError, AttributeError):
            pass

        self._json_response({
            "agent": agent,
            "model": model,
            "output": text,
            "cost_usd": cost,
            "duration_ms": elapsed_ms,
            "stderr": (proc.stderr or "")[:2000],
        })

    # ------------------------------------------------------------------
    # Project-scoped task handlers
    # ------------------------------------------------------------------

    def _handle_get_project_task_file(self, slug, filename):
        if "/" in filename or ".." in filename:
            self._error(400, "Invalid filename")
            return
        bucket, path = task_mgr.find_task(filename, project_slug=slug)
        if path is None:
            self._error(404, "Task not found")
            return
        self._text_response(path.read_text(encoding="utf-8"))

    def _handle_post_project_task(self, slug):
        try:
            body = json.loads(self._read_body())
        except (json.JSONDecodeError, ValueError):
            self._error(400, "Invalid JSON")
            return
        title = (body.get("title") or "").strip()
        agent = (body.get("agent") or "").strip()
        description = (body.get("description") or "").strip()
        depends_on = (body.get("depends_on") or "").strip() or None
        if not title:
            self._error(400, "title is required")
            return
        if not agent:
            self._error(400, "agent is required")
            return
        filename = task_mgr.create_task(title, agent, description, project_slug=slug, depends_on=depends_on)
        self._json_response({"filename": filename, "path": f"projects/{slug}/tasks/backlog/{filename}"})

    def _handle_post_project_assign(self, slug):
        try:
            body = json.loads(self._read_body())
        except (json.JSONDecodeError, ValueError):
            self._error(400, "Invalid JSON")
            return
        filename = (body.get("filename") or "").strip()
        agent = (body.get("agent") or "").strip()
        if not filename or not agent:
            self._error(400, "filename and agent are required")
            return
        try:
            task_mgr.assign_task(filename, agent, project_slug=slug)
        except FileNotFoundError as e:
            self._error(404, str(e))
            return
        self._json_response({"ok": True})

    def _handle_post_project_done(self, slug):
        try:
            body = json.loads(self._read_body())
        except (json.JSONDecodeError, ValueError):
            self._error(400, "Invalid JSON")
            return
        filename = (body.get("filename") or "").strip()
        if not filename:
            self._error(400, "filename is required")
            return
        try:
            task_mgr.complete_task(filename, project_slug=slug)
        except FileNotFoundError as e:
            self._error(404, str(e))
            return
        activated = task_mgr.resolve_handoffs(filename, project_slug=slug)
        to_run = set(activated)
        active_dir = BASE_DIR / "projects" / slug / "tasks" / "active"
        if active_dir.exists():
            for f in active_dir.glob("*.md"):
                try:
                    content = f.read_text(encoding="utf-8")
                    dep = task_mgr.parse_depends_on(content)
                    if dep and dep == filename:
                        to_run.add(f.name)
                except Exception:
                    pass
        for dep_filename in to_run:
            dep_path = active_dir / dep_filename
            dep_content = dep_path.read_text(encoding="utf-8") if dep_path.exists() else ""
            m = re.search(r'^\*\*Agent:\*\*\s*(.+)$', dep_content, re.MULTILINE)
            dep_agent = m.group(1).strip() if m else "orchestrator"
            if not agent_registry.is_valid(dep_agent):
                dep_agent = "orchestrator"
            _spawn_agent_task(slug, dep_filename, dep_agent)
        self._json_response({"ok": True, "activated": list(to_run)})

    def _handle_post_project_retry(self, slug):
        try:
            body = json.loads(self._read_body())
        except (json.JSONDecodeError, ValueError):
            self._error(400, "Invalid JSON")
            return
        filename = (body.get("filename") or "").strip()
        agent = (body.get("agent") or "").strip()
        if not filename or not agent:
            self._error(400, "filename and agent are required")
            return
        # Move from failed/ back to active/
        bucket, src = task_mgr.find_task(filename, project_slug=slug)
        if src is None or bucket != "failed":
            self._error(404, "Task not found in failed/")
            return
        task_mgr.assign_task(filename, agent, project_slug=slug)
        _spawn_agent_task(slug, filename, agent)
        self._json_response({"ok": True})

    def _handle_post_project_task_delete(self, slug):
        try:
            body = json.loads(self._read_body())
        except (json.JSONDecodeError, ValueError):
            self._error(400, "Invalid JSON")
            return
        filename = (body.get("filename") or "").strip()
        if not filename or ".." in filename or "/" in filename:
            self._error(400, "Invalid filename")
            return
        bucket, path = task_mgr.find_task(filename, project_slug=slug)
        if path is None:
            self._error(404, "Task not found")
            return
        path.unlink()
        self._json_response({"ok": True})

    def _handle_post_project_run_all(self, slug):
        """Start all active tasks for a project concurrently."""
        active_dir = BASE_DIR / "projects" / slug / "tasks" / "active"
        if not active_dir.exists():
            self._json_response({"started": []})
            return

        started = []
        for task_file in sorted(active_dir.glob("*.md")):
            filename = task_file.name
            content = task_file.read_text(encoding="utf-8")
            match = re.search(r'^\*\*Agent:\*\*\s*(.+)$', content, re.MULTILINE)
            agent = match.group(1).strip() if match else "orchestrator"
            if not agent_registry.is_valid(agent):
                agent = "orchestrator"
            if _spawn_agent_task(slug, filename, agent):
                started.append({"filename": filename, "agent": agent})

        self._json_response({"started": started})

    def _handle_post_project_kickoff(self, slug):
        try:
            body = json.loads(self._read_body())
        except (json.JSONDecodeError, ValueError):
            self._error(400, "Invalid JSON")
            return

        description = (body.get("description") or "").strip()
        if not description:
            self._error(400, "description is required")
            return

        _snapshot_output(slug)
        created, err = _do_kickoff(slug, description)
        if err:
            self._error(500, err)
            return

        # Auto-start tasks that have no dependencies (same logic as webhook path)
        backlog_dir = BASE_DIR / "projects" / slug / "tasks" / "backlog"
        for task_file in sorted(backlog_dir.glob("*.md")):
            try:
                content = task_file.read_text(encoding="utf-8")
                dep = task_mgr.parse_depends_on(content)
                if dep:
                    continue
                m = re.search(r'^\*\*Agent:\*\*\s*(.+)$', content, re.MULTILINE)
                agent = m.group(1).strip() if m else "orchestrator"
                if not agent_registry.is_valid(agent):
                    agent = "orchestrator"
                task_mgr.assign_task(task_file.name, agent, project_slug=slug)
                _spawn_agent_task(slug, task_file.name, agent)
            except Exception:
                pass

        self._json_response({"ok": True, "tasks": created})

    def _handle_post_project_output_clear(self, slug):
        output_dir = BASE_DIR / "output" / slug
        if output_dir.exists():
            for f in output_dir.rglob("*"):
                if ".runs" in f.parts:
                    continue
                if f.is_file() and f.name != "README.md":
                    f.unlink()
        self._json_response({"ok": True})

    def _handle_post_project_delete(self, slug):
        import shutil
        for d in (BASE_DIR / "projects" / slug, BASE_DIR / "output" / slug,
                  BASE_DIR / "runs" / slug):
            if d.exists():
                shutil.rmtree(d)
        self._json_response({"ok": True})

    def _handle_post_project_resume(self, slug):
        """Clear the paused flag on a project. Does NOT re-dispatch tasks —
        the caller runs /run/all if they want work to restart."""
        _update_project_memory(slug, {
            "paused": False,
            "paused_reason": "",
            "paused_at": 0,
        })
        self._json_response({"ok": True, "paused": False})

    def _handle_get_project_linear(self, slug):
        mem_path = BASE_DIR / "projects" / slug / "memory" / "project_memory.json"
        if not mem_path.exists():
            self._json_response({"issues": {}})
            return
        try:
            data = json.loads(mem_path.read_text(encoding="utf-8"))
            self._json_response({"issues": data.get("linear_issues", {})})
        except Exception:
            self._json_response({"issues": {}})

    def _handle_get_project_github(self, slug):
        mem_path = BASE_DIR / "projects" / slug / "memory" / "project_memory.json"
        if not mem_path.exists():
            self._json_response({"pr_url": None, "repo_url": None})
            return
        try:
            data = json.loads(mem_path.read_text(encoding="utf-8"))
            self._json_response({
                "pr_url": data.get("github_pr"),
                "repo_url": data.get("github_repo"),
            })
        except Exception:
            self._json_response({"pr_url": None, "repo_url": None})

    def _handle_get_project_runs(self, slug):
        """List output snapshots for a project."""
        runs_dir = BASE_DIR / "output" / slug / ".runs"
        if not runs_dir.exists():
            self._json_response([])
            return
        runs = []
        for d in sorted(runs_dir.iterdir(), reverse=True):
            if d.is_dir():
                files = [f for f in d.rglob("*") if f.is_file()]
                runs.append({
                    "id": d.name,
                    "file_count": len(files),
                    "total_size": sum(f.stat().st_size for f in files),
                })
        self._json_response(runs)

    def _handle_get_project_run_snapshot_list(self, slug, run_id):
        """List files in a specific output snapshot."""
        if ".." in run_id:
            self._error(400, "Invalid run id")
            return
        snap_dir = BASE_DIR / "output" / slug / ".runs" / run_id
        if not snap_dir.exists():
            self._error(404, "Run not found")
            return
        files = []
        for f in sorted(snap_dir.rglob("*")):
            if f.is_file():
                rel = str(f.relative_to(snap_dir))
                stat = f.stat()
                files.append({"path": rel, "size": stat.st_size, "modified": stat.st_mtime})
        self._json_response(files)

    def _handle_get_project_run_snapshot_file(self, slug, run_id, filepath):
        """Serve a file from a specific output snapshot."""
        import urllib.parse
        if ".." in run_id:
            self._error(400, "Invalid run id")
            return
        filepath = urllib.parse.unquote(filepath)
        if ".." in filepath:
            self._error(400, "Invalid path")
            return
        snap_dir = (BASE_DIR / "output" / slug / ".runs" / run_id).resolve()
        target = (snap_dir / filepath).resolve()
        try:
            target.relative_to(snap_dir)
        except ValueError:
            self._error(400, "Invalid path")
            return
        if not target.exists() or not target.is_file():
            self._error(404, "File not found")
            return
        qs = urllib.parse.parse_qs(self.path.split("?", 1)[1] if "?" in self.path else "")
        content = target.read_bytes()
        ct = "text/plain; charset=utf-8"
        if target.suffix == ".md":
            ct = "text/markdown; charset=utf-8"
        elif target.suffix in (".json",):
            ct = "application/json"
        self.send_response(200)
        self.send_header("Content-Type", ct)
        self.send_header("Content-Length", str(len(content)))
        if qs.get("download"):
            self.send_header("Content-Disposition", f'attachment; filename="{target.name}"')
        self.end_headers()
        self.wfile.write(content)

    def _handle_get_project_output_list(self, slug):
        output_dir = BASE_DIR / "output" / slug
        if not output_dir.exists():
            self._json_response([])
            return
        files = []
        for f in sorted(output_dir.rglob("*")):
            # Skip .runs/ snapshots and README
            if ".runs" in f.parts:
                continue
            if f.is_file() and f.name != "README.md":
                rel = str(f.relative_to(output_dir))
                stat = f.stat()
                files.append({"path": rel, "size": stat.st_size, "modified": stat.st_mtime})
        self._json_response(files)

    def _handle_get_project_output_file(self, slug, filepath):
        import urllib.parse
        filepath = urllib.parse.unquote(filepath)
        if ".." in filepath:
            self._error(400, "Invalid path")
            return
        output_dir = (BASE_DIR / "output" / slug).resolve()
        target = (output_dir / filepath).resolve()
        try:
            target.relative_to(output_dir)
        except ValueError:
            self._error(400, "Invalid path")
            return
        if not target.exists() or not target.is_file():
            self._error(404, "File not found")
            return
        qs = urllib.parse.parse_qs(self.path.split("?", 1)[1] if "?" in self.path else "")
        if qs.get("download", ["0"])[0] == "1":
            body = target.read_bytes()
            filename = target.name
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self._text_response(target.read_text(encoding="utf-8", errors="replace"))

    def _handle_get_project_memory(self, slug):
        try:
            self._json_response(mem.read_project_memory(slug))
        except FileNotFoundError:
            self._error(404, f"Project memory not found: {slug}")

    def _handle_get_project_decisions(self, slug):
        """List all decision memory categories and their last-modified times."""
        decisions_dir = BASE_DIR / "projects" / slug / "memory" / "decisions"
        if not decisions_dir.exists():
            self._json_response([])
            return
        result = []
        for f in sorted(decisions_dir.glob("*.md")):
            stat = f.stat()
            result.append({"category": f.stem, "size": stat.st_size, "modified": stat.st_mtime})
        self._json_response(result)

    def _handle_get_project_decision_category(self, slug, category):
        """Return the content of one decision memory file."""
        if not category or ".." in category or "/" in category:
            self._error(400, "Invalid category")
            return
        decisions_dir = BASE_DIR / "projects" / slug / "memory" / "decisions"
        target = decisions_dir / f"{category}.md"
        if not target.exists():
            self._text_response("")
            return
        self._text_response(target.read_text(encoding="utf-8"))

    def _handle_get_project_run_output(self, slug):
        import urllib.parse
        qs = urllib.parse.parse_qs(self.path.split("?", 1)[1] if "?" in self.path else "")
        task_id = (qs.get("task_id") or [""])[0]
        self._json_response(mem.read_run(task_id, project_slug=slug))

    def _handle_post_project_run(self, slug):
        try:
            body = json.loads(self._read_body())
        except (json.JSONDecodeError, ValueError):
            self._error(400, "Invalid JSON")
            return

        filename = (body.get("filename") or "").strip()
        agent = (body.get("agent") or "").strip()
        if not filename or not agent:
            self._error(400, "filename and agent are required")
            return

        active_path = BASE_DIR / "projects" / slug / "tasks" / "active" / filename
        if not active_path.exists():
            self._error(400, f"Task not found in active/: {filename}")
            return

        _spawn_agent_task(slug, filename, agent)
        self._json_response({"ok": True, "task_id": filename})

    # ------------------------------------------------------------------
    # Global (legacy) task handlers — kept for CLI compatibility
    # ------------------------------------------------------------------

    def _handle_get_task_file(self, filename):
        if "/" in filename or ".." in filename:
            self._error(400, "Invalid filename")
            return
        bucket, path = task_mgr.find_task(filename)
        if path is None:
            self._error(404, "Task not found")
            return
        self._text_response(path.read_text(encoding="utf-8"))

    def _handle_post_task(self):
        try:
            body = json.loads(self._read_body())
        except (json.JSONDecodeError, ValueError):
            self._error(400, "Invalid JSON")
            return
        title = (body.get("title") or "").strip()
        agent = (body.get("agent") or "").strip()
        description = (body.get("description") or "").strip()
        if not title:
            self._error(400, "title is required")
            return
        if not agent:
            self._error(400, "agent is required")
            return
        filename = task_mgr.create_task(title, agent, description)
        self._json_response({"filename": filename, "path": f"tasks/backlog/{filename}"})

    def _handle_post_assign(self):
        try:
            body = json.loads(self._read_body())
        except (json.JSONDecodeError, ValueError):
            self._error(400, "Invalid JSON")
            return
        filename = (body.get("filename") or "").strip()
        agent = (body.get("agent") or "").strip()
        if not filename or not agent:
            self._error(400, "filename and agent are required")
            return
        try:
            task_mgr.assign_task(filename, agent)
        except FileNotFoundError as e:
            self._error(404, str(e))
            return
        self._json_response({"ok": True})

    def _handle_post_done(self):
        try:
            body = json.loads(self._read_body())
        except (json.JSONDecodeError, ValueError):
            self._error(400, "Invalid JSON")
            return
        filename = (body.get("filename") or "").strip()
        if not filename:
            self._error(400, "filename is required")
            return
        try:
            task_mgr.complete_task(filename)
        except FileNotFoundError as e:
            self._error(404, str(e))
            return
        self._json_response({"ok": True})

    def _handle_post_run(self):
        try:
            body = json.loads(self._read_body())
        except (json.JSONDecodeError, ValueError):
            self._error(400, "Invalid JSON")
            return
        filename = (body.get("filename") or "").strip()
        agent = (body.get("agent") or "").strip()
        if not filename or not agent:
            self._error(400, "filename and agent are required")
            return
        active_path = task_mgr.TASK_DIRS["active"] / filename
        if not active_path.exists():
            self._error(400, f"Task not found in active/: {filename}")
            return
        prompt = (
            f"You are the {agent} agent in the ai-office multi-agent framework.\n\n"
            "Steps:\n"
            "1. Read CLAUDE.md\n"
            f"2. Read agents/{agent}.md\n"
            f"3. Read tasks/active/{filename}\n"
            "4. Complete the task\n"
            "5. Update memory/team_memory.md and memory/team_memory.json\n"
            "6. Move task to tasks/completed/\n\n"
            "Work autonomously. Complete the task fully."
        )
        proc = subprocess.Popen(
            ["claude", "--print", "--dangerously-skip-permissions",
             "--verbose", "--output-format", "stream-json", prompt],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL, text=True, cwd=str(BASE_DIR),
        )
        with _live_procs_lock:
            _live_procs[("global", filename)] = proc
        mem.write_run(filename, [], False)

        def _parse(line):
            try:
                event = json.loads(line)
            except Exception:
                return line if line.strip() else None
            t = event.get("type")
            if t == "assistant":
                for item in event.get("message", {}).get("content", []):
                    if item.get("type") == "text" and item.get("text", "").strip():
                        return item["text"].strip()
                    elif item.get("type") == "tool_use":
                        n = item.get("name", ""); i = item.get("input", {})
                        if n == "Read": return f"> Read: {i.get('file_path', '')}"
                        if n == "Write": return f"> Write: {i.get('file_path', '')}"
                        if n == "Edit": return f"> Edit: {i.get('file_path', '')}"
                        if n == "Bash": return f"> $ {i.get('command', '')[:80]}"
                        return f"> {n}()"
            elif t == "result":
                cost = event.get("total_cost_usd", 0)
                return f"✓ Done  (${cost:.4f})" if event.get("subtype") == "success" else f"✗ Error: {event.get('result', '')}"
            return None

        def _reader(fname, p):
            lines = []
            try:
                for line in p.stdout:
                    line = line.rstrip("\n")
                    if not line: continue
                    try:
                        f = _parse(line)
                        if f: lines.append(f); mem.write_run(fname, lines, False)
                    except Exception: pass
            finally:
                p.wait(); mem.write_run(fname, lines, True)
                with _live_procs_lock:
                    _live_procs.pop(("global", fname), None)

        threading.Thread(target=_reader, args=(filename, proc), daemon=True).start()
        self._json_response({"ok": True, "task_id": filename})

    def _handle_get_run_output(self):
        import urllib.parse
        qs = urllib.parse.parse_qs(self.path.split("?", 1)[1] if "?" in self.path else "")
        task_id = (qs.get("task_id") or [""])[0]
        self._json_response(mem.read_run(task_id))

    def _handle_get_memory(self):
        try:
            self._json_response(mem.read_memory())
        except FileNotFoundError:
            self._error(404, "team_memory.json not found")
        except (json.JSONDecodeError, IOError) as e:
            self._error(500, str(e))

    def _handle_webhook_linear(self):
        body = self._read_body()
        if LINEAR_WEBHOOK_SECRET:
            sig = self.headers.get("linear-signature", "")
            expected = hmac.new(LINEAR_WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
            if not hmac.compare_digest(sig, expected):
                self._error(401, "Invalid signature")
                return
        try:
            payload = json.loads(body)
        except (json.JSONDecodeError, ValueError):
            self._error(400, "Invalid JSON")
            return

        if payload.get("type") != "Issue":
            self._json_response({"ok": True, "skipped": "not an issue event"})
            return
        if payload.get("action") not in ("create", "update"):
            self._json_response({"ok": True, "skipped": "action not create/update"})
            return

        data = payload.get("data", {})
        labels = [l.get("name", "").lower() for l in data.get("labels", [])]
        if WEBHOOK_TRIGGER_LABEL.lower() not in labels:
            self._json_response({"ok": True, "skipped": "trigger label not present"})
            return

        title = data.get("title", "").strip()
        description = (data.get("description") or title).strip()
        if not title:
            self._error(400, "Issue has no title")
            return

        self._json_response({"ok": True, "project": title})
        threading.Thread(target=_run_webhook_project, args=(title, description), daemon=True).start()

    def _handle_webhook_jira(self):
        body = self._read_body()
        if JIRA_WEBHOOK_SECRET:
            sig = self.headers.get("x-hub-signature", "") or self.headers.get("x-hub-signature-256", "")
            if sig.startswith("sha256="):
                sig = sig[len("sha256="):]
            expected = hmac.new(JIRA_WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
            if not sig or not hmac.compare_digest(sig, expected):
                self._error(401, "Invalid signature")
                return
        try:
            payload = json.loads(body)
        except (json.JSONDecodeError, ValueError):
            self._error(400, "Invalid JSON")
            return

        event = payload.get("webhookEvent", "")
        if event not in ("jira:issue_created", "jira:issue_updated"):
            self._json_response({"ok": True, "skipped": f"event={event}"})
            return

        issue = payload.get("issue", {})
        fields = issue.get("fields", {})
        labels = [l.lower() for l in fields.get("labels", [])]
        if WEBHOOK_TRIGGER_LABEL.lower() not in labels:
            self._json_response({"ok": True, "skipped": "trigger label not present"})
            return

        title = fields.get("summary", "").strip()
        description = (fields.get("description") or title).strip()
        if not title:
            self._error(400, "Issue has no summary")
            return

        self._json_response({"ok": True, "project": title})
        threading.Thread(target=_run_webhook_project, args=(title, description), daemon=True).start()

    def _handle_post_toggle_peer_review(self):
        global _peer_review_enabled
        try:
            body = json.loads(self._read_body())
            _peer_review_enabled = bool(body.get("enabled", not _peer_review_enabled))
        except Exception:
            _peer_review_enabled = not _peer_review_enabled
        self._json_response({"peer_review_enabled": _peer_review_enabled})

    def _handle_post_token_record(self):
        try:
            data = json.loads(self._read_body())
            _record_token_usage(
                project=data.get("project", ""),
                agent=data.get("agent", ""),
                task=data.get("task", ""),
                input_tokens=data.get("input_tokens", 0),
                output_tokens=data.get("output_tokens", 0),
                cache_read_tokens=data.get("cache_read_tokens", 0),
                cache_creation_tokens=data.get("cache_creation_tokens", 0),
                cost_usd=data.get("cost_usd", 0),
            )
            self._json_response({"ok": True})
        except Exception as e:
            self._error(500, str(e))

    def _handle_get_health(self):
        import sys as _sys
        _sys.path.insert(0, str(BASE_DIR))
        try:
            from tests.health_check import run_checks
            results = run_checks()
        except Exception as e:
            results = [{"name": "health_check_import", "status": "fail", "msg": str(e)}]
        overall = "fail" if any(r["status"] == "fail" for r in results) else "pass"
        self._json_response({"status": overall, "checks": results})

    def _handle_get_tokens(self):
        import urllib.parse
        qs = urllib.parse.parse_qs(self.path.split("?", 1)[1] if "?" in self.path else "")
        project_filter = qs.get("project", [None])[0]
        try:
            result = token_tracker.query(project_filter)
            result["claude_code"] = token_tracker.read_claude_code_usage()
            self._json_response(result)
        except Exception as e:
            self._json_response({"runs": [], "totals": {}, "error": str(e)})

    def log_message(self, format, *args):
        if "/api/" in str(args[0] if args else ""):
            super().log_message(format, *args)


def _load_env():
    """Load .env file from project root if it exists."""
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val


def _write_mcp_config():
    """Write mcp_search.json with the real API key substituted in."""
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        return
    config = {
        "mcpServers": {
            "web_search": {
                "command": "python3",
                "args": [str(BASE_DIR / "tools" / "perplexity_search.py")],
                "env": {"OPENAI_API_KEY": api_key},
            }
        }
    }
    MCP_SEARCH_CONFIG.write_text(json.dumps(config, indent=2), encoding="utf-8")
    print(f"MCP config written with OpenAI key ({api_key[:8]}…)")


def _recover_stuck_tasks():
    """On startup, move any tasks left in active/ back to backlog.

    These are tasks that were running when the server last crashed.
    They have no live process — move them back so they can be re-run.

    Also re-trigger CI for any project that finished all tasks but never
    got a GitHub PR (server was killed between last task completing and CI).
    """
    projects_dir = BASE_DIR / "projects"
    if not projects_dir.exists():
        return
    recovered = 0
    for active_dir in projects_dir.glob("*/tasks/active"):
        slug = active_dir.parts[-3]
        for task_file in active_dir.glob("*.md"):
            try:
                content = task_file.read_text(encoding="utf-8")
                content = re.sub(r"^\*\*Status:\*\*.*$", "**Status:** backlog",
                                 content, flags=re.MULTILINE)
                backlog_dir = active_dir.parent / "backlog"
                backlog_dir.mkdir(parents=True, exist_ok=True)
                (backlog_dir / task_file.name).write_text(content, encoding="utf-8")
                task_file.unlink()
                recovered += 1
            except Exception:
                pass
    if recovered:
        print(f"Recovered {recovered} stuck task(s) → backlog")

    # Re-trigger CI for projects that completed all tasks but never got a PR
    for mem_path in projects_dir.glob("*/memory/project_memory.json"):
        slug = mem_path.parts[-3]
        try:
            raw = mem_path.read_text(encoding="utf-8")
            # Use string search as fallback when JSON is malformed
            try:
                has_pr = bool(json.loads(raw).get("github_pr"))
            except (json.JSONDecodeError, AttributeError):
                has_pr = '"github_pr"' in raw and '"github_pr": null' not in raw
            if has_pr:
                continue
            completed_dir = BASE_DIR / "projects" / slug / "tasks" / "completed"
            if not completed_dir.exists() or not any(completed_dir.glob("*.md")):
                continue
            if not _all_tasks_done(slug):
                continue
            print(f"Re-triggering CI for {slug} (completed but no PR)")
            threading.Thread(target=_run_ci_tests, args=(slug, 0), daemon=True).start()
        except Exception:
            pass


if __name__ == "__main__":
    _load_env()
    # Re-read env-backed globals now that .env is loaded into os.environ
    LINEAR_WEBHOOK_SECRET = os.environ.get("LINEAR_WEBHOOK_SECRET", "")
    JIRA_WEBHOOK_SECRET   = os.environ.get("JIRA_WEBHOOK_SECRET", "")
    WEBHOOK_TRIGGER_LABEL = os.environ.get("WEBHOOK_TRIGGER_LABEL", "ai-office")
    PROJECT_BUDGET_USD    = float(os.environ.get("PROJECT_BUDGET_USD", "0") or 0)

    # If no OFFICE_PASS configured, mint an ephemeral one and print it so the
    # dashboard is never wide-open with a known default credential.
    if not os.environ.get("OFFICE_PASS"):
        _tmp_pass = secrets.token_urlsafe(16)
        os.environ["OFFICE_PASS"] = _tmp_pass
        _tmp_user = os.environ.get("OFFICE_USER", "admin")
        print("⚠ OFFICE_PASS not set — generated for this session:")
        print(f"    username: {_tmp_user}")
        print(f"    password: {_tmp_pass}")
        print("  Add OFFICE_PASS=<value> to .env to keep it across restarts.\n")

    _write_mcp_config()
    _recover_stuck_tasks()
    os.chdir(BASE_DIR)
    _init_tokens_db()
    server = http.server.HTTPServer(("", PORT), AIOfficeHandler)
    print(f"AI Office running at http://localhost:{PORT}/dashboard/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
