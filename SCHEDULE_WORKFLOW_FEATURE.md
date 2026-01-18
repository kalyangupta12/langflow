# Workflow Scheduling Feature

## Overview

The workflow scheduling feature allows users to schedule workflows to run automatically at specified times and frequencies.

## Backend Implementation

### Database Model
- **Location**: `src/backend/base/langflow/services/database/models/schedule/model.py`
- **Table**: `schedule`
- **Fields**:
  - `id`: UUID primary key
  - `flow_id`: Foreign key to flow table
  - `user_id`: Foreign key to user table
  - `frequency`: Enum (once, daily, weekly, monthly, custom)
  - `schedule_time`: Time in HH:MM format (24-hour)
  - `status`: Enum (active, paused, completed, failed)
  - `day_of_week`: For weekly schedules (0-6, Monday-Sunday)
  - `day_of_month`: For monthly schedules (1-31)
  - `cron_expression`: For custom schedules
  - `last_run_at`, `next_run_at`: Execution tracking
  - `last_run_status`, `last_run_error`: Result tracking
  - `created_at`, `updated_at`: Timestamps

### API Endpoints
- **Location**: `src/backend/base/langflow/api/v1/schedules.py`
- **Routes**:
  - `POST /api/v1/schedules/` - Create a new schedule
  - `GET /api/v1/schedules/` - List all schedules for current user
  - `GET /api/v1/schedules/{schedule_id}` - Get schedule details
  - `PATCH /api/v1/schedules/{schedule_id}` - Update schedule
  - `DELETE /api/v1/schedules/{schedule_id}` - Delete schedule
  - `POST /api/v1/schedules/{schedule_id}/pause` - Pause schedule
  - `POST /api/v1/schedules/{schedule_id}/resume` - Resume schedule

### Database Migration
- **Location**: `src/backend/base/langflow/alembic/versions/add_schedule_table.py`
- **Run Migration**:
  ```bash
  # From the backend directory
  alembic upgrade head
  ```

## Frontend Implementation

### Dashboard Integration
- **Location**: `src/frontend/src/pages/DashboardPage/index.tsx`
- **Features**:
  - "Schedule Workflow" button in dashboard header
  - Dialog modal for creating schedules
  - Workflow selector dropdown
  - Frequency selector (Once, Daily, Weekly, Monthly, Custom)
  - Time picker with clock icon
  - Dark mode compatible UI

### UI Components
- Dialog with form fields
- Select dropdowns for workflow and frequency
- Time input with custom clock icon
- Cancel and Save buttons

## Usage

### Creating a Schedule

1. **Via UI**:
   - Click "Schedule Workflow" button in dashboard header
   - Select a workflow from dropdown
   - Choose frequency (Once, Daily, Weekly, Monthly, Custom)
   - Set time in 24-hour format
   - Click "Save Schedule"

2. **Via API**:
   ```bash
   curl -X POST http://localhost:7860/api/v1/schedules/ \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{
       "flow_id": "your-flow-id",
       "frequency": "daily",
       "schedule_time": "09:00"
     }'
   ```

### Viewing Schedules

```bash
# Get all schedules
curl -X GET http://localhost:7860/api/v1/schedules/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get schedules for specific flow
curl -X GET "http://localhost:7860/api/v1/schedules/?flow_id=your-flow-id" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Pausing/Resuming Schedules

```bash
# Pause
curl -X POST http://localhost:7860/api/v1/schedules/{schedule_id}/pause \
  -H "Authorization: Bearer YOUR_TOKEN"

# Resume
curl -X POST http://localhost:7860/api/v1/schedules/{schedule_id}/resume \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Next Steps (TODO)

### Background Job Execution
To actually execute workflows at scheduled times, you need to implement a scheduler service:

1. **Option 1: APScheduler** (Recommended for simple setups)
   ```python
   # Install: pip install apscheduler
   
   from apscheduler.schedulers.asyncio import AsyncIOScheduler
   from langflow.services.database.models.schedule.model import Schedule
   
   scheduler = AsyncIOScheduler()
   
   async def execute_scheduled_workflow(schedule_id: str):
       # Fetch schedule from database
       # Execute the workflow
       # Update last_run_at, last_run_status
       pass
   
   # Add jobs based on schedules in database
   scheduler.start()
   ```

2. **Option 2: Celery** (For distributed systems)
   ```python
   # Install: pip install celery redis
   
   from celery import Celery
   from celery.schedules import crontab
   
   app = Celery('langflow', broker='redis://localhost:6379')
   
   @app.task
   def execute_workflow(flow_id: str):
       # Execute workflow logic
       pass
   ```

3. **Integration Points**:
   - Add scheduler service to `langflow/services/`
   - Initialize scheduler in `langflow/main.py` lifespan
   - Query active schedules from database
   - Register cron jobs dynamically
   - Handle workflow execution and error logging

### Schedule Display in Dashboard Table
Update the dashboard to show schedule information:
```typescript
// Fetch schedules for each workflow
const schedules = await api.get("/api/v1/schedules/", {
  params: { flow_id: flow.id }
});

// Display in table
<Badge>{schedule ? `${schedule.frequency} at ${schedule.schedule_time}` : "Not scheduled"}</Badge>
```

## Environment Variables

No additional environment variables needed. Uses existing database connection.

## Testing

```bash
# Backend tests
pytest src/backend/tests/unit/api/test_schedules.py

# Frontend - Manual testing:
# 1. Navigate to dashboard
# 2. Click "Schedule Workflow"
# 3. Fill form and save
# 4. Verify schedule appears in table
```

## Troubleshooting

### Schedule not creating
- Check database migration is applied: `alembic current`
- Verify flow exists and user has access
- Check browser console for API errors

### Time picker issues
- Ensure `colorScheme: 'dark'` is set for dark mode
- Browser must support `<input type="time">`

### Backend errors
- Check logs: `tail -f logs/langflow.log`
- Verify database connection
- Ensure user is authenticated

## Security Considerations

- All schedules are user-scoped (can only schedule own workflows)
- Foreign key constraints prevent orphaned schedules
- Schedule execution should validate user permissions
- Consider rate limiting for schedule creation
