# Path: src/backend/base/langflow/services/scheduler/service.py

import asyncio
from datetime import datetime, time, timedelta, timezone
from typing import TYPE_CHECKING

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from lfx.log.logger import logger
from sqlmodel import select

from langflow.services.database.models.schedule.model import (
    Schedule,
    ScheduleFrequency,
    ScheduleStatus,
)
from langflow.services.deps import get_service, session_scope
from langflow.services.schema import ServiceType

if TYPE_CHECKING:
    from langflow.services.database.models.flow.model import Flow


class SchedulerService:
    """Service for managing workflow schedules using APScheduler."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()
        logger.info("Scheduler service started")

    async def execute_workflow(self, schedule_id: str):
        """Execute a scheduled workflow.
        
        Args:
            schedule_id: The schedule ID to execute
        """
        try:
            async with session_scope() as session:
                # Get schedule
                schedule = (
                    await session.exec(select(Schedule).where(Schedule.id == schedule_id))
                ).first()

                if not schedule or schedule.status != ScheduleStatus.ACTIVE:
                    logger.warning(f"Schedule {schedule_id} not found or not active")
                    return

                # Get flow
                from langflow.services.database.models.flow.model import Flow

                flow = (await session.exec(select(Flow).where(Flow.id == schedule.flow_id))).first()

                if not flow:
                    logger.error(f"Flow {schedule.flow_id} not found for schedule {schedule_id}")
                    schedule.last_run_status = "error"
                    schedule.last_run_error = "Flow not found"
                    schedule.last_run_at = datetime.now(timezone.utc)
                    await session.commit()
                    return

                logger.info(f"Executing scheduled workflow: {flow.name} (Schedule: {schedule_id})")

                # Update schedule
                schedule.last_run_at = datetime.now(timezone.utc)
                schedule.last_run_status = "running"

                try:
                    # Import the flow execution logic
                    from langflow.processing.process import process_graph_cached

                    # Execute the flow
                    result = await process_graph_cached(
                        flow_id=str(flow.id),
                        session=session,
                    )

                    schedule.last_run_status = "success"
                    schedule.last_run_error = None
                    logger.info(f"Successfully executed workflow: {flow.name}")

                except Exception as e:
                    schedule.last_run_status = "failed"
                    schedule.last_run_error = str(e)
                    logger.error(f"Failed to execute workflow {flow.name}: {e}", exc_info=True)

                # Update next run time based on frequency
                if schedule.frequency != ScheduleFrequency.ONCE:
                    schedule.next_run_at = self._calculate_next_run(schedule)
                else:
                    schedule.status = ScheduleStatus.COMPLETED

                await session.commit()

        except Exception as e:
            logger.error(f"Error in execute_workflow: {e}", exc_info=True)

    def _calculate_next_run(self, schedule: Schedule) -> datetime:
        """Calculate the next run time based on frequency.
        
        Args:
            schedule: The schedule to calculate next run for
            
        Returns:
            Next run datetime
        """
        now = datetime.now(timezone.utc)
        hour, minute = map(int, schedule.schedule_time.split(":"))

        if schedule.frequency == ScheduleFrequency.DAILY:
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
            return next_run

        elif schedule.frequency == ScheduleFrequency.WEEKLY:
            days_ahead = (schedule.day_of_week or 0) - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            next_run = now + timedelta(days=days_ahead)
            next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)
            return next_run

        elif schedule.frequency == ScheduleFrequency.MONTHLY:
            day = schedule.day_of_month or 1
            next_run = now.replace(day=day, hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                # Move to next month
                if now.month == 12:
                    next_run = next_run.replace(year=now.year + 1, month=1)
                else:
                    next_run = next_run.replace(month=now.month + 1)
            return next_run

        return now + timedelta(days=1)

    async def add_schedule_job(self, schedule: Schedule):
        """Add a schedule to the job scheduler.
        
        Args:
            schedule: The schedule to add
        """
        if schedule.status != ScheduleStatus.ACTIVE:
            logger.debug(f"Skipping inactive schedule: {schedule.id}")
            return

        job_id = str(schedule.id)

        # Remove existing job if present
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)

        try:
            hour, minute = map(int, schedule.schedule_time.split(":"))

            if schedule.frequency == ScheduleFrequency.ONCE:
                # Schedule for specific datetime
                run_time = datetime.now(timezone.utc).replace(
                    hour=hour, minute=minute, second=0, microsecond=0
                )
                if run_time <= datetime.now(timezone.utc):
                    run_time += timedelta(days=1)

                trigger = DateTrigger(run_date=run_time)

            elif schedule.frequency == ScheduleFrequency.DAILY:
                trigger = CronTrigger(hour=hour, minute=minute)

            elif schedule.frequency == ScheduleFrequency.WEEKLY:
                day_of_week = schedule.day_of_week or 0  # 0 = Monday
                trigger = CronTrigger(day_of_week=day_of_week, hour=hour, minute=minute)

            elif schedule.frequency == ScheduleFrequency.MONTHLY:
                day = schedule.day_of_month or 1
                trigger = CronTrigger(day=day, hour=hour, minute=minute)

            elif schedule.frequency == ScheduleFrequency.CUSTOM and schedule.cron_expression:
                # Use custom cron expression
                trigger = CronTrigger.from_crontab(schedule.cron_expression)

            else:
                logger.warning(f"Unsupported schedule frequency: {schedule.frequency}")
                return

            self.scheduler.add_job(
                self.execute_workflow,
                trigger=trigger,
                args=[str(schedule.id)],
                id=job_id,
                replace_existing=True,
                misfire_grace_time=300,  # 5 minutes grace period
            )

            logger.info(f"Added schedule job: {job_id} ({schedule.frequency})")

        except Exception as e:
            logger.error(f"Failed to add schedule {schedule.id}: {e}", exc_info=True)

    async def remove_schedule_job(self, schedule_id: str):
        """Remove a schedule from the job scheduler.
        
        Args:
            schedule_id: The schedule ID to remove
        """
        job_id = str(schedule_id)
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed schedule job: {job_id}")

    async def load_all_schedules(self):
        """Load all active schedules from database and add them to scheduler."""
        try:
            async with session_scope() as session:
                schedules = (
                    await session.exec(
                        select(Schedule).where(Schedule.status == ScheduleStatus.ACTIVE)
                    )
                ).all()

                for schedule in schedules:
                    await self.add_schedule_job(schedule)

                logger.info(f"Loaded {len(schedules)} active schedules")

        except Exception as e:
            logger.error(f"Failed to load schedules: {e}", exc_info=True)

    def shutdown(self):
        """Shutdown the scheduler."""
        self.scheduler.shutdown()
        logger.info("Scheduler service stopped")


# Singleton instance
_scheduler_service: SchedulerService | None = None


def get_scheduler_service() -> SchedulerService:
    """Get or create the scheduler service instance."""
    global _scheduler_service
    if _scheduler_service is None:
        _scheduler_service = SchedulerService()
    return _scheduler_service
