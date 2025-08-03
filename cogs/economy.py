import discord
from discord.ext import commands
import settings
import json
import os
from datetime import datetime, UTC


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.general_channel = self.bot.get_channel(1056276694140452964)
        self.eco_log_channel = self.bot.get_channel(1397620937469464707)
        self.user_mention = ""
        self.eco_points = self.load_eco_points()
        self.hi_words = ("cześć", "czesc", "witam", "dobry", "siem", "witma",
                         "hej", "hi", "yo", "y0", "hey", "elo", "joł",
                         "hola", "merhaba", "salam alejkum", "awe", "ave", "salut", "wave", "bonjour", "hello")
        self.voice_join_times = {}
        self.message_counter = {}

    def load_eco_points(self):
        if os.path.exists(settings.ECO_POINTS_FILE):
            with open(settings.ECO_POINTS_FILE, "r") as f:
                return json.load(f)
        else:
            return {}

    def save_eco_points(self):
        with open(settings.ECO_POINTS_FILE, "w") as f:
            json.dump(self.eco_points, f, indent=4)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author != self.bot.user:

            if message.channel.id == 1056276694140452964:

                # Eco Messages

                # self.message_counter[message.author.id] = self.message_counter.get(message.author.id, 0) + 1
                # if self.message_counter[message.author.id] >= 30:
                #     self.message_counter[message.author.id] = 0
                #     self.eco_points[str(message.author.id)] = self.eco_points.get(str(message.author.id), 0) + 5
                #     self.save_eco_points()
                #     await self.eco_log_channel.send(
                #         f"- **{message.author.display_name}** otrzymuje **+5$** za napisanie 30 wiadomości na kanale {message.channel.mention}! `/top_cash /shop`")


                # Eco Welcome

                if message.author.id == 282859044593598464 and "Witamy" in message.content:
                    try:
                        self.user_mention = message.content.split(" ")[2][:-1]
                    except IndexError:
                        self.user_mention = ""
                        return

                elif self.user_mention and message.author.id != 282859044593598464:
                    self.user_mention = self.user_mention.replace("!", "")
                    if self.user_mention in message.content and any(
                            word in message.content.lower() for word in self.hi_words):
                        self.eco_points[str(message.author.id)] = self.eco_points.get(str(message.author.id), 0) + 10
                        self.save_eco_points()
                        await self.eco_log_channel.send(
                            f"- **{message.author.display_name}** otrzymuje **+10$** za przywitanie nowego ostatniego użytkownika na kanale {message.channel.mention}! `/top_cash /shop`")

                        self.user_mention = ""

            # Eco File

            if message.channel.id in (
                    1249465490439671899, 1349710032656142387, 1269979219451187242, 1269978371543007362,
                    1276875368497680475,
                    1361938010194837587, 1369658691158147152, 1206914818347503646, 1313750634121658429):
                for attachment in message.attachments:
                    if attachment.filename.lower().endswith((".jpg", ".jpeg", ".png", ".mp4", ".mov", ".webm")):
                        self.eco_points[str(message.author.id)] = self.eco_points.get(str(message.author.id), 0) + 3
                        self.save_eco_points()
                        await self.eco_log_channel.send(
                            f"- **{message.author.display_name}** otrzymuje **+3$** za wysłanie obrazu/filmiku na kanale {message.channel.mention}! `/top_cash /shop`")


        elif message.author == self.bot.user:

            # Eco Bumps

            if message.channel.id == 1255884970761916499:
                if "Bumpujesz" in message.content:
                    splitted_bump_msg = message.content.split(" ")
                    bump_user_id = splitted_bump_msg[0]
                    bump_user_id = bump_user_id.replace("<", "")
                    bump_user_id = bump_user_id.replace(">", "")
                    bump_user_id = bump_user_id.replace("@", "")
                    bump_user_id = bump_user_id.replace("!", "")
                    bump_user_fetch = message.guild.get_member(int(bump_user_id))
                    bump_times = splitted_bump_msg[6]
                    bump_times = bump_times.replace("+", "")
                    bump_times = bump_times.replace("*", "")
                    bump_times = int(bump_times.replace("!", ""))
                    bump_times /= 5
                    bump_eco_points = int(10 * (1 + bump_times))
                    self.eco_points[str(bump_user_id)] = self.eco_points.get(str(bump_user_id), 0) + bump_eco_points
                    self.save_eco_points()
                    await self.eco_log_channel.send(
                        f"- **{bump_user_fetch.display_name}** otrzymuje **+{bump_eco_points}$** za bumpowanie Naszego serwera na kanale {message.channel.mention}! `/top_cash /shop`")

            # Eco Inviter

            if message.channel.id == 1164393186626654218:
                if "was invited" in message.content:
                    splitted_inv_msg = message.content.split(" ")
                    inv_user_id = splitted_inv_msg[4]
                    inv_user_id = inv_user_id.replace("<", "")
                    inv_user_id = inv_user_id.replace(">", "")
                    inv_user_id = inv_user_id.replace("@", "")
                    inv_user_id = inv_user_id.replace("!", "")
                    if int(inv_user_id) != int(302050872383242240):
                        inv_user_fetch = message.guild.get_member(int(inv_user_id))
                        self.eco_points[str(inv_user_id)] = self.eco_points.get(str(inv_user_id), 0) + 20
                        self.save_eco_points()
                        await self.eco_log_channel.send(
                            f"- **{inv_user_fetch.display_name}** otrzymuje **+20$** za pomyślne zaproszenie użytkownika na Nasz serwer! `/top_cash /shop`")

    # Eco Voice

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState,
                                    after: discord.VoiceState) -> None:
        if before.channel is None and after.channel is not None:
            if after.channel.id != 1347059456860487690:
                self.voice_join_times[member.id] = datetime.now(UTC)

        elif before.channel is not None and (after.channel is None or before.channel != after.channel):
            if before.channel.id != 1347059456860487690:
                join_time = self.voice_join_times.pop(member.id, None)
                if join_time:
                    time_spent_in_minutes = int((datetime.now(UTC) - join_time).total_seconds() / 60)
                    if time_spent_in_minutes >= 60:
                        self.eco_points[str(member.id)] = self.eco_points.get(str(member.id), 0) + int(
                            time_spent_in_minutes / 12)
                        self.save_eco_points()
                        await self.eco_log_channel.send(
                            f"- **{member.display_name}** otrzymuje **+{int(time_spent_in_minutes / 15)}$** za przebywanie na Naszych kanałach głosowych! `/top_cash /shop`")


async def setup(bot):
    await bot.add_cog(Economy(bot))
