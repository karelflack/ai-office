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
import subprocess
import threading
from pathlib import Path

from core import agents as agent_registry
from core import memory as mem
from core import tasks as task_mgr
from core import projects as project_mgr

PORT = 8000
BASE_DIR = Path(__file__).parent.resolve()

# Tracks live subprocess references keyed by (project_slug, filename).
_live_procs: dict = {}


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
        if not title:
            self._error(400, "title is required")
            return
        if not agent:
            self._error(400, "agent is required")
            return
        filename = task_mgr.create_task(title, agent, description, project_slug=slug)
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
            # Parse agent from task file
            content = task_file.read_text(encoding="utf-8")
            match = re.search(r'^\*\*Agent:\*\*\s*(.+)$', content, re.MULTILINE)
            agent = match.group(1).strip() if match else "orchestrator"
            if agent not in agent_registry.VALID_AGENTS:
                agent = "orchestrator"

            key = (slug, filename)
            if key in _live_procs:
                continue  # already running

            prompt = (
                f"You are the {agent} agent in the ai-office multi-agent framework.\n\n"
                f"You are working on project: '{slug}'\n\n"
                "Steps to follow:\n"
                "1. Read CLAUDE.md for session protocol\n"
                f"2. Read agents/{agent}.md for your full role definition\n"
                f"3. Read projects/{slug}/memory/project_memory.json for project context\n"
                f"4. Read the task file at projects/{slug}/tasks/active/{filename}\n"
                "5. Complete the task as described\n"
                f"6. Write all deliverables to projects/{slug}/output/ — name files clearly\n"
                f"7. Update projects/{slug}/output/README.md with your new file\n"
                f"8. Update projects/{slug}/memory/project_memory.json with your notes\n"
                f"9. Move the task to projects/{slug}/tasks/completed/ and delete it from active/\n\n"
                "Work autonomously. Produce real, useful output."
            )

            proc = subprocess.Popen(
                ["claude", "--print", "--dangerously-skip-permissions",
                 "--verbose", "--output-format", "stream-json", prompt],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL, text=True, cwd=str(BASE_DIR),
            )
            _live_procs[key] = proc
            mem.write_run(filename, [], False, project_slug=slug)

            def _make_reader(k, fname, p, proj_slug):
                def _reader():
                    lines = []
                    try:
                        for line in p.stdout:
                            line = line.rstrip("\n")
                            if not line:
                                continue
                            try:
                                event = json.loads(line)
                                t = event.get("type")
                                formatted = None
                                if t == "assistant":
                                    for item in event.get("message", {}).get("content", []):
                                        if item.get("type") == "text" and item.get("text", "").strip():
                                            formatted = item["text"].strip()
                                        elif item.get("type") == "tool_use":
                                            n = item.get("name", ""); i = item.get("input", {})
                                            if n == "Read": formatted = f"> Read: {i.get('file_path', '')}"
                                            elif n == "Write": formatted = f"> Write: {i.get('file_path', '')}"
                                            elif n == "Edit": formatted = f"> Edit: {i.get('file_path', '')}"
                                            elif n == "Bash": formatted = f"> $ {i.get('command', '')[:80]}"
                                            else: formatted = f"> {n}()"
                                elif t == "result":
                                    cost = event.get("total_cost_usd", 0)
                                    formatted = f"✓ Done  (${cost:.4f})" if event.get("subtype") == "success" else f"✗ Error: {event.get('result', '')}"
                                if formatted:
                                    lines.append(formatted)
                                    mem.write_run(fname, lines, False, project_slug=proj_slug)
                            except Exception:
                                pass
                    finally:
                        p.wait()
                        mem.write_run(fname, lines, True, project_slug=proj_slug)
                        _live_procs.pop(k, None)
                return _reader

            threading.Thread(target=_make_reader(key, filename, proc, slug), daemon=True).start()
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

