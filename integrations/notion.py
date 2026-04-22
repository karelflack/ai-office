"""Notion page creation — writes a project summary after CI passes."""

import json
import os
import urllib.request
from pathlib import Path

from core import projects as project_mgr
from integrations import n8n

BASE_DIR = Path(__file__).resolve().parent.parent


def write_summary(slug: str) -> None:
    """Write a project summary page to Notion. No-op if NOTION_API_KEY not set."""
    api_key = os.environ.get("NOTION_API_KEY", "")
    db_id = os.environ.get("NOTION_DATABASE_ID", "")
    if not api_key or not db_id:
        return

    try:
        proj = project_mgr.get_project(slug)
        project_name = proj.get("name", slug)
        description  = proj.get("description", "")
    except Exception:
        project_name = slug
        description  = ""

    decisions_dir = BASE_DIR / "projects" / slug / "memory" / "decisions"
    def _read_cat(cat: str) -> str:
        p = decisions_dir / f"{cat}.md"
        try:
            return p.read_text(encoding="utf-8").strip() if p.exists() else ""
        except Exception:
            return ""

    architecture   = _read_cat("architecture")
    implementation = _read_cat("implementation")
    strategy       = _read_cat("strategy")
    compliance     = _read_cat("compliance")

    mem_path = BASE_DIR / "projects" / slug / "memory" / "project_memory.json"
    pr_url = ""
    try:
        m = json.loads(mem_path.read_text(encoding="utf-8"))
        pr_url = m.get("pr_url", "")
    except Exception:
        pass

    def _text_block(content: str, heading: str) -> list:
        """Return a heading + paragraph block(s), chunked to Notion's 2000-char limit."""
        if not content:
            return []
        blocks = [{"object": "block", "type": "heading_2",
                   "heading_2": {"rich_text": [{"type": "text", "text": {"content": heading}}]}}]
        for i in range(0, min(len(content), 10000), 1900):
            chunk = content[i:i + 1900]
            blocks.append({"object": "block", "type": "paragraph",
                           "paragraph": {"rich_text": [{"type": "text", "text": {"content": chunk}}]}})
        return blocks

    children = []
    if description:
        children += [{"object": "block", "type": "paragraph",
                      "paragraph": {"rich_text": [{"type": "text", "text": {"content": description}}]}}]
    if pr_url:
        children += [{"object": "block", "type": "paragraph",
                      "paragraph": {"rich_text": [{"type": "text", "text": {"content": f"GitHub PR: {pr_url}",
                                                   "link": {"url": pr_url}}}]}}]
    children += _text_block(architecture,   "Architecture")
    children += _text_block(strategy,       "Strategy")
    children += _text_block(implementation, "Implementation")
    children += _text_block(compliance,     "Compliance")

    payload = json.dumps({
        "parent": {"database_id": db_id},
        "properties": {
            "title": {"title": [{"type": "text", "text": {"content": project_name}}]}
        },
        "children": children[:100],
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            "https://api.notion.com/v1/pages",
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Notion-Version": "2022-06-28",
            },
            method="POST",
        )
        urllib.request.urlopen(req, timeout=30)
        n8n.notify(slug, "system", "notion-page-created.md", f"Notion page created for {project_name}")
    except Exception:
        pass
