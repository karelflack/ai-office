"""
Auth router — /auth

Handles:
- POST /auth/token  : validate a Supabase JWT and return session context
- POST /auth/me     : return the current user's profile
"""

import uuid
from typing import Annotated

import jwt as pyjwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import AuthDep, _decode_supabase_jwt, _get_or_create_user
from app.database import get_db
from app.models.models import TeamMember, User
from app.schemas.schemas import TokenRequest, TokenResponse, UserOut
from app.services.audit import get_client_ip, log_event

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=TokenResponse)
async def exchange_token(
    body: TokenRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """
    Validate a Supabase access token and return the user's team memberships.
    Clients call this after Supabase Auth login to discover their workspace context.
    """
    payload = _decode_supabase_jwt(body.supabase_access_token)

    raw_user_id = payload.get("sub")
    email = payload.get("email", "")
    if not raw_user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = uuid.UUID(raw_user_id)
    user = await _get_or_create_user(db, user_id, email)

    # Collect team memberships
    result = await db.execute(
        select(TeamMember.team_id).where(TeamMember.user_id == user_id)
    )
    team_ids = [row[0] for row in result.fetchall()]

    await log_event(
        db,
        action="login",
        resource_type="user",
        resource_id=user_id,
        actor_user_id=user_id,
        actor_ip=get_client_ip(dict(request.headers)),
        metadata={"email": email},
    )
    await db.commit()

    return TokenResponse(user_id=user_id, email=email, team_ids=team_ids)


@router.get("/me", response_model=UserOut)
async def get_me(auth: AuthDep, db: Annotated[AsyncSession, Depends(get_db)]) -> UserOut:
    """Return the authenticated user's profile."""
    result = await db.execute(select(User).where(User.id == auth.user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserOut.model_validate(user)
