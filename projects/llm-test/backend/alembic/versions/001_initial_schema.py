"""Initial schema — Stackr

Revision ID: 001
Revises:
Create Date: 2026-04-11

Creates all tables matching bjorn's ERD plus the audit_logs table (magnus G1/G2)
and api_keys table (magnus C1-C5).
RLS policies are included as raw SQL — they must be applied against the Supabase
Postgres instance (RLS is enforced at the DB level, not the application level).
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # Custom types
    # ------------------------------------------------------------------
    op.execute(
        "CREATE TYPE team_role AS ENUM ('owner', 'admin', 'member')"
    )
    op.execute(
        "CREATE TYPE stack_ecosystem AS ENUM ('npm', 'pypi', 'go', 'maven', 'cargo', 'rubygems', 'mixed')"
    )
    op.execute(
        "CREATE TYPE scan_job_status AS ENUM ('queued', 'running', 'completed', 'failed')"
    )
    op.execute(
        """CREATE TYPE audit_action AS ENUM (
            'created', 'updated', 'deleted', 'invited', 'removed',
            'key_created', 'key_revoked', 'key_rotated',
            'scan_triggered', 'export_downloaded',
            'login', 'logout', 'login_failed', 'mfa_challenge', 'role_changed'
        )"""
    )
    op.execute(
        """CREATE TYPE audit_resource_type AS ENUM (
            'team', 'stack', 'dependency', 'api_key', 'member', 'scan', 'user'
        )"""
    )
    op.execute("CREATE TYPE api_key_scope AS ENUM ('read', 'write')")

    # ------------------------------------------------------------------
    # Tables
    # ------------------------------------------------------------------

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_table(
        "teams",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("plan", sa.String(50), nullable=False, server_default="free"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_table(
        "team_members",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "team_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("teams.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "role",
            sa.Enum("owner", "admin", "member", name="team_role", create_type=False),
            nullable=False,
            server_default="member",
        ),
        sa.Column("last_active_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "joined_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_team_members_team_user", "team_members", ["team_id", "user_id"], unique=True)

    op.create_table(
        "stacks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "team_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("teams.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column(
            "ecosystem",
            sa.Enum(
                "npm", "pypi", "go", "maven", "cargo", "rubygems", "mixed",
                name="stack_ecosystem",
                create_type=False,
            ),
            nullable=True,
        ),
        sa.Column("github_repo_url", sa.String(500), nullable=True),
        sa.Column("last_scanned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_stacks_team_id", "stacks", ["team_id"])

    op.create_table(
        "dependencies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "stack_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("stacks.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("version", sa.String(100), nullable=False),
        sa.Column("ecosystem", sa.String(50), nullable=False),
        sa.Column("manifest_file", sa.String(255), nullable=True),
        sa.Column("is_dev_dependency", sa.Boolean, nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_dependencies_stack_id", "dependencies", ["stack_id"])

    op.create_table(
        "scan_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "stack_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("stacks.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "triggered_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "queued", "running", "completed", "failed",
                name="scan_job_status",
                create_type=False,
            ),
            nullable=False,
            server_default="queued",
        ),
        sa.Column("dependencies_scanned", sa.Integer, nullable=False, server_default="0"),
        sa.Column("vulnerabilities_found", sa.Integer, nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_scan_jobs_stack_id", "scan_jobs", ["stack_id"])

    op.create_table(
        "cve_matches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "dependency_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("dependencies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "scan_job_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("scan_jobs.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("cve_id", sa.String(100), nullable=True),
        sa.Column("osv_id", sa.String(100), nullable=False),
        sa.Column("severity", sa.String(20), nullable=True),
        sa.Column("cvss_score", sa.Numeric(4, 1), nullable=True),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("fixed_in_version", sa.String(100), nullable=True),
        sa.Column(
            "scanned_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_cve_matches_dependency_id", "cve_matches", ["dependency_id"])
    op.create_index("ix_cve_matches_scan_job_id", "cve_matches", ["scan_job_id"])

    op.create_table(
        "api_keys",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "team_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("teams.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("key_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("key_encrypted", sa.Text, nullable=False),
        sa.Column("key_preview", sa.String(10), nullable=False),
        sa.Column(
            "scope",
            sa.Enum("read", "write", name="api_key_scope", create_type=False),
            nullable=False,
            server_default="read",
        ),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "team_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("teams.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "actor_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("actor_ip", sa.String(50), nullable=True),
        sa.Column("actor_ip_hashed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column(
            "action",
            sa.Enum(
                "created", "updated", "deleted", "invited", "removed",
                "key_created", "key_revoked", "key_rotated",
                "scan_triggered", "export_downloaded",
                "login", "logout", "login_failed", "mfa_challenge", "role_changed",
                name="audit_action",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "resource_type",
            sa.Enum(
                "team", "stack", "dependency", "api_key", "member", "scan", "user",
                name="audit_resource_type",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("result", sa.String(10), nullable=False),
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_audit_logs_team_id", "audit_logs", ["team_id"])
    op.create_index("ix_audit_logs_actor_user_id", "audit_logs", ["actor_user_id"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])

    # ------------------------------------------------------------------
    # RLS Policies (Supabase / Postgres)
    # Enable RLS on all tenant-owned tables; Supabase JWT auth.uid() resolves
    # the current user from the JWT sub claim.
    # ------------------------------------------------------------------
    tables_with_rls = ["stacks", "dependencies", "scan_jobs", "cve_matches", "audit_logs", "api_keys"]
    for tbl in tables_with_rls:
        op.execute(f"ALTER TABLE {tbl} ENABLE ROW LEVEL SECURITY")

    # stacks — members of the owning team can access
    op.execute(
        """
        CREATE POLICY "team members can access their stacks"
        ON stacks FOR ALL
        USING (
            team_id IN (
                SELECT team_id FROM team_members
                WHERE user_id = auth.uid()
            )
        )
        """
    )

    # dependencies — via stack's team membership
    op.execute(
        """
        CREATE POLICY "team members can access stack dependencies"
        ON dependencies FOR ALL
        USING (
            stack_id IN (
                SELECT s.id FROM stacks s
                JOIN team_members tm ON tm.team_id = s.team_id
                WHERE tm.user_id = auth.uid()
            )
        )
        """
    )

    # scan_jobs
    op.execute(
        """
        CREATE POLICY "team members can access scan jobs"
        ON scan_jobs FOR ALL
        USING (
            stack_id IN (
                SELECT s.id FROM stacks s
                JOIN team_members tm ON tm.team_id = s.team_id
                WHERE tm.user_id = auth.uid()
            )
        )
        """
    )

    # cve_matches
    op.execute(
        """
        CREATE POLICY "team members can access cve matches"
        ON cve_matches FOR ALL
        USING (
            dependency_id IN (
                SELECT d.id FROM dependencies d
                JOIN stacks s ON s.id = d.stack_id
                JOIN team_members tm ON tm.team_id = s.team_id
                WHERE tm.user_id = auth.uid()
            )
        )
        """
    )

    # audit_logs — SELECT only for team owners/admins, INSERT only via service role
    op.execute(
        """
        CREATE POLICY "team owners and admins can read audit logs"
        ON audit_logs FOR SELECT
        USING (
            team_id IN (
                SELECT team_id FROM team_members
                WHERE user_id = auth.uid()
                AND role IN ('owner', 'admin')
            )
        )
        """
    )

    # api_keys — owner can see their own keys
    op.execute(
        """
        CREATE POLICY "users can manage their own api keys"
        ON api_keys FOR ALL
        USING (user_id = auth.uid())
        """
    )


def downgrade() -> None:
    # Drop tables in reverse dependency order
    op.execute("DROP POLICY IF EXISTS \"users can manage their own api keys\" ON api_keys")
    op.execute("DROP POLICY IF EXISTS \"team owners and admins can read audit logs\" ON audit_logs")
    op.execute("DROP POLICY IF EXISTS \"team members can access cve matches\" ON cve_matches")
    op.execute("DROP POLICY IF EXISTS \"team members can access scan jobs\" ON scan_jobs")
    op.execute("DROP POLICY IF EXISTS \"team members can access stack dependencies\" ON dependencies")
    op.execute("DROP POLICY IF EXISTS \"team members can access their stacks\" ON stacks")

    op.drop_table("audit_logs")
    op.drop_table("api_keys")
    op.drop_table("cve_matches")
    op.drop_table("scan_jobs")
    op.drop_table("dependencies")
    op.drop_table("stacks")
    op.drop_table("team_members")
    op.drop_table("teams")
    op.drop_table("users")

    op.execute("DROP TYPE IF EXISTS audit_resource_type")
    op.execute("DROP TYPE IF EXISTS audit_action")
    op.execute("DROP TYPE IF EXISTS scan_job_status")
    op.execute("DROP TYPE IF EXISTS stack_ecosystem")
    op.execute("DROP TYPE IF EXISTS team_role")
    op.execute("DROP TYPE IF EXISTS api_key_scope")