Reply with ONLY a JSON array, no markdown, no explanation:
[{{"agent":"bjorn","title":"System Architecture","description":"Design the full system..."}},...]"""

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
        created = []
        valid_agents = agent_registry.VALID_AGENTS
        for item in plan:
            agent = str(item.get("agent", "orchestrator")).strip().lower()
            title = str(item.get("title", "Untitled")).strip()
            desc  = str(item.get("description", "")).strip()
            if agent not in valid_agents:
                agent = "orchestrator"
            filename = task_mgr.create_task(title, agent, desc, project_slug=slug)
            created.append({"filename": filename, "agent": agent, "title": title, "description": desc})

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
        output_dir = BASE_DIR / "projects" / slug / "output"
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
        if ".." in filepath:
            self._error(400, "Invalid path")
            return
        output_dir = (BASE_DIR / "projects" / slug / "output").resolve()
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

        prompt = (
            f"You are the {agent} agent in the ai-office multi-agent framework.\n\n"
            f"You are working on project: '{slug}'\n\n"
            "Steps to follow:\n"
            "1. Read CLAUDE.md for session protocol\n"
            f"2. Read agents/{agent}.md for your full role definition\n"
            f"3. Read projects/{slug}/memory/project_memory.json for project context\n"
            f"4. Read the task file at projects/{slug}/tasks/active/{filename}\n"
            "5. Complete the task as described\n"
            f"6. Write all deliverables to projects/{slug}/output/ — name files clearly\n"
            f"7. Update projects/{slug}/output/README.md with your new file\n"
            f"8. Update projects/{slug}/memory/project_memory.json with your notes under agent_notes\n"
            f"9. Move the task to projects/{slug}/tasks/completed/ and delete it from active/\n\n"
            "Work autonomously. Use your tools. Produce real, useful output."
        )

        proc = subprocess.Popen(
            ["claude", "--print", "--dangerously-skip-permissions",
             "--verbose", "--output-format", "stream-json", prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            text=True,
            cwd=str(BASE_DIR),
        )

        key = (slug, filename)
        _live_procs[key] = proc
        mem.write_run(filename, [], False, project_slug=slug)

        def _parse_stream_event(line):
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
                        if name == "Read":
                            return f"> Read: {inp.get('file_path', '')}"
                        elif name == "Write":
                            return f"> Write: {inp.get('file_path', '')}"
                        elif name == "Edit":
                            return f"> Edit: {inp.get('file_path', '')}"
                        elif name == "Bash":
                            return f"> $ {inp.get('command', '')[:80]}"
                        elif name == "Glob":
                            return f"> Glob: {inp.get('pattern', '')}"
                        elif name == "Grep":
                            return f"> Grep: {inp.get('pattern', '')}"
                        else:
                            return f"> {name}()"
            elif t == "result":
                cost = event.get("total_cost_usd", 0)
                if event.get("subtype") == "success":
                    return f"✓ Done  (${cost:.4f})"
                else:
                    return f"✗ Error: {event.get('result', '')}"
            return None

        def _reader(k, fname, p, proj_slug):
            lines = []
            try:
                for line in p.stdout:
                    line = line.rstrip("\n")
                    if not line:
                        continue
                    try:
                        formatted = _parse_stream_event(line)
                        if formatted:
                            lines.append(formatted)
                            mem.write_run(fname, lines, False, project_slug=proj_slug)
                    except Exception:
                        pass
            finally:
                p.wait()
                mem.write_run(fname, lines, True, project_slug=proj_slug)
                _live_procs.pop(k, None)

        threading.Thread(target=_reader, args=(key, filename, proc, slug), daemon=True).start()
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

    def log_message(self, format, *args):
        if "/api/" in (args[0] if args else ""):
            super().log_message(format, *args)


if __name__ == "__main__":
    os.chdir(BASE_DIR)
    server = http.server.HTTPServer(("", PORT), AIOfficeHandler)
    print(f"AI Office running at http://localhost:{PORT}/dashboard/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
