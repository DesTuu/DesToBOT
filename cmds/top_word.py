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
async def top_word(ctx, channel_id: str = ""):
    await ctx.defer()

    if not channel_id:
        messages = [i async for i in ctx.channel.history(limit=1000)]
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

        plt.figure(figsize=(10, 5))
        plt.bar(most_common_words, most_common_counts, color="blue")
        plt.ylabel("Krotność powtarzania")
        plt.title("Top 15 używanych słów w ostatnim czasie")
        plt.gca().set_yticks(range(0, max(most_common_counts) + 1, 5))
        plt.xticks(rotation=45, ha="right")
        plt.grid(axis="y", linestyle="--", alpha=0.7)

        my_temp_file = io.BytesIO()
        plt.savefig(my_temp_file, format="png", dpi=300)
        my_temp_file.seek(0)
        plt.close()

        my_file = discord.File(my_temp_file, filename="plot_top_word.png")
        await ctx.send(file=my_file)

async def setup(bot: commands.Bot):
    bot.add_command(top_word)
