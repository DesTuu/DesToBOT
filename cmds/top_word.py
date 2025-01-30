import discord
from discord.ext import commands
import settings
import re
import matplotlib.pyplot as plt
from collections import Counter
import io


@commands.hybrid_command(
    brief=f"{settings.PREFIX}top_word - topka słów z kanału"
)
async def top_word(ctx, limit_of_msgs: int = 500):
    if not 0 < limit_of_msgs < 5000:
        await ctx.send("Wpisana została nieprawidłowa wartość", ephemeral=True)
    await ctx.defer()
    channel_id = False

    if not channel_id:
        messages = [i async for i in ctx.channel.history(limit=limit_of_msgs)]
        all_messages = " ".join([message.content for message in messages])
        all_messages = re.sub(r"[:/?!\.]", "", all_messages)
        pattern = r"\b[a-ząćęłńóśźż]{5,12}\b"
        words = re.findall(pattern, all_messages.lower())
        words_counter = Counter(words)
        most_common = words_counter.most_common(15)

        most_common_words = []
        most_common_counts = []
        for word, count in most_common:
            most_common_words.append(word)
            most_common_counts.append(int(count))

        # --------------------------------------------------------------------------
        # plot

        plt.figure(figsize=(10, 6))
        plt.bar(most_common_words, most_common_counts, color="blue")
        plt.ylabel("Ilość powtórzeń")
        # plt.xlabel("Słowa powyżej 4 znaków")
        plt.title("Top 15 używanych słów powyżej 4 znaków ostatnio")
        plt.yticks(range(0, max(most_common_counts) + 1, (max(most_common_counts) // 10) + 1))
        plt.xticks(rotation=30, ha="right")
        plt.grid(axis="y", linestyle="--", alpha=0.7)

        my_temp_file = io.BytesIO()
        plt.savefig(my_temp_file, format="png", dpi=300)
        my_temp_file.seek(0)
        plt.close()

        my_file = discord.File(my_temp_file, filename="plot_top_word.png")
        await ctx.send(file=my_file)

async def setup(bot: commands.Bot):
    bot.add_command(top_word)
