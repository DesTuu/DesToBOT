from discord.ext import commands
import discord
import settings
from googletrans import Translator


@commands.hybrid_command(
    brief=f"{settings.PREFIX}say treśćwiadomości - przekazujesz wiadomość jako destobot",
)
async def translate(ctx: commands.Context, target_language: str = "polish", *, text: str) -> None:
    try:
        translator = Translator()
        translated = translator.translate(text, dest=target_language)
        translated_text = translated.text
        source_language = translated.src

        embed = discord.Embed(
            title="Tłumaczenie",
            description=f"Tekst przetłumaczony z `{source_language}` na `{target_language}`:",
            color=discord.Color.blue()
        )
        embed.add_field(name="Oryginalny tekst", value=text, inline=False)
        embed.add_field(name="Przetłumaczony tekst", value=translated_text, inline=False)

        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Wystąpił błąd podczas tłumaczenia: {e}")


async def setup(bot: commands.Bot):
    bot.add_command(translate)
