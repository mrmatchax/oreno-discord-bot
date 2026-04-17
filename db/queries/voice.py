import asyncpg


async def open_session(
    pool: asyncpg.Pool,
    user_id: int,
    guild_id: int,
    channel_id: int,
    channel_name: str,
    joined_at,
) -> str:
    """Record a new voice session when a user joins a channel. Returns the UUID session_id."""
    row = await pool.fetchrow(
        """
        INSERT INTO voice_sessions (user_id, guild_id, channel_id, channel_name, joined_at)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING session_id
        """,
        user_id, guild_id, channel_id, channel_name, joined_at,
    )
    return str(row["session_id"])


async def close_session(
    pool: asyncpg.Pool,
    user_id: int,
    guild_id: int,
    left_at,
) -> None:
    """Close the most recent open voice session and compute duration in seconds."""
    await pool.execute(
        """
        UPDATE voice_sessions
        SET left_at          = $3,
            duration_seconds = EXTRACT(EPOCH FROM ($3 - joined_at))::INT
        WHERE user_id  = $1
          AND guild_id = $2
          AND left_at IS NULL
        """,
        user_id, guild_id, left_at,
    )
