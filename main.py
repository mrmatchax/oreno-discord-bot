import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import logging
import time
import csv
import os

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
    await member.send(f"Hello Human, Welcome to fking Jedi Temple. May Mae be with u, {member.mention}!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Ignore messages from the bot itself

    if "shit" in message.content.lower():
        await message.delete()  # Deletes the offending message
        await message.channel.send(f"{message.author.mention}! Don't say that! MAEEEEEEEEEEEE!")
    
    await bot.process_commands(message)  # Ensure commands still work

active_voice_sessions = {}

@bot.event
async def on_voice_state_update(member, before, after):
    # Ignore the bot itself so we don't track its own movements
    logging.info(f"Voice state update for {member.name}: before={before.channel}, after={after.channel}")
    if member.bot:
        return
    # log active_voice_sessions to see if it's working
    logging.info(f"Current active voice sessions: {active_voice_sessions}")
    # 1. User JOINS a voice channel (before.channel is None, after.channel has a value)
    if before.channel is None and after.channel is not None:
        active_voice_sessions[member.id] = time.time() # Record the exact start time
        logger.info(f"🎤 {member.name} joined {after.channel.name}")

    # 2. User LEAVES a voice channel (before.channel has a value, after.channel is None)
    elif before.channel is not None and after.channel is None:
        # Check if we have their join time recorded
        logging.info("in elif")
        if member.id in active_voice_sessions:
            logging.info("found member")
            join_time = active_voice_sessions.pop(member.id) # Remove them from active memory and get the time
            leave_time = time.time()
            duration_seconds = round(leave_time - join_time)

            logger.info(f"🚪 {member.name} left {before.channel.name}. Stayed for {duration_seconds} seconds.")

            # --- DATA ENGINEERING STEP 1: STORE THE RAW DATA ---
            # We open a CSV file in 'a' (append) mode to add a new row
            
            file_name = 'voice_logs.csv'
            file_exists = os.path.isfile(file_name)
            
            with open(file_name, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # If the file was just created, write the header row first
                if not file_exists:
                    writer.writerow(['user_id', 'username', 'channel_name', 'duration_seconds', 'timestamp'])
                
                # Write the actual data row
                writer.writerow([member.id, member.name, before.channel.name, duration_seconds, int(leave_time)])


# Command section
# !hello
@bot.command()
async def hello(ctx):
    
    await ctx.send(f"Hello {ctx.author.mention}!")
    
    
@bot.tree.command(name="ping", description="Replies with Pong and shows the bot's latency!")
async def ping(interaction: discord.Interaction):
    # Calculate latency in milliseconds
    latency = round(bot.latency * 1000)
    
    # We must 'respond' to the interaction, otherwise Discord thinks the bot crashed!
    await interaction.response.send_message(f"🏓 Pong! My latency is {latency}ms.")

@bot.tree.command(name="test", description="A simple test command to check if the bot is working.")
async def test(interaction: discord.Interaction):
    await interaction.response.send_message("✅ Test successful! The bot is working fine.")

# 5. EXECUTION: Start the bot using the token
if __name__ == '__main__':
    if TOKEN is None:
        logging.info("❌ Error: DISCORD_TOKEN not found. Check your .env file!")
    else:
        #bot.run(TOKEN,log_handler=handler, log_level=logging.DEBUG)
        bot.run(TOKEN,log_handler=handler)