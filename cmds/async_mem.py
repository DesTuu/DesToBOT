from asyncio import Semaphore, gather
from discord.ext import commands
import discord
import settings
import aiohttp
from bs4 import BeautifulSoup
import random

# Limit concurrent requests
CONCURRENT_REQUESTS = 6
semaphore = Semaphore(CONCURRENT_REQUESTS)

urls = [f"https://jbzd.com.pl/str/{i}" for i in range(1, 21)]


async def fetcher(session: aiohttp.ClientSession, url: str) -> list:
    async with semaphore, session.get(url) as response:
        if response.status != 200:
            return []
        text = await response.text()
        soup = BeautifulSoup(text, 'lxml')

        soup_images = soup.findAll('div', attrs={'class': 'article-image article-media-image'})
        soup_titles = soup.find_all("h3", class_="article-title")

        data = []
        for img, title in zip(soup_images, soup_titles):
            try:
                src = img.img['src']
                title_text = title.text.strip()
                data.append((src, title_text))
            except (TypeError, AttributeError):
                continue
        return data


@commands.hybrid_command(
    brief=f"{settings.PREFIX}async_mem - wysyła memy (ulepszona wersja)",
)
async def async_mem(ctx: commands.Context) -> None:
    async with aiohttp.ClientSession() as session:
        tasks = [fetcher(session, url) for url in urls]
        results = await gather(*tasks)

    all_data = [item for result in results for item in result]

    if not all_data:
        await ctx.send("No memes could be fetched. Please try again later.", ephemeral=True)
        return

    random_data = random.sample(all_data, min(len(all_data), 6))

    for image, title in random_data:
        embed = discord.Embed(
            title=title,
            color=ctx.author.color
        )
        embed.set_image(url=image)
        try:
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Error sending embed: {e}", ephemeral=True)


async def setup(bot: commands.Bot):
    bot.add_command(async_mem)
