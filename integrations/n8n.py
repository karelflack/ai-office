"""n8n webhook bridge for Slack notifications."""

import json
import os
import urllib.request

DEFAULT_URL = "http://localhost:5678/webhook/agent-complete"


def notify(slug: str, agent: str, filename: str, status: str) -> None:
    """Fire n8n webhook when an agent finishes. Non-blocking, errors are silent."""
    url = os.environ.get("N8N_WEBHOOK_URL", DEFAULT_URL)
    try:
        task_title = filename.replace(".md", "").split("-", 3)[-1].replace("-", " ").title()
        payload = json.dumps({
            "project": slug,
            "agent": agent.capitalize(),
            "task": task_title,
            "status": status,
            "file": filename,
        }).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=3)
    except Exception:
        pass
