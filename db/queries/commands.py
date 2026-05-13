import asyncpg


async def insert_command_usage(
    pool: asyncpg.Pool,
    user_id: int,
    guild_id: int,
    command_name: str,
    success: bool = True,
) -> None:
    """Record every slash command invocation with success/failure outcome."""
    await pool.execute(
        """
        INSERT INTO command_usage (user_id, guild_id, command_name, success)
        VALUES ($1, $2, $3, $4)
        """,
        user_id, guild_id, command_name, success,
    )
