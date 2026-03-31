from datetime import datetime, timedelta, timezone
from discord.ext import commands
import discord
import asyncio

TARGET_GUILD_ID = 1056134342826528808
TARGET_CHANNEL_ID = 1269975070625763378
TARGET_MESSAGE_ID = 1373804035999666278


class InvitesList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, *_):
        guild = self.bot.get_guild(TARGET_GUILD_ID)
        invites = await guild.invites()

        filtered_invites = sorted(
            (
                invite for invite in invites
                if invite.max_age == 0 and invite.max_uses == 0 and invite.uses >= 2
            ),
            key=lambda i: i.uses,
            reverse=True
        )

        if not filtered_invites:
            content = "No valid invites found."
        else:
            content = "# Lista Aktywnych Promotorów Serwera\n\n"
            for invite in filtered_invites:
                inviter = invite.inviter.mention if invite.inviter else "Unknown"
                content += f"- {inviter}(`{invite.code}`) - skorzystało **{invite.uses}** użytkowników\n"


        channel = self.bot.get_channel(TARGET_CHANNEL_ID)
        if not channel:
            return
        message = await channel.fetch_message(TARGET_MESSAGE_ID)
        await message.edit(content=content)


async def setup(bot):
    await bot.add_cog(InvitesList(bot))
