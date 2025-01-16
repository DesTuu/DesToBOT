import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta, timezone
import settings
import task_loop_functions
from db.my_token import DISCORD_TOKEN
import random
import asyncio
import time

start_time = time.time()

if __name__ == "__main__":
    logger = settings.logging.getLogger('bot')

    intents = discord.Intents().all()
    bot = commands.Bot(command_prefix=settings.PREFIX, intents=intents,
                       heartbeat_timeout=settings.HEARTBEAT_TIMEOUT)

    # with open(settings.QUIZ_QUESTIONS_FILE, "r", encoding='utf-8') as f:
    #     questions = f.readlines()

    # -------------------------------------------------------------------------------------------------------------
    # help command handler

    bot.remove_command('help')


    @commands.hybrid_command(
        brief=f"{settings.PREFIX}help - wyświetla wszystkie komendy i ich opisy"
    )
    async def help(ctx: commands.Context) -> None:
        embed = discord.Embed(title="Available Commands (Dostępne Komendy)", color=discord.Color.blue())
        commands_sorted = sorted(bot.commands, key=lambda cmd: cmd.name)
        for command in commands_sorted:
            if not command.hidden and command.name != 'help':
                embed.add_field(name=f"{settings.PREFIX}{command.name}", value=command.brief, inline=False)
        await ctx.send(embed=embed)


    @bot.event
    async def on_ready():
        logger.info(f"User: {bot.user} (ID: {bot.user.id})")

        # -------------------------------------------------------------------------------------------------------------
        # load_cmds

        for cmd_file in settings.CMD_DIR.glob('*.py'):
            if cmd_file.name != '__init__.py':
                await bot.load_extension(f"cmds.{cmd_file.name[:-3]}")

        bot.add_command(help)

        await bot.tree.sync()

        # -------------------------------------------------------------------------------------------------------------
        # load_cogs

        cog_files = [cog_file for cog_file in settings.COG_DIR.glob('*.py') if cog_file.stem != '__init__']
        for cog_file in cog_files:
            await bot.load_extension(f"cogs.{cog_file.stem}")

        settings.on_ready_message(bot)
        task_loop.start()


    @tasks.loop(hours=13)
    async def task_loop():
        await bot.change_presence(activity=random.choice(settings.activities))

        async def fetch_last_message(channel):
            retries = 5
            while retries > 0:
                try:
                    async for message in channel.history(limit=1):
                        return message
                except discord.errors.HTTPException as e:
                    if e.status == 429:
                        retries -= 1
                        await asyncio.sleep(5 ** (6 - retries))
                    else:
                        raise
            logger.warning(f"Failed to fetch history from {channel.name}")
            return None

        async def process_channel(channel, delta_days, task_function):
            try:
                last_message = await fetch_last_message(channel)
                if last_message:
                    date_now = datetime.now(timezone.utc)
                    created_date = last_message.created_at
                    delta = date_now - created_date
                    if delta > timedelta(days=delta_days):
                        if asyncio.iscoroutinefunction(task_function):
                            result = await task_function()
                        else:
                            result = task_function()
                        if result:
                            await channel.send(result[:2000])
            except Exception as e:
                logger.error(f"Error processing channel {channel.name}: {e}")

        channel_tasks = [
            (bot.get_channel(1280585325978058884), 5, task_loop_functions.auto_concerts),
            (bot.get_channel(1280584215624290414), 2, task_loop_functions.auto_weather),
            (bot.get_channel(1280585526537093243), 4, task_loop_functions.auto_currencies),
            (bot.get_channel(1280585391501742171), 3, task_loop_functions.async_auto_pracuj)
        ]

        for channel, delta_days, task_function in channel_tasks:
            await process_channel(channel, delta_days, task_function)
            await asyncio.sleep(settings.COOLDOWN_DURATION)

        auto_bus_check_update_channel = bot.get_channel(1280584043037196349)
        try:
            await auto_bus_check_update_channel.send(task_loop_functions.auto_bus_check_update()[:2000])
        except (AttributeError, TypeError):
            pass

    @task_loop.before_loop
    async def before_task_loop():
        await bot.wait_until_ready()


    bot.run(DISCORD_TOKEN, root_logger=True)
