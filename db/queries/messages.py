import asyncpg


async def insert_message(
    pool: asyncpg.Pool,
    message_id: int,
    user_id: int,
    guild_id: int,
    channel_id: int,
    channel_name: str,
    content: str,
    has_attachment: bool,
    has_mention: bool,
    is_reply: bool,
    reply_to_message_id: int = None,
) -> None:
    """Record a message event with full content and interaction metadata."""
    await pool.execute(
        """
        INSERT INTO message_events (
            message_id, user_id, guild_id, channel_id, channel_name,
            content, message_length, has_attachment, has_mention,
            is_reply, reply_to_message_id
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        ON CONFLICT (message_id) DO NOTHING
        """,
        message_id, user_id, guild_id, channel_id, channel_name,
        content, len(content) if content else 0,
        has_attachment, has_mention, is_reply, reply_to_message_id,
    )
