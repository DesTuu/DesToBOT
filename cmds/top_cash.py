from discord.ext import commands
import discord
import settings
import json
import os


def eco_load_points():
    if os.path.exists(settings.ECO_POINTS_FILE):
        with open(settings.ECO_POINTS_FILE, "r") as f:
            return json.load(f)
    return {}


@commands.hybrid_command(
    brief=f"{settings.PREFIX}top_cash - Top 10 Bogaczy",
)
async def top_cash(ctx: commands.Context, is_private: bool = True) -> None:
    if not isinstance(is_private, bool):
        await ctx.send("Wariant `is_private` przyjmuje tylko wartości True lub False.", ephemeral=True)
        return

    eco_points = eco_load_points()

    eco_top_users = sorted(eco_points.items(), key=lambda item: item[1], reverse=True)[:10]

    if eco_top_users:
        description = ""
        top_embed = discord.Embed(title="Top 10 Bogaczy", color=discord.Color.blue())
        for idx, (user_id, points) in enumerate(eco_top_users, start=1):
            mention = f"<@{user_id}>"
            description += f"{idx}. {mention} - {points}$\n"

            top_embed.description = description

        await ctx.send(embed=top_embed, ephemeral=is_private)
    else:
        await ctx.send("Dane dotyczące użytkowników zostały wyczyszczone lub nastąpił błąd pobierania danych.",
                       ephemeral=True)


async def setup(bot: commands.Bot):
    bot.add_command(top_cash)
