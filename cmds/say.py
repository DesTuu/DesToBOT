from discord.ext import commands
import settings


@commands.hybrid_command(
    brief=f"{settings.PREFIX}say treśćwiadomości - przekazujesz wiadomość jako destobot",
)
async def say(ctx: commands.Context, message: str) -> None:
    await ctx.send(message)


async def setup(bot: commands.Bot):
    bot.add_command(say)
