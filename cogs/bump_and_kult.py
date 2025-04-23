import discord
from discord.ext import commands
from datetime import datetime, timedelta
from collections import defaultdict
import settings
import os
import json

# excluded_words = {"bang", "bank", "banan", "band", "jeban", "skuban", "banal", "dzban", "turban",
#                   "banał", "baner", "bania", "banner", "kabanos", "szlaban", "taliban", "odban",
#                   "dban", "bani", "raban", "caliban", "vauban", "banie", "rozjeban", "porąban",
#                   "poraban", "wyraban", "wyrąban"}


class MyOnMessages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldown_time = timedelta(minutes=30)
        self.last_ban_time = defaultdict(lambda: datetime.min)

        # -------------------------------------------------------------------------------------------------------------
        # kult

        self.alpha_swarms_channel = self.bot.get_channel(1130578727730942108)
        self.pheno_role_id = 1136978383381741618
        self.swarms_role_id = 1136020741310132274
        self.alpha_swarms_role_id = 1130578727244402811
        # self.allowed_authors = {1135619477157974127, 691440360605483119}

        # -------------------------------------------------------------------------------------------------------------
        # bump

        self.points = self.load_points()
        self.bump_channel_id = 1255884970761916499
        self.bump_channel = self.bot.get_channel(self.bump_channel_id)
        self.bump_message = "Thx for bumping our Server! We will remind you in 2 hours!"

        # -------------------------------------------------------------------------------------------------------------
        # find_players

        # self.find_players_channel_id = 1253761894750097519
        # self.find_players_channel = self.bot.get_channel(self.find_players_channel_id)

    def load_points(self):
        if os.path.exists(settings.BUMP_POINTS_FILE):
            with open(settings.BUMP_POINTS_FILE, "r") as f:
                return json.load(f)
        else:
            return {}

    def save_points(self, force=False):
        with open(settings.BUMP_POINTS_FILE, "w") as f:
            json.dump(self.points, f, indent=4)

    # ---------------------------------------------------------------------------------------------------
    # last_bumper

    def load_bumper(self):
        with open(settings.LAST_BUMPER_FILE, "r") as f:
            return json.load(f)

    def save_bumper(self, data):
        with open(settings.LAST_BUMPER_FILE, "w") as f:
            json.dump(data, f, indent=4)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.bot.user:
            return

        # if message.guild.id == 1056134342826528808 and not message.author.bot and message.author.id != 304001755912601610:
        #     message_content = message.content.lower()
        #
        #     if "ban" in message_content:
        #
        #         if not any(word in message_content for word in excluded_words):
        #             current_time = datetime.now()
        #             last_time = self.last_ban_time[message.channel.id]
        #
        #             if (current_time - last_time) >= self.cooldown_time:
        #                 self.last_ban_time[message.channel.id] = current_time
        #
        #                 user_to_mention = 304001755912601610
        #                 await message.channel.send(f"<@{user_to_mention}> ktoś napisał ban! 👺")

        # -------------------------------------------------------------------------------------------------------------
        # kult

        if message.guild.id == 1130578727223447582:
            if isinstance(self.alpha_swarms_channel, discord.TextChannel):
                if "@Phenomena" in message.content:
                    await message.channel.send(f"<@&{self.pheno_role_id}>", silent=True)
                elif "@Swarms" in message.content:
                    await message.channel.send(f"<@&{self.swarms_role_id}>", silent=True)
                elif "@Alpha Swarms" in message.content:
                    await message.channel.send(f"<@&{self.alpha_swarms_role_id}>", silent=True)

        # -------------------------------------------------------------------------------------------------------------
        # bump

        if message.channel.id == self.bump_channel_id and message.author.id == 735147814878969968:
            if self.bump_message in message.content:
                if message.mentions:
                    bumper = message.mentions[0]
                    user_id = str(bumper.id)

                    # -----------------------------------------------------------------------------
                    # last bumper

                    bumper_data = self.load_bumper()

                    if bumper_data:
                        if user_id in bumper_data:
                            bumper_data[user_id] += 1
                        else:
                            bumper_data = dict()
                            bumper_data[user_id] = 1
                    else:
                        bumper_data = dict()
                        bumper_data[user_id] = 1

                    self.save_bumper(bumper_data)

                    # ---------------------------------------------------------------------------------
                    # bump

                    self.points[user_id] = self.points.get(user_id, 0) + bumper_data[user_id]
                    self.save_points()

                    # Send the bump confirmation message
                    if isinstance(self.bump_channel, discord.TextChannel):
                        await self.bump_channel.send(
                            f"{bumper.mention} wzrasta Twoja ilość punktów o **+{bumper_data[user_id]}!** (do komendy /top_bump)\n"
                            f"🔥 Bumpujesz nasz serwer **{bumper_data[user_id]}x** pod rząd! 🔥"
                        )

        # -------------------------------------------------------------------------------------------------------------
        # find_players

        # if message.guild.id == 1056134342826528808 and message.channel.id == self.find_players_channel_id:
        #     with open(settings.LAST_MSG_ID, "r") as f:
        #         last_msg_id = f.read().strip()
        #
        #     channel = message.channel
        #     last_message = await channel.fetch_message(int(last_msg_id))
        #
        #     await last_message.delete()
        #
        #     new_message = await channel.send("- **Spinguj rolę gry, wpisz np. @Warframe!** \n"
        #                        "- **Następnie wejdź koniecznie od razu na kanał głosowy (możesz czekać zmutowany)!** \n")
        #
        #     with open(settings.LAST_MSG_ID, "w") as f:
        #         f.write(str(new_message.id))


async def setup(bot):
    await bot.add_cog(MyOnMessages(bot))
