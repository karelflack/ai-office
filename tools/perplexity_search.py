#!/usr/bin/env python3
"""MCP server exposing a web_search tool backed by OpenAI gpt-4o-search-preview."""

import os

import mcp.server.stdio
import mcp.types as types
from mcp.server import Server
from openai import OpenAI

API_KEY = os.environ.get("OPENAI_API_KEY", "")

server = Server("web-search")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="web_search",
            description=(
                "Search the web for current information. "
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
        return [types.TextContent(type="text", text="Error: OPENAI_API_KEY not set")]

    try:
        client = OpenAI(api_key=API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-search-preview",
            messages=[{"role": "user", "content": query}],
        )
        result = response.choices[0].message.content or "No result returned"
    except Exception as e:
        return [types.TextContent(type="text", text=f"Search failed: {e}")]

    return [types.TextContent(type="text", text=result)]


if __name__ == "__main__":
    import asyncio
    asyncio.run(mcp.server.stdio.run_forever(server))
