import discord
from discord.ext import commands
from db.queries.messages import insert_message
from db.queries.users import upsert_user


class Messages(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.guild is None:
            return

        # Word filter
        if "shit" in message.content.lower():
            await message.delete()
            await message.channel.send(f"{message.author.mention}! Don't say that! MAEEEEEEEEEEEE!")
            return

        await upsert_user(self.bot.pool, message.author.id, message.author.name, message.author.display_name)
        await insert_message(
            pool=self.bot.pool,
            message_id=message.id,
            user_id=message.author.id,
            guild_id=message.guild.id,
            channel_id=message.channel.id,
            channel_name=message.channel.name,
            content=message.content,
            has_attachment=len(message.attachments) > 0,
            has_mention=len(message.mentions) > 0,
            is_reply=message.reference is not None,
            reply_to_message_id=message.reference.message_id if message.reference else None,
        )

        await self.bot.process_commands(message)


async def setup(bot: commands.Bot):
    await bot.add_cog(Messages(bot))
