import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import logging

# Configure logging for containers (unbuffered output)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]  # Writes to stderr (not buffered)
)
logger = logging.getLogger("bot")

# Config handler
handler = logging.FileHandler('discord.log', encoding='utf-8', mode='w')

# 1. SECURITY: Load the secret token from the .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# 2. PERMISSIONS (Intents): Tell Discord what data we want to see
intents = discord.Intents.default()
intents.message_content = True  # Allows bot to read chat messages
intents.members = True          # Allows bot to see who is in the server
intents.voice_states = True     # CRITICAL: Allows bot to see voice channel joins/leaves

# 3. INITIALIZATION: Create the bot instance
# We set a dummy prefix '!' because we plan to use modern Slash (/) commands later
class SuperBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    # The 'setup_hook' runs once when the bot starts up.
    # It is the best place to sync our slash commands to Discord.
    async def setup_hook(self):
        try:
            synced = await self.tree.sync()
            logger.info(f"🔄 Synced {len(synced)} slash command(s) to Discord.")
        except Exception as e:
            logger.error(f"❌ Failed to sync commands: {e}")

# Instantiate our custom bot
bot = SuperBot()

# 4. EVENTS: What the bot does when it successfully connects
@bot.event
async def on_ready():
    logger.info("----------------------------------------")
    logger.info(f"✅ Bot is Online!")
    logger.info(f"🤖 Name: {bot.user.name}")
    logger.info(f"🆔 ID: {bot.user.id}")
    logger.info("----------------------------------------")
@bot.event
async def on_member_join(member):
    await member.send(f"Hello Human, I'm your cutie piggy sniffy hedgehog MAEEEEEEEEEEEE, {member.mention}!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Ignore messages from the bot itself

    if "shit" in message.content.lower():
        await message.delete()  # Deletes the offending message
        await message.channel.send(f"{message.author.mention}! Don't say that! MAEEEEEEEEEEEE!")
    
    await bot.process_commands(message)  # Ensure commands still work

# Command section
# !hello
@bot.command()
async def hello(ctx):
    
    await ctx.send(f"Hello {ctx.author.mention}!")

# 5. EXECUTION: Start the bot using the token
if __name__ == '__main__':
    if TOKEN is None:
        logging.info("❌ Error: DISCORD_TOKEN not found. Check your .env file!")
    else:
        bot.run(TOKEN,log_handler=handler, log_level=logging.DEBUG)