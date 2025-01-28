import discord
from discord.ext import commands
import matplotlib.pyplot as plt
import io
import settings

@commands.hybrid_command(
    brief=f"{settings.PREFIX}matplot - prosty wykres światowej populacji ludzi na świecie"
)
async def pop_matplot(ctx: commands.Context):
    years = [1800, 1815, 1831, 1847, 1863, 1878, 1894, 1910, 1926, 1942, 1957, 1973, 1989, 2005, 2021, 2036, 2052, 2068,
             2084, 2100]
    people = [1.0, 1.4, 2.2, 2.8, 3.3, 3.5, 3.7, 3.8, 4.5, 5.0, 5.6, 5.7, 6.5, 7.2, 7.4, 7.6, 7.8, 8.1, 8.6, 9.0]

    plt.figure(figsize=(6, 4))
    plt.title("Światowa Populacja")
    plt.xlabel("Rok")
    plt.ylabel("Ilość ludzi w miliardach")

    plt.plot(years, people, color="blue", )
    plt.grid()

    io_temp_file = io.BytesIO()
    plt.savefig(io_temp_file, format='png', dpi=300)
    io_temp_file.seek(0)

    await ctx.send(file=discord.File(io_temp_file, "plot.png"))

async def setup(bot: commands.Bot):
    bot.add_command(pop_matplot)