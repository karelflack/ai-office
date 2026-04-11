#!/usr/bin/env python3
"""MCP server exposing a web_search tool backed by the Perplexity API."""

import json
import os
import urllib.request
import urllib.error

import mcp.server.stdio
import mcp.types as types
from mcp.server import Server

API_KEY = os.environ.get("PERPLEXITY_API_KEY", "")
API_URL = "https://api.perplexity.ai/chat/completions"
MODEL   = "sonar"

server = Server("perplexity-search")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="web_search",
            description=(
                "Search the web for current information using Perplexity. "
                "Use this for market research, competitor analysis, pricing data, "
                "current events, technical documentation, or anything that may have "
                "changed since the model's training cutoff."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query",
                    }
                },
                "required": ["query"],
            },
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name != "web_search":
        raise ValueError(f"Unknown tool: {name}")

    query = arguments.get("query", "").strip()
    if not query:
        return [types.TextContent(type="text", text="Error: empty query")]

    if not API_KEY:
        return [types.TextContent(type="text", text="Error: PERPLEXITY_API_KEY not set")]

    payload = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": query}],
        "return_citations": True,
    }).encode("utf-8")

    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return [types.TextContent(type="text", text=f"Perplexity API error {e.code}: {body}")]
    except Exception as e:
        return [types.TextContent(type="text", text=f"Request failed: {e}")]

    content = data.get("choices", [{}])[0].get("message", {}).get("content", "No result")

    # Append citations if present
    citations = data.get("citations", [])
    if citations:
        content += "\n\n**Sources:**\n" + "\n".join(f"- {c}" for c in citations)

    return [types.TextContent(type="text", text=content)]


if __name__ == "__main__":
    import asyncio
    asyncio.run(mcp.server.stdio.run_forever(server))
