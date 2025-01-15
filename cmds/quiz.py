from discord.ext import commands
import random
import settings


@commands.hybrid_command(
    brief=f"{settings.PREFIX}quiz - zadaje Ci pytanie z quizu",
)
async def quiz(ctx: commands.Context, is_private: bool = True) -> None:
    emoji_1 = "1️⃣"
    emoji_2 = "2️⃣"
    emoji_3 = "3️⃣"
    emoji_4 = "4️⃣"

    with open(settings.QUIZ_QUESTIONS_FILE, "r", encoding='utf-8') as f:
        questions = f.readlines()

    question = random.choice(questions)
    try:
        question1, question2 = question.split("?")
    except:
        await ctx.send(f"Wystąpił błąd podczas pytania.\n"
                       f"Pytanie: {question}")
        return

    try:
        _, answer2, answer3, answer4, answer5 = question2.split("#")
    except:
        await ctx.send(f"Wystąpił błąd podczas ogólnie odpowiedzi.\n"
                       f"Pytanie: {question}")
        return

    if "@" in answer2:
        answer2 = f"**{answer2.strip('@')}**"
    elif "@" in answer3:
        answer3 = f"**{answer3.strip('@')}**"
    elif "@" in answer4:
        answer4 = f"**{answer4.strip('@')}**"
    elif "@" in answer5:
        answer5 = f"**{answer5.strip('@')}**"
    else:
        await ctx.send(f"Wystąpił błąd podczas poprawnej odpowiedzi.\n"
                       f"Pytanie: {question}")
        return

    await ctx.send(
        f"{question1}?\n{emoji_1}: {answer2}\n{emoji_2}: {answer3}\n{emoji_3}: {answer4}\n{emoji_4}: {answer5}",
        ephemeral=True
    )


async def setup(bot: commands.Bot):
    bot.add_command(quiz)
