"""
Audit logging service (magnus compliance G1/G2).

Rules:
- Logs are WRITE-ONLY — this module only inserts, never updates or deletes
- actor_ip is stored raw initially; a scheduled job hashes it after 30 days
- Raw IP is never exposed via API (only internal security team access)
- Never log raw API key values, password material, or OAuth tokens
"""

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import AuditLog


async def log_event(
    db: AsyncSession,
    *,
    action: str,
    resource_type: str,
    result: str = "success",
    team_id: uuid.UUID | None = None,
    actor_user_id: uuid.UUID | None = None,
    actor_ip: str | None = None,
    resource_id: uuid.UUID | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    """
    Append a single audit log entry. This is the only function that should
    ever write to the audit_logs table from application code.

    Callers must NOT include raw key values, passwords, or tokens in metadata.
    """
    entry = AuditLog(
        id=uuid.uuid4(),
        team_id=team_id,
        actor_user_id=actor_user_id,
        actor_ip=actor_ip,
        actor_ip_hashed=False,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        result=result,
        metadata=metadata,
    )
    db.add(entry)
    # Do not commit here — caller commits their transaction; the log entry is
    # part of the same atomic operation so it rolls back on failure.
    await db.flush()


def get_client_ip(request_headers: dict) -> str | None:
    """Extract client IP from request. Prefer X-Forwarded-For (Railway proxy)."""
    forwarded = request_headers.get("x-forwarded-for")
    if forwarded:
        # Take the first (client) IP from the chain
        return forwarded.split(",")[0].strip()
    return request_headers.get("x-real-ip")
