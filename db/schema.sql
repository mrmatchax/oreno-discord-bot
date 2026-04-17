-- ============================================================
--  Discord Bot — Postgres Schema
--  Multi-server ready | 6 tables
--  Last updated: removed sentiment, removed reaction_events
-- ============================================================


-- ------------------------------------------------------------
--  1. GUILDS
--     One row per Discord server the bot is in.
-- ------------------------------------------------------------
CREATE TABLE guilds (
    guild_id    BIGINT      PRIMARY KEY,   -- Discord's own snowflake ID
    guild_name  TEXT        NOT NULL,
    joined_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active   BOOLEAN     NOT NULL DEFAULT TRUE
);


-- ------------------------------------------------------------
--  2. USERS
--     One row per Discord user the bot has ever seen.
--     username = latest only (no history tracking).
-- ------------------------------------------------------------
CREATE TABLE users (
    user_id       BIGINT      PRIMARY KEY,  -- Discord's own snowflake ID
    username      TEXT        NOT NULL,
    display_name  TEXT,
    avatar_url    TEXT,
    first_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ------------------------------------------------------------
--  3. GUILD MEMBERS
--     Tracks which users are in which guilds.
--     nickname = latest value only, changes are overwritten.
--     left_at = NULL means they are currently a member.
--     This is your retention / churn data.
-- ------------------------------------------------------------
CREATE TABLE guild_members (
    guild_id    BIGINT      NOT NULL REFERENCES guilds(guild_id),
    user_id     BIGINT      NOT NULL REFERENCES users(user_id),
    nickname    TEXT,                      -- Latest nickname, overwrites on change
    joined_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    left_at     TIMESTAMPTZ,               -- NULL = still a member
    is_active   BOOLEAN     NOT NULL DEFAULT TRUE,
    PRIMARY KEY (guild_id, user_id)
);


-- ------------------------------------------------------------
--  4. VOICE SESSIONS
--     One row per voice channel session (join -> leave).
--     duration_seconds is calculated on leave and stored.
--     left_at = NULL means they are currently in the channel.
-- ------------------------------------------------------------
CREATE TABLE voice_sessions (
    session_id       UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id          BIGINT      NOT NULL REFERENCES users(user_id),
    guild_id         BIGINT      NOT NULL REFERENCES guilds(guild_id),
    channel_id       BIGINT      NOT NULL,
    channel_name     TEXT        NOT NULL,
    joined_at        TIMESTAMPTZ NOT NULL,
    left_at          TIMESTAMPTZ,           -- NULL = still in channel
    duration_seconds INT                    -- Filled when they leave
);


-- ------------------------------------------------------------
--  5. MESSAGE EVENTS
--     One row per message sent.
--     Stores full content + metadata signals for later analysis.
-- ------------------------------------------------------------
CREATE TABLE message_events (
    message_id          BIGINT      PRIMARY KEY,  -- Discord's own message ID
    user_id             BIGINT      NOT NULL REFERENCES users(user_id),
    guild_id            BIGINT      NOT NULL REFERENCES guilds(guild_id),
    channel_id          BIGINT      NOT NULL,
    channel_name        TEXT        NOT NULL,
    content             TEXT,                     -- Full message text
    message_length      INT,
    has_attachment      BOOLEAN     NOT NULL DEFAULT FALSE,
    has_mention         BOOLEAN     NOT NULL DEFAULT FALSE,
    is_reply            BOOLEAN     NOT NULL DEFAULT FALSE,
    reply_to_message_id BIGINT,                   -- NULL if not a reply
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ------------------------------------------------------------
--  6. MODERATION EVENTS
--     One row per moderation action (warn, mute, kick, ban).
--     target_user_id    = the member receiving the action.
--     moderator_user_id = the mod who issued it.
--     Both reference the users table but represent different
--     people — this lets you audit who did what to whom.
-- ------------------------------------------------------------
CREATE TABLE moderation_events (
    event_id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    target_user_id    BIGINT      NOT NULL REFERENCES users(user_id),
    moderator_user_id BIGINT      NOT NULL REFERENCES users(user_id),
    guild_id          BIGINT      NOT NULL REFERENCES guilds(guild_id),
    action_type       TEXT        NOT NULL CHECK (action_type IN ('warn', 'mute', 'kick', 'ban', 'unban', 'unmute')),
    reason            TEXT,
    expires_at        TIMESTAMPTZ,          -- NULL = permanent (for mutes/bans)
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ------------------------------------------------------------
--  7. COMMAND USAGE
--     One row every time a slash command is used.
--     Lets you see which features are actually used over time.
-- ------------------------------------------------------------
CREATE TABLE command_usage (
    usage_id     UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      BIGINT      NOT NULL REFERENCES users(user_id),
    guild_id     BIGINT      NOT NULL REFERENCES guilds(guild_id),
    command_name TEXT        NOT NULL,
    success      BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


-- ============================================================
--  INDEXES
--  Added on columns you will query and filter most often.
-- ============================================================

-- Voice sessions
CREATE INDEX idx_voice_sessions_user_id   ON voice_sessions(user_id);
CREATE INDEX idx_voice_sessions_guild_id  ON voice_sessions(guild_id);
CREATE INDEX idx_voice_sessions_joined_at ON voice_sessions(joined_at);

-- Message events
CREATE INDEX idx_message_events_user_id    ON message_events(user_id);
CREATE INDEX idx_message_events_guild_id   ON message_events(guild_id);
CREATE INDEX idx_message_events_created_at ON message_events(created_at);

-- Moderation events
CREATE INDEX idx_moderation_target_user ON moderation_events(target_user_id);
CREATE INDEX idx_moderation_guild_id    ON moderation_events(guild_id);

-- Guild members
CREATE INDEX idx_guild_members_guild_id  ON guild_members(guild_id);
CREATE INDEX idx_guild_members_is_active ON guild_members(is_active);
