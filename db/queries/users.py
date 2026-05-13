import asyncpg


async def upsert_user(
    pool: asyncpg.Pool,
    user_id: int,
    username: str,
    display_name: str = None,
) -> None:
    """Insert or update a Discord user. Overwrites username/display_name on conflict."""
    await pool.execute(
        """
        INSERT INTO users (user_id, username, display_name)
        VALUES ($1, $2, $3)
        ON CONFLICT (user_id) DO UPDATE
            SET username     = EXCLUDED.username,
                display_name = EXCLUDED.display_name,
                updated_at   = NOW()
        """,
        user_id, username, display_name,
    )


async def upsert_guild(pool: asyncpg.Pool, guild_id: int, guild_name: str) -> None:
    """Insert or update a Discord guild (server). Marks it active if it rejoins."""
    await pool.execute(
        """
        INSERT INTO guilds (guild_id, guild_name)
        VALUES ($1, $2)
        ON CONFLICT (guild_id) DO UPDATE
            SET guild_name = EXCLUDED.guild_name,
                is_active  = TRUE
        """,
        guild_id, guild_name,
    )


async def upsert_guild_member(
    pool: asyncpg.Pool,
    guild_id: int,
    user_id: int,
    joined_at,
    nickname: str = None,
) -> None:
    """Insert or reactivate a guild membership. Overwrites nickname if provided."""
    await pool.execute(
        """
        INSERT INTO guild_members (guild_id, user_id, joined_at, nickname, is_active)
        VALUES ($1, $2, $3, $4, TRUE)
        ON CONFLICT (guild_id, user_id) DO UPDATE
            SET joined_at = EXCLUDED.joined_at,
                nickname  = EXCLUDED.nickname,
                is_active = TRUE,
                left_at   = NULL
        """,
        guild_id, user_id, joined_at, nickname,
    )


async def mark_member_left(pool: asyncpg.Pool, guild_id: int, user_id: int) -> None:
    """Mark a guild member inactive when they leave the server."""
    await pool.execute(
        """
        UPDATE guild_members
        SET is_active = FALSE, left_at = NOW()
        WHERE guild_id = $1 AND user_id = $2
        """,
        guild_id, user_id,
    )
