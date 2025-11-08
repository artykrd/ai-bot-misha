-- Create subscription_plans table for managing tariffs

CREATE TABLE IF NOT EXISTS subscription_plans (
    id BIGSERIAL PRIMARY KEY,
    plan_id VARCHAR(50) NOT NULL UNIQUE,  -- e.g., "tariff_1", "tariff_2"
    name VARCHAR(100) NOT NULL,  -- Display name
    description TEXT,

    -- Tokens
    tokens_amount BIGINT NOT NULL,

    -- Duration
    duration_days INTEGER NOT NULL,

    -- Pricing
    price NUMERIC(10, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'RUB',

    -- Features
    is_unlimited BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,

    -- Display order and metadata
    sort_order INTEGER DEFAULT 0,
    button_text VARCHAR(200),  -- Text to show on button

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index
CREATE INDEX IF NOT EXISTS idx_subscription_plans_active ON subscription_plans(is_active);
CREATE INDEX IF NOT EXISTS idx_subscription_plans_sort ON subscription_plans(sort_order);

-- Insert default tariffs matching bot_structure.md
INSERT INTO subscription_plans (plan_id, name, description, tokens_amount, duration_days, price, button_text, sort_order) VALUES
    ('tariff_1', '7 дней', 'Базовый тариф на неделю', 150000, 7, 98.00, '7 дней — 150,000 токенов — 98 руб.', 1),
    ('tariff_2', '14 дней', 'Стандартный тариф на 2 недели', 250000, 14, 196.00, '14 дней — 250,000 токенов — 196 руб.', 2),
    ('tariff_3', '21 день', 'Расширенный тариф на 3 недели', 500000, 21, 289.00, '21 день — 500,000 токенов — 289 руб.', 3),
    ('tariff_6', '30 дней (1M)', 'Месячный тариф с 1M токенов', 1000000, 30, 597.00, '30 дней — 1,000,000 токенов — 597 руб.', 4),
    ('tariff_21', '30 дней (5M)', 'Премиум тариф с 5M токенов', 5000000, 30, 2790.00, '30 дней — 5,000,000 токенов — 2790 руб.', 5),
    ('tariff_22', 'Безлимит 1 день', 'Безлимитный доступ на 1 день', 999999999, 1, 199.00, '🔥 Безлимит на 1 день', 6)
ON CONFLICT (plan_id) DO UPDATE SET
    name = EXCLUDED.name,
    tokens_amount = EXCLUDED.tokens_amount,
    duration_days = EXCLUDED.duration_days,
    price = EXCLUDED.price,
    button_text = EXCLUDED.button_text,
    updated_at = NOW();

-- Create eternal tokens plans table
CREATE TABLE IF NOT EXISTS eternal_token_plans (
    id BIGSERIAL PRIMARY KEY,
    plan_id VARCHAR(50) NOT NULL UNIQUE,  -- e.g., "eternal_150k"
    name VARCHAR(100) NOT NULL,
    tokens_amount BIGINT NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'RUB',
    button_text VARCHAR(200),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert eternal token plans
INSERT INTO eternal_token_plans (plan_id, name, tokens_amount, price, button_text, sort_order) VALUES
    ('eternal_150k', '150,000 вечных токенов', 150000, 149.00, '150,000 токенов — 149 руб.', 1),
    ('eternal_250k', '250,000 вечных токенов', 250000, 279.00, '250,000 токенов — 279 руб.', 2),
    ('eternal_500k', '500,000 вечных токенов', 500000, 519.00, '500,000 токенов — 519 руб.', 3),
    ('eternal_1m', '1,000,000 вечных токенов', 1000000, 999.00, '1,000,000 токенов — 999 руб.', 4)
ON CONFLICT (plan_id) DO UPDATE SET
    name = EXCLUDED.name,
    tokens_amount = EXCLUDED.tokens_amount,
    price = EXCLUDED.price,
    button_text = EXCLUDED.button_text,
    updated_at = NOW();

-- View all tariffs
SELECT * FROM subscription_plans WHERE is_active = true ORDER BY sort_order;
SELECT * FROM eternal_token_plans WHERE is_active = true ORDER BY sort_order;
