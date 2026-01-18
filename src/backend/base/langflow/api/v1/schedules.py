# Path: src/backend/base/langflow/api/v1/schedules.py

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from langflow.api.utils import CurrentActiveUser, DbSession
from langflow.services.database.models.flow.model import Flow
from langflow.services.database.models.schedule.model import (
    Schedule,
    ScheduleCreate,
    ScheduleRead,
    ScheduleStatus,
    ScheduleUpdate,
)
from langflow.services.scheduler import get_scheduler_service

router = APIRouter(prefix="/schedules", tags=["Schedules"])


@router.post("/", response_model=ScheduleRead, status_code=201)
async def create_schedule(
    *,
    session: DbSession,
    schedule: ScheduleCreate,
    current_user: CurrentActiveUser,
):
    """Create a new workflow schedule.
    
    Args:
        session: Database session
        schedule: Schedule data
        current_user: Current authenticated user
        
    Returns:
        Created schedule
    """
    # Verify the flow exists and belongs to the user
    flow = (
        await session.exec(
            select(Flow).where(Flow.id == schedule.flow_id).where(Flow.user_id == current_user.id)
        )
    ).first()
    
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found or access denied")
    
    # Create schedule
    schedule.user_id = current_user.id
    db_schedule = Schedule.model_validate(schedule, from_attributes=True)
    session.add(db_schedule)
    await session.commit()
    await session.refresh(db_schedule)
    
    # Add to scheduler if active
    scheduler = get_scheduler_service()
    await scheduler.add_schedule_job(db_schedule)
    
    return ScheduleRead.model_validate(db_schedule, from_attributes=True)


@router.get("/", response_model=list[ScheduleRead])
async def get_schedules(
    *,
    session: DbSession,
    current_user: CurrentActiveUser,
    flow_id: UUID | None = None,
):
    """Get all schedules for the current user.
    
    Args:
        session: Database session
        current_user: Current authenticated user
        flow_id: Optional flow ID to filter schedules
        
    Returns:
        List of schedules
    """
    stmt = select(Schedule).where(Schedule.user_id == current_user.id)
    
    if flow_id:
        stmt = stmt.where(Schedule.flow_id == flow_id)
    
    schedules = (await session.exec(stmt)).all()
    return [ScheduleRead.model_validate(schedule, from_attributes=True) for schedule in schedules]


@router.get("/{schedule_id}", response_model=ScheduleRead)
async def get_schedule(
    *,
    session: DbSession,
    schedule_id: UUID,
    current_user: CurrentActiveUser,
):
    """Get a specific schedule.
    
    Args:
        session: Database session
        schedule_id: Schedule ID
        current_user: Current authenticated user
        
    Returns:
        Schedule details
    """
    schedule = (
        await session.exec(
            select(Schedule).where(Schedule.id == schedule_id).where(Schedule.user_id == current_user.id)
        )
    ).first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    return ScheduleRead.model_validate(schedule, from_attributes=True)


@router.patch("/{schedule_id}", response_model=ScheduleRead)
async def update_schedule(
    *,
    session: DbSession,
    schedule_id: UUID,
    schedule_update: ScheduleUpdate,
    current_user: CurrentActiveUser,
):
    """Update a schedule.
    
    Args:
        session: Database session
        schedule_id: Schedule ID
        schedule_update: Updated schedule data
        current_user: Current authenticated user
        
    Returns:
        Updated schedule
    """
    db_schedule = (
        await session.exec(
            select(Schedule).where(Schedule.id == schedule_id).where(Schedule.user_id == current_user.id)
        )
    ).first()
    
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # Update fields
    update_data = schedule_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_schedule, key, value)
    
    session.add(db_schedule)
    await session.commit()
    await session.refresh(db_schedule)
    
    # Update scheduler job
    scheduler = get_scheduler_service()
    await scheduler.add_schedule_job(db_schedule)
    
    return ScheduleRead.model_validate(db_schedule, from_attributes=True)


@router.delete("/{schedule_id}", status_code=204)
async def delete_schedule(
    *,
    session: DbSession,
    schedule_id: UUID,
    current_user: CurrentActiveUser,
):
    """Delete a schedule.
    
    Args:
        session: Database session
        schedule_id: Schedule ID
        current_user: Current authenticated user
    """
    schedule = (
        await session.exec(
            select(Schedule).where(Schedule.id == schedule_id).where(Schedule.user_id == current_user.id)
        )
    ).first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # Remove from scheduler
    scheduler = get_scheduler_service()
    await scheduler.remove_schedule_job(str(schedule_id))
    
    await session.delete(schedule)
    await session.commit()


@router.post("/{schedule_id}/pause", response_model=ScheduleRead)
async def pause_schedule(
    *,
    session: DbSession,
    schedule_id: UUID,
    current_user: CurrentActiveUser,
):
    """Pause a schedule.
    
    Args:
        session: Database session
        schedule_id: Schedule ID
        current_user: Current authenticated user
        
    Returns:
        Updated schedule
    """
    schedule = (
        await session.exec(
            select(Schedule).where(Schedule.id == schedule_id).where(Schedule.user_id == current_user.id)
        )
    ).first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    schedule.status = ScheduleStatus.PAUSED
    session.add(schedule)
    await session.commit()
    await session.refresh(schedule)
    
    # Remove from scheduler
    scheduler = get_scheduler_service()
    await scheduler.remove_schedule_job(str(schedule_id))
    
    return ScheduleRead.model_validate(schedule, from_attributes=True)


@router.post("/{schedule_id}/resume", response_model=ScheduleRead)
async def resume_schedule(
    *,
    session: DbSession,
    schedule_id: UUID,
    current_user: CurrentActiveUser,
):
    """Resume a paused schedule.
    
    Args:
        session: Database session
        schedule_id: Schedule ID
        current_user: Current authenticated user
        
    Returns:
        Updated schedule
    """
    schedule = (
        await session.exec(
            select(Schedule).where(Schedule.id == schedule_id).where(Schedule.user_id == current_user.id)
        )
    ).first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    schedule.status = ScheduleStatus.ACTIVE
    session.add(schedule)
    await session.commit()
    await session.refresh(schedule)
    
    # Add to scheduler
    scheduler = get_scheduler_service()
    await scheduler.add_schedule_job(schedule)
    
    return ScheduleRead.model_validate(schedule, from_attributes=True)
