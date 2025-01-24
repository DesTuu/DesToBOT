from discord.ext import commands
import settings


@commands.hybrid_command(
    brief=f"{settings.PREFIX}say treśćwiadomości - przekazujesz wiadomość jako bot",
)
async def say(ctx: commands.Context, message) -> None:
    await ctx.send(message)


async def setup(bot: commands.Bot):
    bot.add_command(say)
