"""
Dependencies router — /stacks/{stack_id}/dependencies

Add, list, and remove dependencies for a stack.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import AuthDep
from app.database import get_db
from app.models.models import Dependency, Stack
from app.schemas.schemas import DependencyCreate, DependencyOut, OkResponse
from app.services.audit import get_client_ip, log_event

router = APIRouter(tags=["dependencies"])


async def _assert_stack_access(stack_id: uuid.UUID, team_id: uuid.UUID, db: AsyncSession) -> Stack:
    result = await db.execute(
        select(Stack).where(Stack.id == stack_id, Stack.team_id == team_id)
    )
    stack = result.scalar_one_or_none()
    if stack is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stack not found")
    return stack


@router.get("/stacks/{stack_id}/dependencies", response_model=list[DependencyOut])
async def list_dependencies(
    stack_id: uuid.UUID,
    auth: AuthDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[DependencyOut]:
    await _assert_stack_access(stack_id, auth.team_id, db)

    result = await db.execute(
        select(Dependency)
        .where(Dependency.stack_id == stack_id)
        .order_by(Dependency.name)
    )
    deps = result.scalars().all()
    return [DependencyOut.model_validate(d) for d in deps]


@router.post(
    "/stacks/{stack_id}/dependencies",
    response_model=DependencyOut,
    status_code=status.HTTP_201_CREATED,
)
async def add_dependency(
    stack_id: uuid.UUID,
    body: DependencyCreate,
    auth: AuthDep,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DependencyOut:
    await _assert_stack_access(stack_id, auth.team_id, db)

    dep = Dependency(
        id=uuid.uuid4(),
        stack_id=stack_id,
        name=body.name,
        version=body.version,
        ecosystem=body.ecosystem,
        manifest_file=body.manifest_file,
        is_dev_dependency=body.is_dev_dependency,
    )
    db.add(dep)

    await log_event(
        db,
        action="created",
        resource_type="dependency",
        resource_id=dep.id,
        team_id=auth.team_id,
        actor_user_id=auth.user_id,
        actor_ip=get_client_ip(dict(request.headers)),
        metadata={"name": body.name, "version": body.version},
    )
    await db.commit()
    await db.refresh(dep)
    return DependencyOut.model_validate(dep)


@router.delete("/stacks/{stack_id}/dependencies/{dep_id}", response_model=OkResponse)
async def remove_dependency(
    stack_id: uuid.UUID,
    dep_id: uuid.UUID,
    auth: AuthDep,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OkResponse:
    await _assert_stack_access(stack_id, auth.team_id, db)

    result = await db.execute(
        select(Dependency).where(Dependency.id == dep_id, Dependency.stack_id == stack_id)
    )
    dep = result.scalar_one_or_none()
    if dep is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dependency not found")

    await db.delete(dep)

    await log_event(
        db,
        action="deleted",
        resource_type="dependency",
        resource_id=dep_id,
        team_id=auth.team_id,
        actor_user_id=auth.user_id,
        actor_ip=get_client_ip(dict(request.headers)),
        metadata={"name": dep.name},
    )
    await db.commit()
    return OkResponse(message="Dependency removed")


@router.get("/dependencies/{dep_id}/cves", response_model=list)
async def get_dependency_cves(
    dep_id: uuid.UUID,
    auth: AuthDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list:
    """
    CVEs for a specific dependency (cross-stack convenience endpoint).
    Verifies team access via the dependency's stack.
    """
    from app.models.models import CveMatch

    # Verify the dependency belongs to the team via its stack
    result = await db.execute(
        select(Dependency)
        .join(Stack, Stack.id == Dependency.stack_id)
        .where(Dependency.id == dep_id, Stack.team_id == auth.team_id)
    )
    dep = result.scalar_one_or_none()
    if dep is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dependency not found")

    from app.schemas.schemas import CveMatchOut

    cve_result = await db.execute(
        select(CveMatch)
        .where(CveMatch.dependency_id == dep_id)
        .order_by(CveMatch.scanned_at.desc())
    )
    cves = cve_result.scalars().all()
    return [CveMatchOut.model_validate(c) for c in cves]
