#!/usr/bin/env python3
"""
AI Office HTTP server.
Serves static files from project root and provides a REST API under /api/.
Run with: python3 server.py
"""

import http.server
import json
import os
import re
import sqlite3
import subprocess
import threading
import time
from pathlib import Path

from core import agents as agent_registry
from core import memory as mem
from core import tasks as task_mgr
from core import projects as project_mgr

PORT = 8000
BASE_DIR = Path(__file__).parent.resolve()
TOKENS_DB = BASE_DIR / "tokens.db"

# Tracks live subprocess references keyed by (project_slug, filename).
_live_procs: dict = {}


def _init_tokens_db():
    con = sqlite3.connect(str(TOKENS_DB))
    con.execute("""
        CREATE TABLE IF NOT EXISTS token_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts INTEGER NOT NULL,
            project TEXT,
            agent TEXT,
            task TEXT,
            input_tokens INTEGER DEFAULT 0,
            output_tokens INTEGER DEFAULT 0,
            cache_read_tokens INTEGER DEFAULT 0,
            cache_creation_tokens INTEGER DEFAULT 0,
            cost_usd REAL DEFAULT 0
        )
    """)
    con.commit()
    con.close()


def _record_token_usage(project, agent, task, input_tokens, output_tokens,
                        cache_read_tokens, cache_creation_tokens, cost_usd):
    try:
        con = sqlite3.connect(str(TOKENS_DB))
        con.execute(
            "INSERT INTO token_usage (ts, project, agent, task, input_tokens, output_tokens, "
            "cache_read_tokens, cache_creation_tokens, cost_usd) VALUES (?,?,?,?,?,?,?,?,?)",
            (int(time.time()), project, agent, task,
             input_tokens, output_tokens, cache_read_tokens, cache_creation_tokens, cost_usd)
        )
        con.commit()
        con.close()
    except Exception:
        pass

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
                if name == "Read":   return f"> Read: {inp.get('file_path', '')}"
                if name == "Write":  return f"> Write: {inp.get('file_path', '')}"
                if name == "Edit":   return f"> Edit: {inp.get('file_path', '')}"
                if name == "Bash":   return f"> $ {inp.get('command', '')[:80]}"
                if name == "Glob":   return f"> Glob: {inp.get('pattern', '')}"
                if name == "Grep":   return f"> Grep: {inp.get('pattern', '')}"
                return f"> {name}()"
    elif t == "result":
        cost = event.get("total_cost_usd", 0)
        if event.get("subtype") == "success":
            return f"✓ Done  (${cost:.4f})"
        else:
            return f"✗ Error: {event.get('result', '')}"
    return None


def _spawn_agent_task(slug: str, filename: str, agent: str) -> bool:
    """Spawn a Claude subprocess for an active task. Returns False if already running."""
    key = (slug, filename)
    if key in _live_procs:
        return False

    output_subdir = AGENT_OUTPUT_DIR.get(agent, "strategy")
    output_path = f"output/{slug}/{output_subdir}"

    prompt = (
        f"You are the {agent} agent in the ai-office multi-agent framework.\n\n"
        f"You are working on project: '{slug}'\n\n"
        "Steps to follow:\n"
        "1. Read CLAUDE.md for session protocol\n"
        f"2. Read agents/{agent}.md for your full role definition\n"
        f"3. Read projects/{slug}/memory/project_memory.json for project context\n"
        f"4. Read the task file at projects/{slug}/tasks/active/{filename}\n"
        "5. Complete the task as described\n"
        f"6. Write all deliverables to {output_path}/ — name files clearly (YYYY-MM-DD-description.ext)\n"
        f"7. Update output/{slug}/README.md — add a row: | path/to/file | what it contains | {agent} | today's date |\n"
        f"8. Update projects/{slug}/memory/project_memory.json with your notes under agent_notes\n"
        f"9. Move the task to projects/{slug}/tasks/completed/ and delete it from active/\n\n"
        "Work autonomously. Use your tools. Produce real, useful output."
    )

    proc = subprocess.Popen(
        ["claude", "--print", "--dangerously-skip-permissions",
         "--verbose", "--output-format", "stream-json", prompt],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL, text=True, cwd=str(BASE_DIR),
    )
    _live_procs[key] = proc
    mem.write_run(filename, [], False, project_slug=slug)

    def _reader():
        lines = []
        succeeded = False
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
            _live_procs.pop(key, None)

            if failed:
                # Mark task failed and cascade to dependents
                reason = lines[-1] if lines else f"Process exited with code {exit_code}"
                task_mgr.fail_task(filename, reason=reason, project_slug=slug)
                task_mgr.cascade_fail(filename, project_slug=slug)
                return

            # Auto-dispatch: move backlog dependents to active and run them
            newly_activated = task_mgr.resolve_handoffs(filename, project_slug=slug)
            to_run = set(newly_activated)
            # Also pick up any tasks already in active/ that were waiting on this one
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
                if dep_agent not in agent_registry.VALID_AGENTS:
                    dep_agent = "orchestrator"
                _spawn_agent_task(slug, dep_filename, dep_agent)

    threading.Thread(target=_reader, daemon=True).start()
    return True


