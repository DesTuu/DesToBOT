from discord.ext import commands
import discord
import random
from db import gifs
import settings
import requests


@commands.hybrid_command(
    brief=f"{settings.PREFIX}poke nickogólnydiscorda - zaczepiasz wybranego użytkownika gifem"
)
async def poke(ctx: commands.Context, user: discord.Member) -> None:
    embed = discord.Embed(
        title="",
        description=f"{ctx.author.mention} zaczepia {user.mention}!",
        color=ctx.author.color
    )

    randomgif = random.choice(gifs.poke)
    response = requests.get(randomgif, headers={"User-Agent": "Mozilla/5.0"})
    while response.url != randomgif:
        randomgif = random.choice(gifs.poke)
    embed.set_image(url=randomgif)
    await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    bot.add_command(poke)
