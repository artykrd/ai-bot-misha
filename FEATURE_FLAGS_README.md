# Feature Flags and Unlimited Limits Implementation

## Overview

This implementation adds:

1. **Unlimited subscription limits enforcement** - Real daily limits for unlimited_1day subscriptions
2. **Async video generation** - Job queue for scalable video processing (supports 100+ concurrent users)
3. **Comprehensive AI logging** - Full tracking of all AI operations for analytics and cost control
4. **Feature flags** - Safe rollout via system_settings table

## Key Components

### 1. Unlimited Limits Service

**File:** `app/services/subscription/unlimited_limits_service.py`

- Enforces daily limits for unlimited subscriptions based on `model_costs` table
- Time window: 21:00 MSK → 21:00 MSK (24 hours)
- Checks both request count and token budget per model
- Integrated into `SubscriptionService.check_and_use_tokens()`

**Configuration:**
- `model_costs.unlimited_daily_limit` - Max requests per day
- `model_costs.unlimited_budget_tokens` - Token budget per day

### 2. Async Video Architecture

**Files:**
- `app/database/models/video_job.py` - Job queue model
- `app/services/video_job_service.py` - Job management service
- `app/workers/video_worker.py` - Background worker
- `app/bot/handlers/async_kling_handler.py` - Async Kling handler

**How it works:**
1. User requests video → Job created in `video_generation_jobs` table
2. User gets "in queue" message immediately
3. Background worker processes jobs asynchronously
4. Worker sends video to user when ready
5. Handles timeouts gracefully (timeout_waiting status for retry)

**Benefits:**
- Non-blocking: bot doesn't wait for video generation
- Scalable: supports 100+ concurrent users
- Reliable: jobs persist in database, can be retried
- User-friendly: "video in queue" vs "timeout error"

### 3. Comprehensive AI Logging

**Files:**
- `app/services/logging/ai_logging_service.py` - Logging service (already existed, now used everywhere)
- Updated: `check_and_use_tokens()` now accepts `model_id` for limits

**Features:**
- All AI operations logged to `ai_requests` table
- Tracks: cost_usd, cost_rub, operation_category, subscription_id, is_unlimited_subscription
- Status lifecycle: pending → completed/failed/timeout_waiting
- Fire-and-forget: errors don't break operations

### 4. Feature Flags

**Table:** `system_settings`

**Flags:**
- `unlimited_limits_enabled` (default: true) - Enable/disable limits enforcement
- `async_video_enabled` (default: true) - Enable/disable async video queue
- `ai_logging_enabled` (default: true) - Enable/disable comprehensive logging

**Usage:**
```python
async with async_session_maker() as session:
    result = await session.execute(
        select(SystemSetting).where(SystemSetting.key == "unlimited_limits_enabled")
    )
    setting = result.scalar_one_or_none()
    enabled = setting.value.lower() in ("true", "1", "yes") if setting else True
```

## Database Changes

### New Table: `video_generation_jobs`

```sql
CREATE TABLE video_generation_jobs (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    ai_request_id BIGINT,
    provider VARCHAR(50) NOT NULL,  -- kling, sora, veo, etc.
    model_id VARCHAR(100) NOT NULL,
    task_id VARCHAR(255),           -- Provider's task ID
    status VARCHAR(50) NOT NULL DEFAULT 'pending',  -- pending, processing, timeout_waiting, completed, failed
    prompt TEXT NOT NULL,
    input_data JSONB NOT NULL,
    video_path TEXT,
    error_message TEXT,
    chat_id BIGINT NOT NULL,
    progress_message_id BIGINT,
    tokens_cost BIGINT NOT NULL DEFAULT 0,
    attempt_count INT NOT NULL DEFAULT 0,
    max_attempts INT NOT NULL DEFAULT 3,
    started_processing_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (ai_request_id) REFERENCES ai_requests(id) ON DELETE SET NULL
);

CREATE INDEX ix_video_generation_jobs_status ON video_generation_jobs(status);
CREATE INDEX ix_video_generation_jobs_expires_at ON video_generation_jobs(expires_at);
-- etc.
```

### New Feature Flags in `system_settings`

```sql
INSERT INTO system_settings (key, value, value_type, description) VALUES
    ('unlimited_limits_enabled', 'true', 'bool', 'Enable unlimited subscription limits enforcement'),
    ('async_video_enabled', 'true', 'bool', 'Enable async video generation with job queue'),
    ('ai_logging_enabled', 'true', 'bool', 'Enable comprehensive AI operations logging');
```

## Migration

**File:** `alembic/versions/006_add_video_jobs_and_feature_flags.py`

**Apply migration:**
```bash
alembic upgrade head
```

**Rollback (if needed):**
```bash
alembic downgrade 005
```

## Usage Examples

### 1. Check Unlimited Limits

