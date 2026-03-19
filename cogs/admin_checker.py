from datetime import datetime, timedelta, timezone
from discord.ext import commands
import discord

GUILD_ID = 1056134342826528808
USER_ID = 354712325053218819

class AdminChecker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_dm(self, content):
        user = await self.bot.fetch_user(USER_ID)
        await user.send(content)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        guild = channel.guild

        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
            user = entry.user

            if user.bot or user.id == USER_ID:
                return

            if user.guild_permissions.administrator:
                await self.send_dm(
                    f"⚠️ Admin {user} usunął kanał: {channel.name}"
                )

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        guild = role.guild

        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete):
            user = entry.user

            if user.bot or user.id == USER_ID:
                return

            if user.guild_permissions.administrator:
                await self.send_dm(
                    f"⚠️ Admin {user} usunął rolę: {role.name}"
                )

async def setup(bot):
    await bot.add_cog(AdminChecker(bot))
