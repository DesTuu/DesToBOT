import discord
from discord.ext import commands
from matplotlib.projections import projection_registry

import settings
import json
import os


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.general_channel = self.bot.get_channel(1056276694140452964)
        self.user_mention = ""
        self.eco_points = self.load_eco_points()

    def load_eco_points(self):
        if os.path.exists(settings.ECO_POINTS_FILE):  # poprawiono na ECO_POINTS_FILE
            with open(settings.ECO_POINTS_FILE, "r") as f:
                return json.load(f)
        else:
            return {}

    def save_eco_points(self):
        with open(settings.ECO_POINTS_FILE, "w") as f:
            json.dump(self.eco_points, f, indent=4)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.bot.user:
            return
        if message.channel.id != 1056276694140452964:
            return

        if message.author.id == 282859044593598464 and "Witamy" in message.content:
            try:
                self.user_mention = message.content.split(" ")[2][:-1]
            except IndexError:
                self.user_mention = ""
                return

        elif self.user_mention and message.author.id != 282859044593598464:
            self.user_mention = self.user_mention.replace("!", "")
            if self.user_mention in message.content:
                user_id = str(message.author.id)
                self.eco_points[user_id] = self.eco_points.get(user_id, 0) + 10
                self.save_eco_points()
                await message.channel.send(
                    f"{message.author.mention} **+10$** dolarów za przywitanie nowego użytkownika! /cash"
                )

                self.user_mention = ""

async def setup(bot):
    await bot.add_cog(Welcome(bot))
