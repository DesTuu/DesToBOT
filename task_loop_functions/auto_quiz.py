import discord
import random
import json
import asyncio
import settings

async def auto_quiz(bot):
    with open(settings.QUIZ_QUESTIONS_FILE, "r", encoding='utf-8') as f:
        questions = f.readlines()

    quiz_channel = bot.get_channel(1283074891670622358)

    emoji_1 = "1️⃣"
    emoji_2 = "2️⃣"
    emoji_3 = "3️⃣"
    emoji_4 = "4️⃣"

    question = random.choice(questions)
    try:
        question1, question2 = question.split("?")
    except:
        await quiz_channel.send(f"<@&1169392520309002350> wystąpił błąd podczas pytania.\n"
                                f"Pytanie: {question}")
        return

    try:
        _, answer2, answer3, answer4, answer5 = question2.split("#")
    except:
        await quiz_channel.send(f"<@&1169392520309002350> wystąpił błąd podczas ogólnie odpowiedzi.\n"
                                f"Pytanie: {question}")
        return

    quiz_message = await quiz_channel.send(
        f"<@&1283079833437601812>\n"
        f"{question1}?\n{emoji_1}: {answer2.strip('@')}\n{emoji_2}: {answer3.strip('@')}\n{emoji_3}: {answer4.strip('@')}\n{emoji_4}: {answer5.strip('@')}"
    )
    await quiz_message.add_reaction(emoji_1)
    await quiz_message.add_reaction(emoji_2)
    await quiz_message.add_reaction(emoji_3)
    await quiz_message.add_reaction(emoji_4)

    user_reactions = {}

    def check_reaction(reaction, user):
        return (
                user != bot.user
                and str(reaction.emoji) in [emoji_1, emoji_2, emoji_3, emoji_4]
                and reaction.message.id == quiz_message.id
        )

    end_time = asyncio.get_event_loop().time() + 150
    while asyncio.get_event_loop().time() < end_time:
        try:
            reaction, user = await bot.wait_for('reaction_add',
                                                timeout=end_time - asyncio.get_event_loop().time(),
                                                check=check_reaction)

            if user.id in user_reactions:
                await quiz_message.remove_reaction(reaction.emoji, user)
            else:
                user_reactions[user.id] = reaction.emoji

        except asyncio.TimeoutError:
            break

    if "@" in answer2:
        correct_emoji = emoji_1
        correct_answer = answer2
    elif "@" in answer3:
        correct_emoji = emoji_2
        correct_answer = answer3
    elif "@" in answer4:
        correct_emoji = emoji_3
        correct_answer = answer4
    elif "@" in answer5:
        correct_emoji = emoji_4
        correct_answer = answer5
    else:
        await quiz_channel.send(f"<@&1169392520309002350> wystąpił błąd podczas poprawnej odpowiedzi.\n"
                                f"Pytanie: {question}")
        return

    quiz_message = await quiz_channel.fetch_message(quiz_message.id)
    correct_reaction = None
    for reaction in quiz_message.reactions:
        if str(reaction.emoji) == correct_emoji:
            correct_reaction = reaction
            break

    if correct_reaction:
        with open(settings.QUIZ_POINTS_FILE, 'r') as file:
            points = json.load(file)

        users = []
        async for user in correct_reaction.users():
            if not user.bot and user_reactions.get(user.id) == correct_emoji:
                users.append(user)

        winners = []
        if users:
            for user in users:
                winners.append(user.mention)
                if str(user.id) in points:
                    points[str(user.id)] += 1
                else:
                    points[str(user.id)] = 1

            with open(settings.QUIZ_POINTS_FILE, 'w') as file:
                json.dump(points, file, indent=4)

            await quiz_channel.send(
                f"Czas minął! Prawidłowa odpowiedź to **{correct_answer.strip('@').rstrip()}**!\n"
                f"Zwycięzcy: {', '.join(winners)} otrzymują po jednym punkcie do /top_quiz!")
        else:
            await quiz_channel.send(
                f"Czas minął! Prawidłowa odpowiedź to **{correct_answer.strip('@').rstrip()}**!\n"
                f"Nikt nie zdążył wybrać poprawnej odpowiedzi. Spróbuj następnym razem!")
    else:
        await quiz_channel.send("Nie udało się znaleźć poprawnej odpowiedzi. Spróbuj ponownie później.")
