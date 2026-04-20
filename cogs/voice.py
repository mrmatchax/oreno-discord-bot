import discord
from discord.ext import commands
from datetime import datetime, timezone
from db.queries.voice import open_session, close_session
from db.queries.users import upsert_user
import logging

logger = logging.getLogger("bot")


class Voice(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        if member.bot:
            return

        await upsert_user(self.bot.pool, member.id, member.name, member.display_name)

        # User joins a voice channel
        if before.channel is None and after.channel is not None:
            await open_session(
                pool=self.bot.pool,
                user_id=member.id,
                guild_id=member.guild.id,
                channel_id=after.channel.id,
                channel_name=after.channel.name,
                joined_at=datetime.now(timezone.utc),
            )
            logger.info(f"🎤 {member.name} joined {after.channel.name}")

        # User leaves a voice channel
        elif before.channel is not None and after.channel is None:
            await close_session(
                pool=self.bot.pool,
                user_id=member.id,
                guild_id=member.guild.id,
                left_at=datetime.now(timezone.utc),
            )
            logger.info(f"🚪 {member.name} left {before.channel.name}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Voice(bot))
