from db import jokes
from discord.ext import commands
import random
import settings


@commands.hybrid_command(
    brief=f"{settings.PREFIX}joke - losuje żart"
)
async def joke(ctx: commands.Context) -> None:
    r = random.choice(jokes.jokes)
    await ctx.send(r)


async def setup(bot: commands.Bot):
    bot.add_command(joke)
