#!/usr/bin/env python3
"""
AI Office HTTP server.
Serves static files from project root and provides a REST API under /api/.
Run with: python3 server.py
"""

import http.server
import json
import os
import subprocess
import threading
from pathlib import Path

from core import agents as agent_registry
from core import memory as mem
from core import tasks as task_mgr

PORT = 8000
BASE_DIR = Path(__file__).parent.resolve()

# Tracks live subprocess references keyed by filename so we can stream output.
# Run output is also written to runs/<filename>.json for persistence.
_live_procs: dict = {}


class AIOfficeHandler(http.server.SimpleHTTPRequestHandler):
    """Extends SimpleHTTPRequestHandler to intercept /api/* routes."""

    def translate_path(self, path):
        import urllib.parse
        path = urllib.parse.unquote(path)
        path = path.split("?", 1)[0].split("#", 1)[0]
        path = os.path.normpath(path)
        return str(BASE_DIR / path.lstrip("/"))

    # ------------------------------------------------------------------
    # CORS helpers
    # ------------------------------------------------------------------

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    # ------------------------------------------------------------------
    # Response helpers
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
            self._handle_get_task_file(path[len("/api/tasks/"):])
        elif path == "/api/memory":
            self._handle_get_memory()
        elif path == "/api/run/output":
            self._handle_get_run_output()
        elif path == "/api/run/status":
            self._handle_get_run_status()
        else:
            super().do_GET()

    def do_POST(self):
        path = self.path.split("?", 1)[0]

        if path == "/api/login":
            self._handle_post_login()
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
    # API handlers
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

    def _handle_get_tasks(self):
        self._json_response(task_mgr.list_tasks())

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
        self._json_response({
            "filename": filename,
            "path": f"tasks/backlog/{filename}",
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

        proc = subprocess.Popen(
            ["claude", "--print", "--dangerously-skip-permissions",
             "--verbose", "--output-format", "stream-json", prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            text=True,
            cwd=str(BASE_DIR),
        )

        _live_procs[filename] = proc
        mem.write_run(filename, [], False)

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

        def _reader(fname, p):
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
                            mem.write_run(fname, lines, False)
                    except Exception:
                        pass
            finally:
                p.wait()
                mem.write_run(fname, lines, True)
                _live_procs.pop(fname, None)

        threading.Thread(target=_reader, args=(filename, proc), daemon=True).start()
        self._json_response({"ok": True, "task_id": filename})

    def _handle_get_run_output(self):
        import urllib.parse
        qs = urllib.parse.parse_qs(self.path.split("?", 1)[1] if "?" in self.path else "")
        task_id = (qs.get("task_id") or [""])[0]
        self._json_response(mem.read_run(task_id))

    def _handle_get_run_status(self):
        self._json_response(mem.list_runs())

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
