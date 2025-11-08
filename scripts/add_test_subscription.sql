-- Script to add unlimited test subscription
-- Run this in psql connected to ai_bot database

-- 1. First, find your user (replace with your actual telegram_id)
SELECT id, telegram_id, username, first_name
FROM users
ORDER BY created_at DESC
LIMIT 5;

-- If you know your telegram_id, use it here:
-- SELECT id FROM users WHERE telegram_id = YOUR_TELEGRAM_ID;

-- 2. Add unlimited test subscription (replace USER_ID with your actual id from step 1)
INSERT INTO subscriptions (
    user_id,
    subscription_type,
    tokens_amount,
    tokens_used,
    price,
    is_active,
    started_at,
    expires_at
) VALUES (
    1,  -- Replace with your user_id from query above
    'unlimited_test',
    9999999,
    0,
    0.00,
    true,
    NOW(),
    NOW() + INTERVAL '365 days'  -- Valid for 1 year
)
ON CONFLICT DO NOTHING;

-- 3. Verify subscription was created
SELECT
    u.telegram_id,
    u.username,
    s.subscription_type,
    s.tokens_amount,
    s.tokens_used,
    s.tokens_amount - s.tokens_used as remaining_tokens,
    s.is_active,
    s.expires_at
FROM subscriptions s
JOIN users u ON u.id = s.user_id
WHERE s.is_active = true;
