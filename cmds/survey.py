from discord.ext import commands
import settings


@commands.hybrid_command(
    brief=f"{settings.PREFIX}survey treśćankiety - niech zagłosują za lub przeciw w ankiecie",
)
async def survey(ctx: commands.Context, message) -> None:
    msg = await ctx.send(message)
    await msg.add_reaction("\U00002705")
    await msg.add_reaction("❔")
    await msg.add_reaction("\U0000274c")


async def setup(bot: commands.Bot):
    bot.add_command(survey)
