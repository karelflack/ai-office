"""
Stacks router — /stacks

All operations are scoped to auth.team_id — no cross-tenant access possible.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import AuthDep
from app.database import get_db
from app.models.models import Stack
from app.schemas.schemas import OkResponse, StackCreate, StackOut, StackUpdate
from app.services.audit import get_client_ip, log_event

router = APIRouter(prefix="/stacks", tags=["stacks"])


async def _get_stack_for_team(
    stack_id: uuid.UUID, team_id: uuid.UUID, db: AsyncSession
) -> Stack:
    """Load a stack and assert it belongs to the authenticated team."""
    result = await db.execute(
        select(Stack).where(Stack.id == stack_id, Stack.team_id == team_id)
    )
    stack = result.scalar_one_or_none()
    if stack is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stack not found")
    return stack


@router.get("", response_model=list[StackOut])
async def list_stacks(
    auth: AuthDep, db: Annotated[AsyncSession, Depends(get_db)]
) -> list[StackOut]:
    """List all stacks for the authenticated team."""
    result = await db.execute(
        select(Stack).where(Stack.team_id == auth.team_id).order_by(Stack.created_at.desc())
    )
    stacks = result.scalars().all()
    return [StackOut.model_validate(s) for s in stacks]


@router.post("", response_model=StackOut, status_code=status.HTTP_201_CREATED)
async def create_stack(
    body: StackCreate,
    auth: AuthDep,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> StackOut:
    """Create a new stack."""
    stack = Stack(
        id=uuid.uuid4(),
        team_id=auth.team_id,
        name=body.name,
        description=body.description,
        ecosystem=body.ecosystem,
        github_repo_url=body.github_repo_url,
    )
    db.add(stack)
    await db.flush()

    await log_event(
        db,
        action="created",
        resource_type="stack",
        resource_id=stack.id,
        team_id=auth.team_id,
        actor_user_id=auth.user_id,
        actor_ip=get_client_ip(dict(request.headers)),
        metadata={"name": body.name},
    )
    await db.commit()
    await db.refresh(stack)
    return StackOut.model_validate(stack)


@router.get("/{stack_id}", response_model=StackOut)
async def get_stack(
    stack_id: uuid.UUID,
    auth: AuthDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> StackOut:
    stack = await _get_stack_for_team(stack_id, auth.team_id, db)
    return StackOut.model_validate(stack)


@router.patch("/{stack_id}", response_model=StackOut)
async def update_stack(
    stack_id: uuid.UUID,
    body: StackUpdate,
    auth: AuthDep,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> StackOut:
    stack = await _get_stack_for_team(stack_id, auth.team_id, db)

    for field, value in body.model_dump(exclude_none=True).items():
        setattr(stack, field, value)

    await log_event(
        db,
        action="updated",
        resource_type="stack",
        resource_id=stack_id,
        team_id=auth.team_id,
        actor_user_id=auth.user_id,
        actor_ip=get_client_ip(dict(request.headers)),
    )
    await db.commit()
    await db.refresh(stack)
    return StackOut.model_validate(stack)


@router.delete("/{stack_id}", response_model=OkResponse)
async def delete_stack(
    stack_id: uuid.UUID,
    auth: AuthDep,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OkResponse:
    stack = await _get_stack_for_team(stack_id, auth.team_id, db)
    await db.delete(stack)

    await log_event(
        db,
        action="deleted",
        resource_type="stack",
        resource_id=stack_id,
        team_id=auth.team_id,
        actor_user_id=auth.user_id,
        actor_ip=get_client_ip(dict(request.headers)),
        metadata={"name": stack.name},
    )
    await db.commit()
    return OkResponse(message="Stack deleted")