```python
from app.services.subscription.unlimited_limits_service import UnlimitedLimitsService

async with async_session_maker() as session:
    limits_service = UnlimitedLimitsService(session)
    allowed, error_msg = await limits_service.check_unlimited_limits(
        user_id=123,
        subscription=subscription,
        model_id="kling-2.5",
        tokens_cost=50000
    )
    if not allowed:
        # Show error to user
        await message.answer(error_msg)
```

### 2. Create Async Video Job

```python
from app.services.video_job_service import VideoJobService

async with async_session_maker() as session:
    job_service = VideoJobService(session)
    job = await job_service.create_job(
        user_id=user.id,
        provider="kling",
        model_id="kling-v2-5-turbo",
        prompt="Epic dragon flying over mountains",
        input_data={
            "images": [],
            "duration": 5,
            "aspect_ratio": "16:9",
            "version": "2.5"
        },
        chat_id=message.chat.id,
        tokens_cost=50000,
        progress_message_id=msg.message_id
    )
```

### 3. Log AI Operation

```python
from app.services.logging import log_ai_operation_background

# Fire-and-forget logging
log_ai_operation_background(
    user_id=user.id,
    model_id="kling-2.5",
    operation_category="video_gen",
    tokens_cost=50000,
    prompt=prompt[:500],
    status="completed",
    response_file_path=video_path,
    processing_time_seconds=elapsed_time,
    input_data={"duration": 5, "version": "2.5"}
)
```

## Background Worker

The video worker runs automatically when bot starts.

**Configuration:**
- Poll interval: 30 seconds (configurable in `VideoWorker.__init__`)
- Max concurrent pending jobs: 5
- Max concurrent timeout retries: 3
- Cleanup expired jobs: every 10th cycle

**Monitoring:**
```python
# Check logs for:
# - "video_worker_started"
# - "processing_pending_video_jobs"
# - "video_job_completed"
# - "video_job_failed"
```

## Testing

### 1. Test Unlimited Limits

1. Get unlimited_1day subscription
2. Configure model_costs with low limits (e.g., 3 requests, 10000 tokens)
3. Make requests until limit reached
4. Verify error message with limit info
5. Wait until 21:00 MSK for reset

### 2. Test Async Video

1. Request Kling video generation
2. Verify "in queue" message appears immediately
3. Check `video_generation_jobs` table for new record
4. Monitor worker logs for processing
5. Verify video sent to user when ready

### 3. Test Feature Flags

```sql
-- Disable async video
UPDATE system_settings SET value = 'false' WHERE key = 'async_video_enabled';

-- Re-enable
UPDATE system_settings SET value = 'true' WHERE key = 'async_video_enabled';
```

## Troubleshooting

### Video jobs not processing

1. Check worker is running: grep "video_worker_started" in logs
2. Check feature flag: `SELECT * FROM system_settings WHERE key = 'async_video_enabled';`
3. Check pending jobs: `SELECT * FROM video_generation_jobs WHERE status = 'pending';`

### Limits not enforcing

1. Check feature flag: `SELECT * FROM system_settings WHERE key = 'unlimited_limits_enabled';`
2. Check model_costs configured: `SELECT * FROM model_costs WHERE model_id LIKE 'kling%';`
3. Check ai_requests for tracking: `SELECT * FROM ai_requests WHERE user_id = X ORDER BY created_at DESC;`

### Jobs stuck in processing

1. Check for expired jobs: `SELECT * FROM video_generation_jobs WHERE expires_at < NOW();`
2. Worker auto-cleans expired jobs every 10th cycle
3. Manual cleanup: `UPDATE video_generation_jobs SET status = 'failed' WHERE expires_at < NOW();`

## Production Considerations

### 1. Backward Compatibility

✅ All changes are backward compatible:
- Feature flags default to enabled
- Async handler falls back to sync if disabled
- Old code continues to work
- No data deletion or destructive changes

### 2. Performance

- Video worker processes max 5 jobs simultaneously
- Pending jobs polled every 30 seconds
- Database indexed on critical columns
- Fire-and-forget logging doesn't block operations

### 3. Monitoring

Key metrics to track:
- Video job success rate
- Average processing time
- Expired job count
- Unlimited limit violations
- AI request completion rate

### 4. Scaling

For higher load:
- Increase worker `poll_interval` (lower = faster, more DB load)
- Increase max concurrent jobs in worker
- Run multiple worker instances (ensure unique job locking)
- Monitor database connection pool

## Security

- No user input directly in SQL queries (uses SQLAlchemy ORM)
- Proper foreign key constraints prevent orphaned records
- Feature flags allow quick disable if issues arise
- Unlimited limits prevent cost abuse

## Future Enhancements

Possible additions:
- Priority queue for premium users
- Job retry with exponential backoff
- Webhook notifications for job completion
- Admin panel for job management
- Per-user concurrency limits
- Job analytics dashboard
