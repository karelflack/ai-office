"""
Teams router — /teams

Handles team CRUD, member listing, invites, role changes, and member removal.
RBAC is enforced server-side for every mutating operation (magnus E1).
Immediate access revocation on member removal (magnus E3).
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import AuthDep, require_admin_or_owner, require_owner
from app.database import get_db
from app.models.models import Team, TeamMember, User
from app.schemas.schemas import (
    InviteRequest,
    MemberOut,
    OkResponse,
    RoleChangeRequest,
    TeamCreate,
    TeamOut,
    TeamUpdate,
)
from app.services.audit import get_client_ip, log_event

router = APIRouter(prefix="/teams", tags=["teams"])


@router.post("", response_model=TeamOut, status_code=status.HTTP_201_CREATED)
async def create_team(
    body: TeamCreate,
    auth: AuthDep,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TeamOut:
    """Create a new team. The creator becomes the owner."""
    # Check slug uniqueness
    existing = await db.execute(select(Team).where(Team.slug == body.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Team slug already taken"
        )

    team = Team(id=uuid.uuid4(), name=body.name, slug=body.slug, plan=body.plan)
    db.add(team)
    await db.flush()

    membership = TeamMember(
        id=uuid.uuid4(),
        team_id=team.id,
        user_id=auth.user_id,
        role="owner",
    )
    db.add(membership)

    await log_event(
        db,
        action="created",
        resource_type="team",
        resource_id=team.id,
        team_id=team.id,
        actor_user_id=auth.user_id,
        actor_ip=get_client_ip(dict(request.headers)),
        metadata={"slug": body.slug},
    )
    await db.commit()
    await db.refresh(team)
    return TeamOut.model_validate(team)


@router.get("/{team_id}", response_model=TeamOut)
async def get_team(team_id: uuid.UUID, auth: AuthDep, db: Annotated[AsyncSession, Depends(get_db)]) -> TeamOut:
    """Get team details. Auth middleware already verified membership."""
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    return TeamOut.model_validate(team)


@router.patch("/{team_id}", response_model=TeamOut)
async def update_team(
    team_id: uuid.UUID,
    body: TeamUpdate,
    auth: AuthDep,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TeamOut:
    """Update team name. Requires admin or owner role."""
    require_admin_or_owner(auth)

    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    if body.name is not None:
        team.name = body.name

    await log_event(
        db,
        action="updated",
        resource_type="team",
        resource_id=team_id,
        team_id=auth.team_id,
        actor_user_id=auth.user_id,
        actor_ip=get_client_ip(dict(request.headers)),
    )
    await db.commit()
    await db.refresh(team)
    return TeamOut.model_validate(team)


@router.get("/{team_id}/members", response_model=list[MemberOut])
async def list_members(
    team_id: uuid.UUID, auth: AuthDep, db: Annotated[AsyncSession, Depends(get_db)]
) -> list[MemberOut]:
    """
    List team members with last-active timestamps (magnus E2).
    Available to all team members.
    """
    result = await db.execute(
        select(TeamMember, User)
        .join(User, User.id == TeamMember.user_id)
        .where(TeamMember.team_id == team_id)
        .order_by(TeamMember.joined_at)
    )
    rows = result.fetchall()

    members = []
    for membership, user in rows:
        out = MemberOut.model_validate(membership)
        out.email = user.email
        out.name = user.name
        members.append(out)
    return members


@router.post("/{team_id}/invite", response_model=OkResponse, status_code=status.HTTP_201_CREATED)
async def invite_member(
    team_id: uuid.UUID,
    body: InviteRequest,
    auth: AuthDep,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OkResponse:
    """
    Invite a user to the team by email. Requires admin or owner (magnus E1).
    Creates a TeamMember record if the user already exists; otherwise a pending
    invite record would be needed (simplified: user must already exist in users table).
    """
    require_admin_or_owner(auth)

    # Look up target user
    user_result = await db.execute(select(User).where(User.email == body.email))
    target_user = user_result.scalar_one_or_none()
    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. They must sign up before being invited.",
        )

    # Check for existing membership
    existing = await db.execute(
        select(TeamMember).where(
            TeamMember.team_id == team_id, TeamMember.user_id == target_user.id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User is already a team member"
        )

    membership = TeamMember(
        id=uuid.uuid4(),
        team_id=team_id,
        user_id=target_user.id,
        role=body.role,
    )
    db.add(membership)

    await log_event(
        db,
        action="invited",
        resource_type="member",
        resource_id=target_user.id,
        team_id=auth.team_id,
        actor_user_id=auth.user_id,
        actor_ip=get_client_ip(dict(request.headers)),
        metadata={"invited_email": body.email, "role": body.role},
    )
    await db.commit()
    return OkResponse(message=f"Invited {body.email} as {body.role}")


@router.patch("/{team_id}/members/{user_id}/role", response_model=OkResponse)
async def change_member_role(
    team_id: uuid.UUID,
    user_id: uuid.UUID,
    body: RoleChangeRequest,
    auth: AuthDep,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OkResponse:
    """Change a member's role. Requires owner (only owners can grant/revoke admin)."""
    require_owner(auth)

    result = await db.execute(
        select(TeamMember).where(
            TeamMember.team_id == team_id, TeamMember.user_id == user_id
        )
    )
    membership = result.scalar_one_or_none()
    if membership is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

    old_role = membership.role
    membership.role = body.role

    await log_event(
        db,
        action="role_changed",
        resource_type="member",
        resource_id=user_id,
        team_id=auth.team_id,
        actor_user_id=auth.user_id,
        actor_ip=get_client_ip(dict(request.headers)),
        metadata={"old_role": old_role, "new_role": body.role},
    )
    await db.commit()
    return OkResponse(message=f"Role updated to {body.role}")


@router.delete("/{team_id}/members/{user_id}", response_model=OkResponse)
async def remove_member(
    team_id: uuid.UUID,
    user_id: uuid.UUID,
    auth: AuthDep,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OkResponse:
    """
    Remove a member from the team immediately (magnus E3).
    Requires admin or owner. Owners cannot remove themselves.
    """
    require_admin_or_owner(auth)

    if user_id == auth.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot remove yourself from a team",
        )

    result = await db.execute(
        select(TeamMember).where(
            TeamMember.team_id == team_id, TeamMember.user_id == user_id
        )
    )
    membership = result.scalar_one_or_none()
    if membership is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

    # Admins cannot remove owners (magnus E1 — server-side RBAC)
    if membership.role == "owner" and not auth.is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only owners can remove other owners"
        )

    await db.delete(membership)

    await log_event(
        db,
        action="removed",
        resource_type="member",
        resource_id=user_id,
        team_id=auth.team_id,
        actor_user_id=auth.user_id,
        actor_ip=get_client_ip(dict(request.headers)),
        metadata={"removed_user_id": str(user_id)},
    )
    await db.commit()
    return OkResponse(message="Member removed")
