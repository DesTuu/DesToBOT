import discord
from discord.ext import commands
import settings


@commands.hybrid_command(
    brief=f"{settings.PREFIX}voteban użytkownik - żartobliwa komenda do banowania ziomka",
)
async def vote_ban(ctx: commands.Context, member: discord.Member) -> None:
    msg = await ctx.send(f"Głosowanie za zbanowaniem użytkownika {member.mention} z serwera!")
    await msg.add_reaction("\U00002705")
    await msg.add_reaction("❔")
    await msg.add_reaction("\U0000274c")


async def setup(bot: commands.Bot):
    bot.add_command(vote_ban)
