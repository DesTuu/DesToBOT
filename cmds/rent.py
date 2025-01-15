from discord.ext import commands
import settings


@commands.hybrid_command(
    brief=f"{settings.PREFIX}rent - automatyczne obliczanie wartości na pewnym kanale [DesTu only]",
    hidden=False,
    guilds_id=[1056134342826528808]
)
async def rent(ctx: commands.Context, amount: int = 1200) -> None:
    if ctx.author.id == 354712325053218819:
        async for msg in ctx.channel.history(limit=1):
            if "Amount: " in msg.content:
                bot_message = msg.content
                last_total = bot_message[:-2].split()[-1]

        total_amount = int(last_total) + amount
        rent_string = f"- Amount: {amount}zł\n\n" \
                      f"- Increasing total amount: {total_amount}zł"

        await ctx.send(rent_string)


async def setup(bot: commands.Bot):
    bot.add_command(rent)
