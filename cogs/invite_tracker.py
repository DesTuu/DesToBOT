from discord.ext import commands
import discord
import asyncio

TARGET_GUILD_ID = 1056134342826528808
TARGET_CHANNEL_ID = 1164393186626654218

class InviteTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invite_cache = {}
        self.bot.loop.create_task(self.setup_cache())

    async def cog_load(self):
        await self.bot.wait_until_ready()
        await self.setup_cache()

    async def setup_cache(self):
        await self.bot.wait_until_ready()
        guild = self.bot.get_guild(TARGET_GUILD_ID)
        if guild:
            invites = await guild.invites()
            self.invite_cache[guild.id] = invites

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id != TARGET_GUILD_ID:
            return

        guild = member.guild
        try:
            new_invites = await guild.invites()
        except discord.Forbidden:
            return

        old_invites = self.invite_cache.get(guild.id, [])
        old_invite_uses = {invite.code: invite.uses for invite in old_invites}

        inviter = None
        used_invite = None

        for invite in new_invites:
            if invite.code in old_invite_uses:
                if invite.uses > old_invite_uses[invite.code]:
                    inviter = invite.inviter
                    used_invite = invite
                    break
            else:
                if invite.uses > 0:
                    inviter = invite.inviter
                    used_invite = invite
                    break

        self.invite_cache[guild.id] = new_invites

        channel = guild.get_channel(TARGET_CHANNEL_ID)
        if inviter and channel:
            await channel.send(
                f"{member.mention} was invited by {inviter.mention} using invite `{used_invite.code}`. +",
                allowed_mentions=discord.AllowedMentions.none()
            )
        elif channel:
            await channel.send(
                f"{member.mention} joined, but inviter could not be determined. ?",
                allowed_mentions=discord.AllowedMentions.none()
            )

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        guild = invite.guild
        if guild.id == TARGET_GUILD_ID:
            invites = await guild.invites()
            self.invite_cache[guild.id] = invites

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        guild = invite.guild
        if guild.id == TARGET_GUILD_ID:
            invites = await guild.invites()
            self.invite_cache[guild.id] = invites

async def setup(bot):
    await bot.add_cog(InviteTracker(bot))
