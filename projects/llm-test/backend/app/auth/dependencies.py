"""
FastAPI dependency injection for JWT authentication.

Flow:
1. Client sends `Authorization: Bearer <supabase_jwt>` header
2. We verify the JWT signature against the Supabase JWT secret
3. We extract the user ID (sub claim) and inject it into the request context
4. We look up the user's team membership and inject team_id

Key compliance notes (bjorn architecture / magnus compliance):
- NEVER use the service role key in user-facing routes (bjorn constraint)
- Update last_active_at on every authenticated request (magnus E2)
- Immediate revocation check: if user has no active team membership, reject (magnus E3)
"""

import uuid
from datetime import datetime, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.models import TeamMember, User

bearer_scheme = HTTPBearer(auto_error=True)


class AuthContext:
    """Injected into every authenticated route handler."""

    def __init__(
        self,
        user_id: uuid.UUID,
        email: str,
        team_id: uuid.UUID,
        role: str,
    ) -> None:
        self.user_id = user_id
        self.email = email
        self.team_id = team_id
        self.role = role

    @property
    def is_owner(self) -> bool:
        return self.role == "owner"

    @property
    def is_admin_or_owner(self) -> bool:
        return self.role in ("owner", "admin")


def _decode_supabase_jwt(token: str) -> dict:
    """Decode and verify a Supabase-issued JWT."""
    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            options={"verify_exp": True},
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def _get_or_create_user(
    db: AsyncSession, user_id: uuid.UUID, email: str
) -> User:
    """Upsert a minimal user record from the JWT claims."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(id=user_id, email=email)
        db.add(user)
        await db.flush()
    return user


async def get_current_user_and_team(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AuthContext:
    """
    Primary auth dependency. Validates JWT, injects AuthContext with team_id.

    team_id must be passed as the `X-Team-Id` request header. Multi-team users
    select their active workspace per request; the header makes the selection explicit.
    """
    payload = _decode_supabase_jwt(credentials.credentials)

    raw_user_id = payload.get("sub")
    email = payload.get("email", "")
    if not raw_user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    user_id = uuid.UUID(raw_user_id)

    # Resolve team_id from header
    team_id_header = request.headers.get("X-Team-Id")
    if not team_id_header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Team-Id header is required",
        )
    try:
        team_id = uuid.UUID(team_id_header)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid X-Team-Id")

    # Verify membership (magnus E3: immediate revocation = no membership record = no access)
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.user_id == user_id,
            TeamMember.team_id == team_id,
        )
    )
    membership = result.scalar_one_or_none()
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this team",
        )

    # Update last_active_at (magnus E2: team owners can see last-active timestamps)
    await db.execute(
        update(TeamMember)
        .where(TeamMember.user_id == user_id, TeamMember.team_id == team_id)
        .values(last_active_at=datetime.now(timezone.utc))
    )
    await db.commit()

    return AuthContext(
        user_id=user_id,
        email=email,
        team_id=team_id,
        role=membership.role,
    )


def require_admin_or_owner(auth: AuthContext) -> AuthContext:
    """Raises 403 if the authenticated user is not admin or owner."""
    if not auth.is_admin_or_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires admin or owner role",
        )
    return auth


def require_owner(auth: AuthContext) -> AuthContext:
    """Raises 403 if the authenticated user is not the team owner."""
    if not auth.is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This action requires owner role",
        )
    return auth


# Convenience type aliases used as Annotated dependencies in router signatures
AuthDep = Annotated[AuthContext, Depends(get_current_user_and_team)]
