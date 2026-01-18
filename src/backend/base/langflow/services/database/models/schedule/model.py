# Path: src/backend/base/langflow/services/database/models/schedule/model.py

from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from pydantic import field_validator
from sqlmodel import Column, Field, JSON, Relationship, SQLModel

if TYPE_CHECKING:
    from langflow.services.database.models.flow.model import Flow
    from langflow.services.database.models.user.model import User


class ScheduleFrequency(str, Enum):
    """Schedule frequency options."""

    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class ScheduleStatus(str, Enum):
    """Schedule status options."""

    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class ScheduleBase(SQLModel):
    """Base schedule model."""

    flow_id: UUID = Field(foreign_key="flow.id", index=True)
    frequency: ScheduleFrequency = Field(default=ScheduleFrequency.ONCE)
    schedule_time: str = Field(description="Time in HH:MM format")
    status: ScheduleStatus = Field(default=ScheduleStatus.ACTIVE)
    
    # For weekly schedules: 0-6 (Monday-Sunday)
    day_of_week: int | None = Field(default=None, nullable=True)
    
    # For monthly schedules: 1-31
    day_of_month: int | None = Field(default=None, nullable=True)
    
    # Custom cron expression for advanced scheduling
    cron_expression: str | None = Field(default=None, nullable=True)
    
    # Last execution details
    last_run_at: datetime | None = Field(default=None, nullable=True)
    next_run_at: datetime | None = Field(default=None, nullable=True)
    
    # Execution results
    last_run_status: str | None = Field(default=None, nullable=True)
    last_run_error: str | None = Field(default=None, nullable=True)
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("schedule_time")
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        """Validate time format is HH:MM."""
        try:
            hour, minute = map(int, v.split(":"))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError
            return v
        except (ValueError, AttributeError):
            raise ValueError("Time must be in HH:MM format (24-hour)")


class Schedule(ScheduleBase, table=True):  # type: ignore[call-arg]
    """Schedule database model."""

    id: UUID = Field(default_factory=uuid4, primary_key=True, unique=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    
    # Relationships
    flow: "Flow" = Relationship()
    user: "User" = Relationship(back_populates="schedules")


class ScheduleCreate(ScheduleBase):
    """Schedule creation model."""

    user_id: UUID | None = Field(default=None, exclude=True)


class ScheduleRead(ScheduleBase):
    """Schedule read model."""

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime


class ScheduleUpdate(SQLModel):
    """Schedule update model."""

    frequency: ScheduleFrequency | None = None
    schedule_time: str | None = None
    status: ScheduleStatus | None = None
    day_of_week: int | None = None
    day_of_month: int | None = None
    cron_expression: str | None = None

    @field_validator("schedule_time")
    @classmethod
    def validate_time_format(cls, v: str | None) -> str | None:
        """Validate time format is HH:MM."""
        if v is None:
            return v
        try:
            hour, minute = map(int, v.split(":"))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError
            return v
        except (ValueError, AttributeError):
            raise ValueError("Time must be in HH:MM format (24-hour)")
