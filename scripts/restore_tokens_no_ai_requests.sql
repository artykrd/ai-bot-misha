-- Restore tokens for subscriptions drained without corresponding ai_requests records.
--
-- When to run: after confirming a user has tokens_used > 0 but zero rows in ai_requests.
-- The mismatch proves token deduction happened through the buggy fixed-cost path in
-- dialog_handler.py (pre-charge without AIRequest creation).
--
-- Safe to run multiple times (idempotent for users who already have tokens_used = 0).

BEGIN;

-- Preview affected subscriptions before making changes:
-- SELECT s.id, s.user_id, s.subscription_type, s.tokens_amount, s.tokens_used, s.updated_at
-- FROM subscriptions s
-- WHERE s.tokens_used > 0
--   AND NOT EXISTS (SELECT 1 FROM ai_requests ar WHERE ar.user_id = s.user_id)
--   AND s.is_active = TRUE;

-- Restore tokens for all active subscriptions belonging to users with zero ai_requests.
UPDATE subscriptions s
SET
    tokens_used = 0,
    updated_at  = NOW()
WHERE s.tokens_used > 0
  AND s.is_active = TRUE
  AND NOT EXISTS (
      SELECT 1 FROM ai_requests ar WHERE ar.user_id = s.user_id
  );

-- Verify result:
SELECT s.id, s.user_id, s.subscription_type, s.tokens_amount, s.tokens_used
FROM subscriptions s
WHERE NOT EXISTS (SELECT 1 FROM ai_requests ar WHERE ar.user_id = s.user_id)
  AND s.is_active = TRUE
ORDER BY s.user_id, s.id;

COMMIT;
