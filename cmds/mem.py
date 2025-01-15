from discord.ext import commands
from bs4 import BeautifulSoup
import requests
import settings
import random
import discord


@commands.hybrid_command(
    brief=f"{settings.PREFIX}mem - losuje 5 memów z jbzd.com.pl"
)
async def mem(ctx: commands.Context) -> None:
    await ctx.defer()

    A = []
    mem_set = []
    for site in range(9):
        url = f"https://jbzd.com.pl/str/{site}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        match = soup.findAll('div', attrs={'class': 'article-image article-media-image'})
        for i in match:
            try:
                src = i.img['src']
                A.append(src)
            except TypeError:
                pass

    embed = discord.Embed(
        title="",
        description="Oto jeden z najnowszych memów ze strony jbzd.com.pl:",
        color=ctx.author.color
    )
    for i in range(6):
        mem = random.choice(A)
        mem_set.append(mem)

    mem_set = set(mem_set)

    for i in mem_set:
        embed.set_image(url=i)
        try:
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(e)


async def setup(bot: commands.Bot):
    bot.add_command(mem)
