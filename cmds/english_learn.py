from discord.ext import commands
from googletrans import Translator
import random
import settings


def generate_story():
    with open("db/english_stories.txt", "r", encoding='utf-8') as f:
        stories = f.readlines()
    stories = random.choices(stories, k=5)
    return "".join(stories)


def translate_story(text):
    translator = Translator()
    translated = translator.translate(text, src="en", dest="pl")
    translated = translated.text.replace("...", ".")
    translated = translated.replace(".", ". ")
    translated = translated.replace("?", "? ")
    translated = translated.replace("!", "! ")
    return translated


@commands.hybrid_command(
    brief=f"{settings.PREFIX}english_learn - wyświetla tekst po angielsku i po polsku"
)
async def english_learn(ctx: commands.Context) -> None:
    english_story = generate_story()
    translated_story = translate_story(english_story)
    message = f"{english_story}\n||{translated_story}||"

    await ctx.send(message)


async def setup(bot: commands.Bot):
    bot.add_command(english_learn)
