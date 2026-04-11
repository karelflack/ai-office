"""
Pydantic v2 schemas for request/response serialisation.
Each router uses a pair: <Resource>Create (request body) and <Resource>Out (response).
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# ---------------------------------------------------------------------------
# Shared
# ---------------------------------------------------------------------------


class OkResponse(BaseModel):
    ok: bool = True
    message: str = "success"


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


class TokenRequest(BaseModel):
    """Exchange a Supabase JWT for a validated session context."""

    supabase_access_token: str = Field(..., min_length=10)


class TokenResponse(BaseModel):
    user_id: uuid.UUID
    email: str
    team_ids: list[uuid.UUID]


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    name: str | None
    created_at: datetime


# ---------------------------------------------------------------------------
# Teams
# ---------------------------------------------------------------------------


class TeamCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    slug: str = Field(..., min_length=2, max_length=100, pattern=r"^[a-z0-9-]+$")
    plan: str = "free"


class TeamUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=255)


class TeamOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    plan: str
    created_at: datetime
    updated_at: datetime


class MemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    team_id: uuid.UUID
    user_id: uuid.UUID
    role: str
    last_active_at: datetime | None
    joined_at: datetime

    # Populated via join when listing members
    email: str | None = None
    name: str | None = None


class InviteRequest(BaseModel):
    email: EmailStr
    role: Literal["admin", "member"] = "member"


class RoleChangeRequest(BaseModel):
    role: Literal["owner", "admin", "member"]


# ---------------------------------------------------------------------------
# Stacks
# ---------------------------------------------------------------------------


class StackCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    ecosystem: str | None = Field(
        None,
        pattern=r"^(npm|pypi|go|maven|cargo|rubygems|mixed)$",
    )
    github_repo_url: str | None = Field(None, max_length=500)


class StackUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    ecosystem: str | None = None
    github_repo_url: str | None = None


class StackOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    team_id: uuid.UUID
    name: str
    description: str | None
    ecosystem: str | None
    github_repo_url: str | None
    last_scanned_at: datetime | None
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------------


class DependencyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    version: str = Field(..., min_length=1, max_length=100)
    ecosystem: str = Field(..., min_length=1, max_length=50)
    manifest_file: str | None = None
    is_dev_dependency: bool = False


class DependencyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    stack_id: uuid.UUID
    name: str
    version: str
    ecosystem: str
    manifest_file: str | None
    is_dev_dependency: bool
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# CVE / Vulnerabilities
# ---------------------------------------------------------------------------


class CveMatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    dependency_id: uuid.UUID
    scan_job_id: uuid.UUID | None
    cve_id: str | None
    osv_id: str
    severity: str | None
    cvss_score: Decimal | None
    summary: str | None
    fixed_in_version: str | None
    scanned_at: datetime


# ---------------------------------------------------------------------------
# Scan Jobs
# ---------------------------------------------------------------------------


class ScanJobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    stack_id: uuid.UUID
    triggered_by: uuid.UUID | None
    status: str
    dependencies_scanned: int
    vulnerabilities_found: int
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime


# ---------------------------------------------------------------------------
# API Keys
# ---------------------------------------------------------------------------


class ApiKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    scope: Literal["read", "write"] = "read"
    expires_at: datetime | None = None


class ApiKeyCreatedOut(BaseModel):
    """Returned ONCE at creation — includes the plaintext key (never shown again)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    scope: str
    key_preview: str
    # Plaintext raw key — caller must save this; it will not be retrievable again
    raw_key: str
    expires_at: datetime | None
    created_at: datetime


class ApiKeyOut(BaseModel):
    """Normal listing — raw key is omitted, only preview shown (magnus C2)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    scope: str
    key_preview: str
    last_used_at: datetime | None
    expires_at: datetime | None
    revoked_at: datetime | None
    created_at: datetime

    @property
    def masked_key(self) -> str:
        return f"sk-...{self.key_preview}"


# ---------------------------------------------------------------------------
# Audit Logs
# ---------------------------------------------------------------------------


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    team_id: uuid.UUID | None
    actor_user_id: uuid.UUID | None
    action: str
    resource_type: str
    resource_id: uuid.UUID | None
    result: str
    metadata: dict | None
    created_at: datetime
    # Raw IP is not exposed in API response — only for internal security team (magnus G1)
