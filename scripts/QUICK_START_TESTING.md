# Quick Start: Add Unlimited Tokens for Testing

## Option 1: Single psql command (Fastest)

Connect to your database and run this **one-liner** (replace `USER_ID` with your actual user id):

```bash
psql -U ai_bot_user -d ai_bot -c "INSERT INTO subscriptions (user_id, subscription_type, tokens_amount, tokens_used, price, is_active, started_at, expires_at) VALUES (1, 'unlimited_test', 9999999, 0, 0.00, true, NOW(), NOW() + INTERVAL '365 days');"
```

## Option 2: Step-by-step in psql

1. **Find your user_id:**
```sql
SELECT id, telegram_id, username, first_name
FROM users
ORDER BY created_at DESC
LIMIT 1;
```

2. **Add unlimited subscription** (replace `1` with your user_id):
```sql
INSERT INTO subscriptions (
    user_id, subscription_type, tokens_amount, tokens_used,
    price, is_active, started_at, expires_at
) VALUES (
    1,  -- Your user_id here
    'unlimited_test', 9999999, 0, 0.00, true,
    NOW(), NOW() + INTERVAL '365 days'
);
```

3. **Verify it worked:**
```sql
SELECT u.telegram_id, u.username, s.tokens_amount, s.tokens_used,
       s.tokens_amount - s.tokens_used as remaining
FROM subscriptions s
JOIN users u ON u.id = s.user_id
WHERE s.is_active = true;
```

## Option 3: Use provided SQL file

```bash
psql -U ai_bot_user -d ai_bot -f scripts/quick_add_tokens.sql
```

Then manually edit the user_id in the INSERT statement before running.

---

## After Adding Tokens

✅ You should now have **9,999,999 tokens** available
✅ Subscription is valid for **365 days**
✅ You can test the bot **unlimited times**

**Test it:** Send `/start` in the bot, check your balance should show 9,999,999 tokens!
