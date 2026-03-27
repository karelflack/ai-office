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
import shutil
import subprocess
import threading
from datetime import date
from pathlib import Path

PORT = 8000
BASE_DIR = Path(__file__).parent.resolve()
TASKS_DIR = BASE_DIR / "tasks"
MEMORY_FILE = BASE_DIR / "memory" / "team_memory.json"

VALID_AGENTS = {
    "orchestrator", "arve", "bjorn", "dag", "else", "frode",
    "halvard", "guro", "jorunn", "ingrid", "knut", "laila",
    "magnus", "nora", "odd", "per",
}

TASK_DIRS = {
    "backlog":   TASKS_DIR / "backlog",
    "active":    TASKS_DIR / "active",
    "completed": TASKS_DIR / "completed",
}

# Tracks in-flight claude subprocess runs keyed by filename.
# Each value: { "process": Popen, "output": [str], "done": bool, "agent": str }
running_tasks: dict = {}


def slugify(text: str) -> str:
    """Lowercase, strip non-alphanumeric chars, replace spaces/underscores with hyphens."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s_-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def find_task(filename: str):
    """Search backlog, active, completed for a task file. Returns (bucket, path) or (None, None)."""
    for bucket, directory in TASK_DIRS.items():
        candidate = directory / filename
        if candidate.exists():
            return bucket, candidate
    return None, None


def update_markdown_fields(content: str, agent: str = None, status: str = None) -> str:
    """Use re.sub to update **Agent:** and **Status:** lines in markdown."""
    if agent is not None:
        content = re.sub(
            r"^\*\*Agent:\*\*.*$",
            f"**Agent:** {agent}",
            content,
            flags=re.MULTILINE,
        )
    if status is not None:
        content = re.sub(
            r"^\*\*Status:\*\*.*$",
            f"**Status:** {status}",
            content,
            flags=re.MULTILINE,
        )
    return content


class AIOfficeHandler(http.server.SimpleHTTPRequestHandler):
    """Extends SimpleHTTPRequestHandler to intercept /api/* routes."""

    # Serve static files from the project root, not cwd
    def translate_path(self, path):
        # Let the parent resolve the path relative to BASE_DIR
        import urllib.parse
        path = urllib.parse.unquote(path)
        # Strip query string
        path = path.split("?", 1)[0].split("#", 1)[0]
        # Normalise
        path = os.path.normpath(path)
        # Join with BASE_DIR instead of os.getcwd()
        return str(BASE_DIR / path.lstrip("/"))

    # ------------------------------------------------------------------
    # CORS helpers
    # ------------------------------------------------------------------

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    # ------------------------------------------------------------------
    # JSON response helpers
    # ------------------------------------------------------------------

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

        if path == "/api/tasks":
            self._handle_get_tasks()
        elif path.startswith("/api/tasks/"):
            filename = path[len("/api/tasks/"):]
            self._handle_get_task_file(filename)
        elif path == "/api/memory":
            self._handle_get_memory()
        elif path == "/api/run/output":
            self._handle_get_run_output()
        elif path == "/api/run/status":
            self._handle_get_run_status()
        else:
            # Fall through to static file serving
            super().do_GET()

    def do_POST(self):
        path = self.path.split("?", 1)[0]

        if path == "/api/tasks":
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
    # API handlers
    # ------------------------------------------------------------------

    def _handle_get_tasks(self):
        result = {}
        for bucket, directory in TASK_DIRS.items():
            directory.mkdir(parents=True, exist_ok=True)
            files = sorted(
                f.name for f in directory.iterdir()
                if f.is_file() and f.name.endswith(".md")
            )
            result[bucket] = files
        self._json_response(result)

    def _handle_get_task_file(self, filename):
        # Prevent path traversal
        if "/" in filename or ".." in filename:
            self._error(400, "Invalid filename")
            return

        bucket, path = find_task(filename)
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

        today = date.today().isoformat()
        slug = slugify(title)
        filename = f"{today}-{slug}.md"

        backlog_dir = TASK_DIRS["backlog"]
        backlog_dir.mkdir(parents=True, exist_ok=True)

        task_path = backlog_dir / filename

        # Build markdown content
        content_lines = [
            f"# {title}",
            "",
            f"**Agent:** {agent}",
            f"**Status:** backlog",
            f"**Created:** {today}",
            "",
        ]
        if description:
            content_lines += ["## Description", "", description, ""]

        task_path.write_text("\n".join(content_lines), encoding="utf-8")

        self._json_response({
            "filename": filename,
            "path": str(task_path.relative_to(BASE_DIR)),
        })

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

        bucket, src_path = find_task(filename)
        if src_path is None:
            self._error(404, "Task not found")
            return

        active_dir = TASK_DIRS["active"]
        active_dir.mkdir(parents=True, exist_ok=True)
        dest_path = active_dir / filename

        # Update fields in markdown before moving
        content = src_path.read_text(encoding="utf-8")
        content = update_markdown_fields(content, agent=agent, status="active")

        dest_path.write_text(content, encoding="utf-8")
        if src_path != dest_path:
            src_path.unlink()

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

        bucket, src_path = find_task(filename)
        if src_path is None:
            self._error(404, "Task not found")
            return

        completed_dir = TASK_DIRS["completed"]
        completed_dir.mkdir(parents=True, exist_ok=True)
        dest_path = completed_dir / filename

        content = src_path.read_text(encoding="utf-8")
        content = update_markdown_fields(content, status="completed")

        dest_path.write_text(content, encoding="utf-8")
        if src_path != dest_path:
            src_path.unlink()

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

        # Task must be in active/
        active_path = TASK_DIRS["active"] / filename
        if not active_path.exists():
            self._error(400, f"Task not found in active/: {filename}")
            return

        # Build the prompt that claude will receive
        prompt = (
            f"You are the {agent} agent in the ai-office multi-agent framework.\n\n"
            "Your job: complete the task assigned to you.\n\n"
            "Steps to follow:\n"
            "1. Read the file CLAUDE.md for your session protocol\n"
            f"2. Read agents/{agent}.md for your full role definition and behavior rules\n"
            f"3. Read the task file at tasks/active/{filename} carefully\n"
            "4. Complete the task as described — write code, research, plan, or write as your role requires\n"
            "5. After completing the work, update memory/team_memory.md and memory/team_memory.json "
            "with a note under Agent Notes\n"
            f"6. Move the task file to tasks/completed/ by updating its Status field and saving it "
            "there, then deleting it from tasks/active/\n\n"
            "Work autonomously. Use your tools. Complete the task fully."
        )

        # Spawn claude subprocess, capturing stdout+stderr together
        proc = subprocess.Popen(
            ["claude", "--print", prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=str(BASE_DIR),
        )

        running_tasks[filename] = {
            "process": proc,
            "output": [],
            "done": False,
            "agent": agent,
        }

        # Background thread reads output line-by-line until the process exits
        def _reader(fname, p):
            try:
                for line in p.stdout:
                    try:
                        running_tasks[fname]["output"].append(line.rstrip("\n"))
                    except UnicodeDecodeError:
                        # Skip lines that can't be decoded
                        pass
            finally:
                p.wait()
                running_tasks[fname]["done"] = True

        t = threading.Thread(target=_reader, args=(filename, proc), daemon=True)
        t.start()

        self._json_response({"ok": True, "task_id": filename})

    def _handle_get_run_output(self):
        import urllib.parse
        qs = urllib.parse.parse_qs(self.path.split("?", 1)[1] if "?" in self.path else "")
        task_id = (qs.get("task_id") or [""])[0]

        if task_id not in running_tasks:
            self._json_response({"lines": [], "done": False})
            return

        entry = running_tasks[task_id]
        self._json_response({
            "lines": list(entry["output"]),
            "done": entry["done"],
        })

    def _handle_get_run_status(self):
        running = []
        done = []
        for fname, entry in running_tasks.items():
            if entry["done"]:
                done.append(fname)
            else:
                running.append(fname)
        self._json_response({"running": running, "done": done})

    def _handle_get_memory(self):
        if not MEMORY_FILE.exists():
            self._error(404, "team_memory.json not found")
            return
        try:
            data = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
            self._json_response(data)
        except (json.JSONDecodeError, IOError) as e:
            self._error(500, str(e))

    # ------------------------------------------------------------------
    # Suppress noisy default logging (keep it clean)
    # ------------------------------------------------------------------

    def log_message(self, format, *args):
        # Only log API requests, suppress static file noise
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
