-- Quick script to add unlimited tokens to latest user
-- Copy and paste this into your psql session

-- Step 1: Show all users (to find your user_id)
SELECT id, telegram_id, username, first_name, last_name, created_at
FROM users
ORDER BY created_at DESC;

-- Step 2: Add unlimited subscription to user
-- IMPORTANT: Replace '1' with your actual user_id from query above
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
    1,  -- ⚠️ REPLACE THIS with your user_id from query above
    'unlimited_test',
    9999999,
    0,
    0.00,
    true,
    NOW(),
    NOW() + INTERVAL '365 days'
);

-- Step 3: Verify subscription was created
SELECT
    u.id as user_id,
    u.telegram_id,
    u.username,
    s.id as subscription_id,
    s.subscription_type,
    s.tokens_amount,
    s.tokens_used,
    (s.tokens_amount - s.tokens_used) as remaining_tokens,
    s.is_active,
    s.expires_at
FROM subscriptions s
JOIN users u ON u.id = s.user_id
WHERE s.is_active = true
ORDER BY s.created_at DESC;
