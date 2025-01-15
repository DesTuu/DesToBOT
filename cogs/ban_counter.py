from discord.ext import commands
import settings
import asyncio

TARGET_GUILD_ID = 1056134342826528808
TARGET_CHANNEL_ID = 1279764298499100693


async def update_ban_counter(guild):
    if guild.id != TARGET_GUILD_ID:
        return

    ban_count = 0

    async for _ in guild.bans():
        ban_count += 1

    channel = guild.get_channel(TARGET_CHANNEL_ID)
    await channel.edit(name=f'🔨│Bans: {ban_count}')


class BanCounter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.update_target_guild())

    async def cog_load(self):
        await self.bot.wait_until_ready()
        await self.update_target_guild()

    async def update_target_guild(self):
        await self.bot.wait_until_ready()
        guild = self.bot.get_guild(TARGET_GUILD_ID)
        # await asyncio.sleep(settings.COOLDOWN_DURATION)
        await update_ban_counter(guild)
        # await asyncio.sleep(settings.COOLDOWN_DURATION)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        if guild.id == TARGET_GUILD_ID:
            await update_ban_counter(guild)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        if guild.id == TARGET_GUILD_ID:
            await update_ban_counter(guild)


async def setup(bot):
    await bot.add_cog(BanCounter(bot))
