import discord
from discord.ext import commands
import matplotlib.pyplot as plt
import io
import re


class TopMatplot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id == 282859044593598464 and message.embeds:
            embed = message.embeds[0]
            leaderboard_text = embed.description
            if "#6" in leaderboard_text:
                mention_nicknames = re.finditer(r"<@!(\d{17,20})>", leaderboard_text)

                nick_names = []
                for i in mention_nicknames:
                    member_id = int(i.group(1))
                    member = message.guild.get_member(member_id)
                    if member:
                        if re.fullmatch(r"[\w\s]+", member.display_name):
                            nick_names.append(member.display_name)
                        else:
                            nick_names.append(member.name.title())
                    else:
                        nick_names.append(str(member_id))

                experiences = [int(x.group(1)) for x in re.finditer(r"XP: `(\d+)`", leaderboard_text)]

                # ----------------------------------------------------------------------------------------------
                # plot

                plt.figure(figsize=(10, 5))
                plt.bar(nick_names, experiences, color='royalblue')
                plt.xlabel("Użytkownicy")
                plt.ylabel("Punkty aktywności")
                plt.title("Top 10 danej aktywności")
                plt.xticks(rotation=45, ha="right")
                plt.grid(axis='y', linestyle='--', alpha=0.7)

                my_temp_file = io.BytesIO()
                plt.savefig(my_temp_file, format='png', dpi=300, bbox_inches="tight")
                my_temp_file.seek(0)
                plt.close()

                file = discord.File(my_temp_file, filename="leaderboard.png")
                await message.channel.send(file=file)


async def setup(bot: commands.Bot):
    await bot.add_cog(TopMatplot(bot))
