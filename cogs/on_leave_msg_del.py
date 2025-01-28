import discord
from discord.ext import commands


class OnLeaveMsgDel(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        if member.guild.id == 1056134342826528808:
            general_channel = self.bot.get_channel(1056276694140452964)
            async for message in general_channel.history(limit=100):
                if str(message.author.id).strip() == "282859044593598464":
                    if f"<@!{member.id}>" in message.content:
                        await message.delete()


async def setup(bot):
    await bot.add_cog(OnLeaveMsgDel(bot))
