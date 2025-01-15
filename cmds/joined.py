from discord.ext import commands
import discord
import settings


@commands.hybrid_command(
    brief=f"{settings.PREFIX}joined nickname - wyświetla kiedy dany użytkownik dołączył na serwer"
)
async def joined(ctx: commands.Context, user: discord.Member) -> None:
    m = str(user.joined_at)[:19]
    await ctx.send(f"{str(user).title()} dołączył na serwer: {m}")


async def setup(bot: commands.Bot):
    bot.add_command(joined)
