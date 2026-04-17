import asyncpg


async def insert_mod_event(
    pool: asyncpg.Pool,
    target_user_id: int,
    moderator_user_id: int,
    guild_id: int,
    action_type: str,
    reason: str = None,
    expires_at=None,
) -> None:
    """Record a moderation action. action_type must be: warn, mute, kick, ban, unban, unmute."""
    await pool.execute(
        """
        INSERT INTO moderation_events
            (target_user_id, moderator_user_id, guild_id, action_type, reason, expires_at)
        VALUES ($1, $2, $3, $4, $5, $6)
        """,
        target_user_id, moderator_user_id, guild_id, action_type, reason, expires_at,
    )
