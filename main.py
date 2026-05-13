import asyncio
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import logging
from aiohttp import web

from db.connection import create_pool, close_pool
from db.queries.users import upsert_guild, upsert_user, upsert_guild_member

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("bot")
handler = logging.FileHandler('discord.log', encoding='utf-8', mode='w')

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

COGS = [
    "cogs.general",
    "cogs.members",
    "cogs.messages",
    "cogs.voice",
]

class SuperBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.pool = await create_pool()
        logger.info("✅ Database pool created.")

        for cog in COGS:
            await self.load_extension(cog)
            logger.info(f"🔌 Loaded cog: {cog}")

        try:
            synced = await self.tree.sync()
            logger.info(f"🔄 Synced {len(synced)} slash command(s).")
        except Exception as e:
            logger.error(f"❌ Failed to sync commands: {e}")

    async def close(self):
        await close_pool()
        logger.info("🔌 Database pool closed.")
        await super().close()

bot = SuperBot()

@bot.event
async def on_ready():
    logger.info("----------------------------------------")
    logger.info(f"✅ Bot is Online!")
    logger.info(f"🤖 Name: {bot.user.name}")
    logger.info(f"🆔 ID: {bot.user.id}")
    logger.info("----------------------------------------")

    # Upsert every guild and member the bot can already see on startup
    for guild in bot.guilds:
        await upsert_guild(bot.pool, guild.id, guild.name)
        async for member in guild.fetch_members():
            if not member.bot:
                await upsert_user(bot.pool, member.id, member.name, member.display_name)
                await upsert_guild_member(bot.pool, guild.id, member.id, member.joined_at, member.nick)
        logger.info(f"📋 Synced guild: {guild.name}")

async def health_check(request):
    return web.Response(text="OK")

async def run_health_server():
    app = web.Application()
    app.router.add_get("/", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Health server running on port {port}")

async def main():
    if TOKEN is None:
        logger.error("❌ DISCORD_TOKEN not found. Check your .env file!")
        return
    await run_health_server()
    async with bot:
        await bot.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