class AIOfficeHandler(http.server.SimpleHTTPRequestHandler):

    def translate_path(self, path):
        import urllib.parse
        path = urllib.parse.unquote(path)
        path = path.split("?", 1)[0].split("#", 1)[0]
        path = os.path.normpath(path)
        return str(BASE_DIR / path.lstrip("/"))

    # ------------------------------------------------------------------
    # CORS + response helpers
    # ------------------------------------------------------------------

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def _json_response(self, data, status=200):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def _text_response(self, text, status=200):
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def _error(self, status, message):
        self._json_response({"error": message}, status)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(length)

    # ------------------------------------------------------------------
    # Routing
    # ------------------------------------------------------------------

    def do_GET(self):
        path = self.path.split("?", 1)[0]

        if path == "/api/projects":
            self._json_response(project_mgr.list_projects())
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
        else:
            super().do_GET()

    def do_POST(self):
        path = self.path.split("?", 1)[0]

        if path == "/api/login":
            self._handle_post_login()
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

        if rest == "tasks":
            self._json_response(task_mgr.list_tasks(project_slug=slug))
        elif rest.startswith("tasks/"):
            filename = rest[len("tasks/"):]
            self._handle_get_project_task_file(slug, filename)
        elif rest == "output":
            self._handle_get_project_output_list(slug)
        elif rest.startswith("output/"):
            self._handle_get_project_output_file(slug, rest[len("output/"):])
        elif rest == "memory":
            self._handle_get_project_memory(slug)
        elif rest == "run/output":
            self._handle_get_project_run_output(slug)
        elif rest == "run/status":
            self._json_response(mem.list_runs(project_slug=slug))
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
        expected_pass = os.environ.get("OFFICE_PASS", "admin")
        if body.get("username") == expected_user and body.get("password") == expected_pass:
            self._json_response({"ok": True})
        else:
            self._json_response({"ok": False, "error": "Invalid credentials."}, status=401)

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
        if not name:
            self._error(400, "name is required")
            return
        try:
            slug = project_mgr.create_project(name, description)
            self._json_response({"slug": slug})
        except ValueError as e:
            self._error(409, str(e))

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
            if dep_agent not in agent_registry.VALID_AGENTS:
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
            if agent not in agent_registry.VALID_AGENTS:
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

        prompt = f"""You are a project planner for an AI agent office.

Project to plan: "{description}"

Choose 3-6 agents and define their tasks. Available agents:
- bjorn: system architecture, tech stack, data models, Mermaid diagrams
- arve: writing code, scaffolding projects, implementing features
- dag: DevOps, Docker, CI/CD pipelines, deployment
- else: research, market analysis, competitor landscape
- frode: sprint planning, backlog breakdown, story points
- nora: pricing model, revenue streams, unit economics
- magnus: legal, compliance, GDPR, privacy policy
- ingrid: UI/UX design, wireframes, user flows
- jorunn: brand identity, naming, tone of voice
- halvard: growth strategy, acquisition channels, onboarding
- knut: project milestones, progress tracking

Rules:
- For software projects: always start with bjorn (architecture), include arve (code)
- Only include agents genuinely relevant to this project type
- Order tasks logically: research/architecture first, implementation last
- Each description must be specific — what exactly to produce, what format, what decisions to make
- Use the "depends_on" field to declare which task (by title) must complete before this one starts. Set to null if the task can start immediately.
- Example: arve's implementation should depend on bjorn's architecture. odd's testing should depend on arve's implementation.

Reply with ONLY a JSON array, no markdown, no explanation:
[{{"agent":"bjorn","title":"System Architecture","description":"Design the full system...","depends_on":null}},{{"agent":"arve","title":"Implementation","description":"...","depends_on":"System Architecture"}}]"""

        try:
            proc = subprocess.run(
                ["claude", "--print", "--dangerously-skip-permissions",
                 "--output-format", "json", prompt],
                capture_output=True, text=True,
                cwd=str(BASE_DIR), timeout=120,
            )
        except subprocess.TimeoutExpired:
            self._error(504, "Planning timed out — try a shorter description")
            return
        except FileNotFoundError:
            self._error(500, "claude CLI not found")
            return

        # Parse outer JSON from --output-format json
        try:
            outer = json.loads(proc.stdout)
            text = outer.get("result", "")
        except (json.JSONDecodeError, AttributeError):
            text = proc.stdout

        # Extract JSON array from the text
        match = re.search(r'\[[\s\S]*\]', text)
        if not match:
            self._error(500, "Could not parse plan from orchestrator — try again")
            return

        try:
            plan = json.loads(match.group())
        except json.JSONDecodeError:
            self._error(500, "Orchestrator returned malformed plan — try again")
            return

        # Validate and create task files
        # First pass: create all tasks, build title → filename map
        created = []
        valid_agents = agent_registry.VALID_AGENTS
        title_to_filename: dict = {}
        for item in plan:
            agent = str(item.get("agent", "orchestrator")).strip().lower()
            title = str(item.get("title", "Untitled")).strip()
            desc  = str(item.get("description", "")).strip()
            raw_dep = item.get("depends_on")
            if agent not in valid_agents:
                agent = "orchestrator"
            # Resolve depends_on title → filename from previously created tasks
            depends_on = title_to_filename.get(raw_dep) if raw_dep else None
            filename = task_mgr.create_task(title, agent, desc, project_slug=slug, depends_on=depends_on)
            title_to_filename[title] = filename
            created.append({"filename": filename, "agent": agent, "title": title, "description": desc, "depends_on": depends_on})

        # Update project memory with the kickoff description
        mem_path = BASE_DIR / "projects" / slug / "memory" / "project_memory.json"
        if mem_path.exists():
            try:
                m = json.loads(mem_path.read_text(encoding="utf-8"))
                m["kickoff_description"] = description
                m["kickoff_plan"] = [{"agent": t["agent"], "title": t["title"]} for t in created]
                mem_path.write_text(json.dumps(m, indent=2), encoding="utf-8")
            except Exception:
                pass

        self._json_response({"ok": True, "tasks": created})

    def _handle_get_project_output_list(self, slug):
        output_dir = BASE_DIR / "output" / slug
        if not output_dir.exists():
            self._json_response([])
            return
        files = []
        for f in sorted(output_dir.rglob("*")):
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
        self._text_response(target.read_text(encoding="utf-8", errors="replace"))

    def _handle_get_project_memory(self, slug):
        try:
            self._json_response(mem.read_project_memory(slug))
        except FileNotFoundError:
            self._error(404, f"Project memory not found: {slug}")

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

    def _handle_get_tokens(self):
        try:
            con = sqlite3.connect(str(TOKENS_DB))
            con.row_factory = sqlite3.Row
            runs = con.execute(
                "SELECT * FROM token_usage ORDER BY ts DESC LIMIT 100"
            ).fetchall()
            totals = con.execute(
                "SELECT SUM(input_tokens) as input_tokens, SUM(output_tokens) as output_tokens, "
                "SUM(cache_read_tokens) as cache_read_tokens, SUM(cost_usd) as cost_usd "
                "FROM token_usage"
            ).fetchone()
            con.close()
            self._json_response({
                "runs": [dict(r) for r in runs],
                "totals": dict(totals) if totals else {},
            })
        except Exception as e:
            self._json_response({"runs": [], "totals": {}, "error": str(e)})

    def log_message(self, format, *args):
        if "/api/" in str(args[0] if args else ""):
            super().log_message(format, *args)


if __name__ == "__main__":
    os.chdir(BASE_DIR)
    _init_tokens_db()
    server = http.server.HTTPServer(("", PORT), AIOfficeHandler)
    print(f"AI Office running at http://localhost:{PORT}/dashboard/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
