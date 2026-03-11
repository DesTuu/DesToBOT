import discord
from discord.ext import commands

class CancelGameListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is None or message.author.bot is False:
            return

        if message.guild.id != 1056134342826528808:
            return
        if not message.channel.category or message.channel.category.id != 1343928535974154240:
            return
        if message.author.id != 857633321064595466:
            return

        if message.embeds:
            embed = message.embeds[0]
            if embed.title and "cancel game?" in embed.title.lower():
                users = []
                for field in embed.fields:
                    if "not voted:" in field.value.lower():
                        lines = field.value.split("\n")
                        for line in lines:
                            if line.lower().startswith("not voted:"):
                                users_raw = line.split(":", 1)[1]
                                users = [name.strip() for name in users_raw.split(",") if name.strip()]
                user_list = ", ".join(users) if users else "brak danych"
                channel = self.bot.get_channel(1377020524802080799)
                if channel:
                    await channel.send(f"Ktoś z użytkowników: {user_list} - użył komendy /cancel")


async def setup(bot):
    await bot.add_cog(CancelGameListener(bot))
