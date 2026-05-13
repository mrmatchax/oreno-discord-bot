import discord
from discord.ext import commands
from db.queries.commands import insert_command_usage


class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name="ping", description="Replies with Pong and shows the bot's latency!")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"🏓 Pong! My latency is {latency}ms.")
        await insert_command_usage(self.bot.pool, interaction.user.id, interaction.guild_id, "ping", success=True)

    @discord.app_commands.command(name="test", description="A simple test command to check if the bot is working.")
    async def test(self, interaction: discord.Interaction):
        await interaction.response.send_message("✅ Test successful! The bot is working fine.")
        await insert_command_usage(self.bot.pool, interaction.user.id, interaction.guild_id, "test", success=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))
