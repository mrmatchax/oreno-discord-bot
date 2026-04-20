import discord
from discord.ext import commands
from db.queries.users import upsert_user, upsert_guild_member, mark_member_left


class Members(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.bot:
            return
        await upsert_user(self.bot.pool, member.id, member.name, member.display_name)
        await upsert_guild_member(self.bot.pool, member.guild.id, member.id, member.joined_at, member.nick)
        await member.send(f"Hello Human, Welcome to fking Jedi Temple. May Mae be with u, {member.mention}!")

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        if member.bot:
            return
        await mark_member_left(self.bot.pool, member.guild.id, member.id)


async def setup(bot: commands.Bot):
    await bot.add_cog(Members(bot))
