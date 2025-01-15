from discord.ext import commands
import time
import datetime
import settings
import main


@commands.hybrid_command(
    brief=f"{settings.PREFIX}uptime - pokazuje, jak długo bez wywrotki stoi bot na nogach :)",
)
async def uptime(ctx: commands.Context):
    current_time = time.time()
    uptime_seconds = int(round(current_time - main.start_time))
    uptime_duration = str(datetime.timedelta(seconds=uptime_seconds))
    await ctx.send(f'Uptime Bota: {uptime_duration}')


async def setup(bot: commands.Bot):
    bot.add_command(uptime)
