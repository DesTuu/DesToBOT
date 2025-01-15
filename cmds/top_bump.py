from discord.ext import commands
import discord
import settings
import json
import os


# Load points data from a file
def bump_load_points():
    if os.path.exists(settings.BUMP_POINTS_FILE):
        with open(settings.BUMP_POINTS_FILE, "r") as f:
            return json.load(f)
    return {}


@commands.hybrid_command(
    brief=f"{settings.PREFIX}top10 - top 10 najaktywniejszych bumperów",
)
async def top_bump(ctx: commands.Context, is_private: bool = True) -> None:
    if not isinstance(is_private, bool):
        await ctx.send("Wariant `is_private` przyjmuje tylko wartości True lub False.", ephemeral=True)
        return

    # Load bump points once
    bump_points = bump_load_points()

    # Sort the bump points in-memory and get the top 10
    bump_top_users = sorted(bump_points.items(), key=lambda item: item[1], reverse=True)[:10]

    if bump_top_users:
        description = ""
        top_embed = discord.Embed(title="Top 10 Bumperów", color=discord.Color.blue())
        for idx, (user_id, points) in enumerate(bump_top_users, start=1):
            mention = f"<@{user_id}>"
            description += f"{idx}. {mention} - {points} punktów\n"

            top_embed.description = description

        await ctx.send(embed=top_embed, ephemeral=is_private)
    else:
        await ctx.send("Dane dotyczące użytkowników zostały wyczyszczone lub nastąpił błąd pobierania danych.",
                       ephemeral=True)


async def setup(bot: commands.Bot):
    bot.add_command(top_bump)
