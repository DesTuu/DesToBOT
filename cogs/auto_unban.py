from datetime import datetime, timedelta, timezone
from discord.ext import commands
import discord
import asyncio

TARGET_GUILD_ID = 1056134342826528808
TARGET_CHANNEL_ID = 1281898784741261456
MODERATOR_ID = 1075805857314521118

class AutoUnban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_ban(self, *_):
        await self.check_autobans()

    async def check_autobans(self):
        guild = self.bot.get_guild(TARGET_GUILD_ID)
        if guild is None:
            return

        bans = [entry async for entry in guild.bans()]

        for ban in bans:
            reason = ban.reason
            user = ban.user

            if reason:
                if "Dyno Autoban" in reason:
                    if datetime.now(timezone.utc) - user.created_at > timedelta(days=14):
                        await asyncio.sleep(10)
                        await guild.unban(user, reason="Auto-unban triggered")

                        log_channel = self.bot.get_channel(TARGET_CHANNEL_ID)
                        if log_channel:
                            embed = discord.Embed(
                                title=f"Case NaN | Unban | {user.name}",
                                color=discord.Color.yellow(),
                                timestamp=datetime.now(timezone.utc)
                            )
                            embed.add_field(name="User", value=f"<@{user.id}>", inline=True)
                            embed.add_field(name="Moderator", value=f"<@!{MODERATOR_ID}>", inline=True)
                            embed.add_field(name="Reason", value="Autounban Rule `Konto na Discordzie dłużej niż 2 tygodnie`", inline=True)
                            embed.set_footer(text=f"ID: {user.id}")
                            await log_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AutoUnban(bot))
