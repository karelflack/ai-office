"""
SQLAlchemy models matching bjorn's ERD.

Design notes:
- users table mirrors auth.users in Supabase; we store a minimal profile here
  for join queries. The authoritative identity is Supabase Auth.
- All tenant-owned tables include team_id to support RLS policies.
- audit_logs is append-only — no UPDATE or DELETE is allowed by DB policy.
- api_keys stores only the encrypted key value; plaintext is shown once at creation.
"""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

TeamRole = Enum("owner", "admin", "member", name="team_role")
StackEcosystem = Enum(
    "npm", "pypi", "go", "maven", "cargo", "rubygems", "mixed", name="stack_ecosystem"
)
ScanJobStatus = Enum("queued", "running", "completed", "failed", name="scan_job_status")
AuditAction = Enum(
    "created",
    "updated",
    "deleted",
    "invited",
    "removed",
    "key_created",
    "key_revoked",
    "key_rotated",
    "scan_triggered",
    "export_downloaded",
    "login",
    "logout",
    "login_failed",
    "mfa_challenge",
    "role_changed",
    name="audit_action",
)
AuditResourceType = Enum(
    "team", "stack", "dependency", "api_key", "member", "scan", "user", name="audit_resource_type"
)
ApiKeyScope = Enum("read", "write", name="api_key_scope")


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class User(Base):
    """
    Mirrors auth.users from Supabase Auth. This table is a local cache of
    minimal profile data needed for joins. The Supabase JWT sub claim is the
    authoritative user ID.
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    team_memberships: Mapped[list["TeamMember"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    scan_jobs: Mapped[list["ScanJob"]] = relationship(back_populates="triggered_by_user")
    api_keys: Mapped[list["ApiKey"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    plan: Mapped[str] = mapped_column(String(50), default="free", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    members: Mapped[list["TeamMember"]] = relationship(
        back_populates="team", cascade="all, delete-orphan"
    )
    stacks: Mapped[list["Stack"]] = relationship(
        back_populates="team", cascade="all, delete-orphan"
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="team")


class TeamMember(Base):
    __tablename__ = "team_members"
    __table_args__ = (
        Index("ix_team_members_team_user", "team_id", "user_id", unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(TeamRole, nullable=False, default="member")
    # last_active_at supports magnus E2 (team owners can see last-active timestamps)
    last_active_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    team: Mapped["Team"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="team_memberships")


class Stack(Base):
    __tablename__ = "stacks"
    __table_args__ = (Index("ix_stacks_team_id", "team_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    ecosystem: Mapped[str | None] = mapped_column(StackEcosystem, nullable=True)
    github_repo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    last_scanned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    team: Mapped["Team"] = relationship(back_populates="stacks")
    dependencies: Mapped[list["Dependency"]] = relationship(
        back_populates="stack", cascade="all, delete-orphan"
    )
    scan_jobs: Mapped[list["ScanJob"]] = relationship(
        back_populates="stack", cascade="all, delete-orphan"
    )


class Dependency(Base):
    __tablename__ = "dependencies"
    __table_args__ = (Index("ix_dependencies_stack_id", "stack_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stack_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stacks.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(100), nullable=False)
    ecosystem: Mapped[str] = mapped_column(String(50), nullable=False)
    manifest_file: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_dev_dependency: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    stack: Mapped["Stack"] = relationship(back_populates="dependencies")
    cve_matches: Mapped[list["CveMatch"]] = relationship(
        back_populates="dependency", cascade="all, delete-orphan"
    )


class CveMatch(Base):
    """
    Append-only per scan. Old records are never deleted — superseded by new
    scan jobs. UI always shows the most recent scan's results.
    """

    __tablename__ = "cve_matches"
    __table_args__ = (
        Index("ix_cve_matches_dependency_id", "dependency_id"),
        Index("ix_cve_matches_scan_job_id", "scan_job_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dependency_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dependencies.id", ondelete="CASCADE"), nullable=False
    )
    scan_job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scan_jobs.id", ondelete="SET NULL"), nullable=True
    )
    cve_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    osv_id: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str | None] = mapped_column(String(20), nullable=True)
    # Numeric type (not text) for sorting — bjorn's architecture note
    cvss_score: Mapped[Decimal | None] = mapped_column(Numeric(4, 1), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    fixed_in_version: Mapped[str | None] = mapped_column(String(100), nullable=True)
    scanned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    dependency: Mapped["Dependency"] = relationship(back_populates="cve_matches")
    scan_job: Mapped["ScanJob"] = relationship(back_populates="cve_matches")


class ScanJob(Base):
    __tablename__ = "scan_jobs"
    __table_args__ = (Index("ix_scan_jobs_stack_id", "stack_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stack_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stacks.id", ondelete="CASCADE"), nullable=False
    )
    triggered_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(ScanJobStatus, default="queued", nullable=False)
    dependencies_scanned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    vulnerabilities_found: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    stack: Mapped["Stack"] = relationship(back_populates="scan_jobs")
    triggered_by_user: Mapped["User | None"] = relationship(back_populates="scan_jobs")
    cve_matches: Mapped[list["CveMatch"]] = relationship(back_populates="scan_job")


class ApiKey(Base):
    """
    Stores encrypted API keys (magnus C1/C2).
    - key_hash: SHA-256 of the raw key — used for lookup on inbound requests
    - key_encrypted: AES-256-GCM encrypted raw key — only decrypted once at creation
    - key_preview: last 6 chars of raw key — shown masked in UI (sk-...abc123)
    - plaintext is NEVER stored; returned once at creation only
    """

    __tablename__ = "api_keys"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    key_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)  # hex SHA-256
    key_encrypted: Mapped[str] = mapped_column(Text, nullable=False)  # base64(iv + ciphertext)
    key_preview: Mapped[str] = mapped_column(String(10), nullable=False)  # last 6 chars
    scope: Mapped[str] = mapped_column(ApiKeyScope, default="read", nullable=False)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="api_keys")

    @property
    def is_active(self) -> bool:
        from datetime import timezone as tz

        if self.revoked_at is not None:
            return False
        if self.expires_at is not None and self.expires_at < datetime.now(tz.utc):
            return False
        return True


class AuditLog(Base):
    """
    Write-once, append-only audit log (magnus G1/G2).
    No UPDATE or DELETE should ever be issued against this table.
    Database-level enforcement via RLS policy: deny UPDATE/DELETE to all roles.
    """

    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_team_id", "team_id"),
        Index("ix_audit_logs_actor_user_id", "actor_user_id"),
        Index("ix_audit_logs_created_at", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("teams.id", ondelete="SET NULL"), nullable=True
    )
    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    # IP hashed after 30 days — store raw here, a scheduled job will hash it
    actor_ip: Mapped[str | None] = mapped_column(String(50), nullable=True)
    actor_ip_hashed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    action: Mapped[str] = mapped_column(AuditAction, nullable=False)
    resource_type: Mapped[str] = mapped_column(AuditResourceType, nullable=False)
    resource_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    result: Mapped[str] = mapped_column(String(10), nullable=False)  # "success" | "failure"
    metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    team: Mapped["Team | None"] = relationship(back_populates="audit_logs")
