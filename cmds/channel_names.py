from discord.ext import commands
import discord
import settings


@commands.hybrid_command(
    brief=f"{settings.PREFIX}channel_names - zmienia nazwy wszystkich kanałów",
)
async def channel_names(ctx: commands.Context, mode: int) -> None:
    if ctx.author.id == 354712325053218819:
        await ctx.send("Zmieniam nazwy kanałów! Może to trochę potrwać!")
        for channel in ctx.guild.channels:
            if not isinstance(channel, discord.CategoryChannel):
                channel_name = channel.name
                if mode == 1 and "「" in channel_name:
                    await channel.edit(name=f"{channel_name[1]}│{channel_name[3:]}")
                elif mode == 1 and "「" not in channel_name:
                    await channel.edit(name=f"{channel_name[0]}│{channel_name[1:]}")
                elif mode == 2 and "│" in channel_name:
                    await channel.edit(name=f"「{channel_name[0]}」{channel_name[2:]}")
                elif mode == 2 and "│" not in channel_name:
                    await channel.edit(name=f"「{channel_name[0]}」{channel_name[1:]}")
    else:
        await ctx.send("Nie masz permisji do użycia tej komendy!")



async def setup(bot: commands.Bot):
    bot.add_command(channel_names)
