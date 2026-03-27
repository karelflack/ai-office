import os
import json
import asyncio
from typing import Optional, Callable
import anthropic

client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))

WORKER_PROFILES = {
    "alice": {"name": "Alice", "color": "#4ecdc4", "specialty": "web research and fact-finding"},
    "bob":   {"name": "Bob",   "color": "#ff6b6b", "specialty": "writing and summarizing"},
    "carol": {"name": "Carol", "color": "#ffd93d", "specialty": "analysis and reasoning"},
    "dave":  {"name": "Dave",  "color": "#6bcb77", "specialty": "code and technical tasks"},
    "eve":   {"name": "Eve",   "color": "#a855f7", "specialty": "planning and organizing"},
}

MOCK_MODE = not bool(os.getenv("ANTHROPIC_API_KEY", ""))


async def call_claude(system: str, user: str) -> str:
    if MOCK_MODE:
        await asyncio.sleep(1.5)
        return f"[MOCK] Response to: {user[:60]}..."
    resp = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return resp.content[0].text


async def boss_breakdown(task: str, broadcast: Callable) -> list[dict]:
    """Boss agent breaks down a task into subtasks for workers."""
    await broadcast({"type": "boss_state", "state": "thinking", "message": f"Breaking down: {task[:80]}..."})

    system = """You are a boss agent managing a small team.
Break the user's request into 2-4 subtasks, each suited to a specialist.
Respond ONLY with valid JSON — an array of objects like:
[{"worker": "alice", "task": "specific task description"}, ...]
Available workers and specialties:
- alice: web research and fact-finding
- bob: writing and summarizing
- carol: analysis and reasoning
- dave: code and technical tasks
- eve: planning and organizing
Pick the best workers for the job. Use 2-4 workers total."""

    raw = await call_claude(system, task)

    try:
        start = raw.find("[")
        end = raw.rfind("]") + 1
        assignments = json.loads(raw[start:end])
    except Exception:
        assignments = [{"worker": "alice", "task": task}]

    await broadcast({"type": "boss_state", "state": "assigning", "message": f"Assigning {len(assignments)} tasks..."})
    return assignments


async def worker_execute(worker_id: str, task: str, broadcast: Callable) -> str:
    """Worker agent executes its assigned task."""
    profile = WORKER_PROFILES.get(worker_id, {"name": worker_id, "specialty": "general"})
    needs_web = any(w in task.lower() for w in ["search", "find", "look up", "research", "web", "internet", "latest", "current"])

    # Walk to boss to receive task
    await broadcast({"type": "agent_state", "id": worker_id, "state": "walking_to_boss", "task": task})
    await asyncio.sleep(1.2)
    await broadcast({"type": "agent_state", "id": worker_id, "state": "receiving_task", "task": task})
    await asyncio.sleep(0.8)

    # Walk to workbench
    await broadcast({"type": "agent_state", "id": worker_id, "state": "walking_to_bench", "task": task})
    await asyncio.sleep(1.0)

    # Start working
    work_state = "outside" if needs_web else "working"
    await broadcast({"type": "agent_state", "id": worker_id, "state": work_state, "task": task})

    system = f"""You are {profile['name']}, a specialist in {profile['specialty']}.
Complete the assigned task thoroughly but concisely. Max 150 words."""

    result = await call_claude(system, task)

    # Walk back to boss to report
    await broadcast({"type": "agent_state", "id": worker_id, "state": "returning", "task": task})
    await asyncio.sleep(1.0)
    await broadcast({"type": "agent_state", "id": worker_id, "state": "reporting", "task": task, "result": result})
    return result


async def boss_synthesize(original_task: str, results: list[dict], broadcast: Callable) -> str:
    """Boss synthesizes all worker results into a final answer."""
    await broadcast({"type": "boss_state", "state": "synthesizing", "message": "Reading reports from the team..."})

    parts = "\n\n".join(f"[{r['worker'].upper()}]: {r['result']}" for r in results)
    system = """You are a boss agent. Your team has completed their subtasks.
Synthesize their reports into one clear, helpful final answer. Be concise."""

    final = await call_claude(system, f"Original request: {original_task}\n\nTeam reports:\n{parts}")

    await broadcast({"type": "boss_state", "state": "done", "message": "Task complete."})
    await broadcast({"type": "final_answer", "text": final})
    return final


async def run_office_task(task: str, broadcast: Callable):
    """Full pipeline: boss assigns → workers execute → boss synthesizes."""
    try:
        assignments = await boss_breakdown(task, broadcast)

        worker_tasks = []
        for a in assignments:
            worker_id = a.get("worker", "alice")
            worker_tasks.append(worker_execute(worker_id, a["task"], broadcast))

        results_raw = await asyncio.gather(*worker_tasks, return_exceptions=True)

        results = []
        for i, r in enumerate(results_raw):
            worker_id = assignments[i].get("worker", "alice")
            if isinstance(r, Exception):
                results.append({"worker": worker_id, "result": f"Error: {r}"})
            else:
                results.append({"worker": worker_id, "result": r})
            await broadcast({"type": "agent_state", "id": worker_id, "state": "idle"})

        final = await boss_synthesize(task, results, broadcast)
        await broadcast({"type": "boss_state", "state": "idle", "message": ""})
        return final

    except Exception as e:
        await broadcast({"type": "error", "message": str(e)})
        raise
