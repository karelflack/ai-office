"""Linear issue lifecycle — create, update, comment."""

import json
import os
import threading
import urllib.request
from pathlib import Path

from core.memory import update_project_memory

BASE_DIR = Path(__file__).resolve().parent.parent
_states_cache: dict = {}  # team_id -> {name: state_id}


def api(query: str, variables: dict = None) -> dict:
    """Execute a Linear GraphQL query. Returns data dict or {} on failure."""
    key = os.environ.get("LINEAR_API_KEY", "")
    if not key:
        return {}
    payload = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(
        "https://api.linear.app/graphql",
        data=payload,
        headers={"Authorization": key, "Content-Type": "application/json"},
        method="POST",
    )
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read()).get("data", {})
    except Exception:
        return {}


def get_state_id(state_name: str) -> str | None:
    """Return the workflow state ID for the given name in LINEAR_TEAM_ID, with caching."""
    team_id = os.environ.get("LINEAR_TEAM_ID", "")
    if not team_id:
        return None
    if team_id not in _states_cache:
        data = api(
            """query($teamId: String!) {
                workflowStates(filter: { team: { id: { eq: $teamId } } }) {
                    nodes { id name }
                }
            }""",
            {"teamId": team_id},
        )
        nodes = data.get("workflowStates", {}).get("nodes", [])
        _states_cache[team_id] = {n["name"]: n["id"] for n in nodes}
    states = _states_cache.get(team_id, {})
    return states.get(state_name) or next(
        (v for k, v in states.items() if k.lower() == state_name.lower()), None
    )


def create_issues(slug: str, tasks: list) -> None:
    """Create one Linear issue per task at kickoff. Stores issue URLs in project memory."""
    if not os.environ.get("LINEAR_API_KEY") or not os.environ.get("LINEAR_TEAM_ID"):
        return
    team_id = os.environ["LINEAR_TEAM_ID"]

    def _run():
        issue_map = {}
        for task in tasks:
            agent = task.get("agent", "")
            title = task.get("title", "")
            desc  = task.get("description", "")
            filename = task.get("filename", "")

            data = api(
                """mutation($title: String!, $description: String!, $teamId: String!) {
                    issueCreate(input: { title: $title, description: $description, teamId: $teamId }) {
                        issue { id url }
                    }
                }""",
                {
                    "title": f"[{agent.upper()}] {title}",
                    "description": f"**Project:** {slug}\n**Agent:** {agent}\n\n{desc}",
                    "teamId": team_id,
                },
            )
            issue = data.get("issueCreate", {}).get("issue", {})
            if issue.get("id"):
                issue_map[filename] = {"id": issue["id"], "url": issue["url"]}

        if not issue_map:
            return
        update_project_memory(slug, {"linear_issues": issue_map})

    threading.Thread(target=_run, daemon=True).start()


def update_issue(slug: str, filename: str, state_name: str, comment: str = "") -> None:
    """Move a Linear issue to a new state and optionally add a comment."""
    if not os.environ.get("LINEAR_API_KEY"):
        return

    def _run():
        mem_path = BASE_DIR / "projects" / slug / "memory" / "project_memory.json"
        if not mem_path.exists():
            return
        try:
            m = json.loads(mem_path.read_text(encoding="utf-8"))
            issue_info = m.get("linear_issues", {}).get(filename)
            if not issue_info:
                return
            issue_id = issue_info["id"]
        except Exception:
            return

        state_id = get_state_id(state_name)
        if state_id:
            api(
                """mutation($id: String!, $stateId: String!) {
                    issueUpdate(id: $id, input: { stateId: $stateId }) { success }
                }""",
                {"id": issue_id, "stateId": state_id},
            )
        if comment:
            api(
                """mutation($issueId: String!, $body: String!) {
                    commentCreate(input: { issueId: $issueId, body: $body }) { success }
                }""",
                {"issueId": issue_id, "body": comment},
            )

    threading.Thread(target=_run, daemon=True).start()


def add_pr_comment(slug: str) -> None:
    """After all tasks done, comment the GitHub PR URL on every Linear issue for this project."""
    if not os.environ.get("LINEAR_API_KEY"):
        return

    def _run():
        mem_path = BASE_DIR / "projects" / slug / "memory" / "project_memory.json"
        if not mem_path.exists():
            return
        try:
            m = json.loads(mem_path.read_text(encoding="utf-8"))
        except Exception:
            return

        pr_url = m.get("github_pr", "")
        issue_map = m.get("linear_issues", {})
        if not issue_map:
            return

        comment = f"✅ All AI agents completed.\n\n{f'GitHub PR: {pr_url}' if pr_url else 'No GitHub PR (GITHUB_TOKEN not configured).'}"
        for info in issue_map.values():
            api(
                """mutation($issueId: String!, $body: String!) {
                    commentCreate(input: { issueId: $issueId, body: $body }) { success }
                }""",
                {"issueId": info["id"], "body": comment},
            )

    threading.Thread(target=_run, daemon=True).start()
