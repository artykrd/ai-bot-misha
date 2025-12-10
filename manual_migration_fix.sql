-- Manual migration fix script
-- This script manually creates the unlimited invite tables

-- Check if tables exist
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('unlimited_invite_links', 'unlimited_invite_uses');

-- If tables don't exist, create them manually

-- Create unlimited_invite_links table
CREATE TABLE IF NOT EXISTS unlimited_invite_links (
    id BIGSERIAL PRIMARY KEY,
    invite_code VARCHAR(50) NOT NULL UNIQUE,
    duration_days INTEGER NOT NULL,
    max_uses INTEGER,
    current_uses INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT true,
    expires_at TIMESTAMP WITH TIME ZONE,
    description VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_unlimited_invite_links_invite_code ON unlimited_invite_links(invite_code);
CREATE INDEX IF NOT EXISTS ix_unlimited_invite_links_is_active ON unlimited_invite_links(is_active);

-- Create unlimited_invite_uses table
CREATE TABLE IF NOT EXISTS unlimited_invite_uses (
    id BIGSERIAL PRIMARY KEY,
    invite_link_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL UNIQUE,
    subscription_id BIGINT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    FOREIGN KEY (invite_link_id) REFERENCES unlimited_invite_links(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS ix_unlimited_invite_uses_invite_link_id ON unlimited_invite_uses(invite_link_id);
CREATE INDEX IF NOT EXISTS ix_unlimited_invite_uses_user_id ON unlimited_invite_uses(user_id);
