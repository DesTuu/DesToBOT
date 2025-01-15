from discord.ext import commands
import discord
import settings


@commands.hybrid_command(
    brief=f"{settings.PREFIX}sort id_kategorii - sortuje alfabetycznie kanały w danej kategorii [DesTu only]"
)
async def sort(ctx: commands.Context, category_id_str: str) -> None:
    await ctx.defer()
    
    if ctx.author.id == 354712325053218819:
        try:
            category_id = int(category_id_str)
        except ValueError:
            await ctx.send("Podaj prawidłowe ID kategorii.", ephemeral=True)
            return
        category = discord.utils.get(ctx.guild.categories, id=category_id)
        if category:
            sorted_channels = sorted(category.channels, key=lambda c: c.name.split('│')[-1].strip())
            await ctx.send(f"Zaczęto sortować kanały w kategorii **{category.name}**. Może to długo potrwać.",
                           ephemeral=True)
            for index, channel in enumerate(sorted_channels):
                await channel.edit(position=index)


async def setup(bot: commands.Bot):
    bot.add_command(sort)
