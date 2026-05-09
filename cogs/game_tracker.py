from datetime import datetime, timezone

import discord
from discord.ext import commands, tasks

TARGET_GUILD_ID = 1056134342826528808
TARGET_CHANNEL_ID = 1495334311703085097
MESSAGE_ID = 1502579241664122920

ROLES_ID = [
    1448747955325636804,
    1315707236776935474,
    1408897749654442004
]


class GameTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_game_feed.start()

    def cog_unload(self):
        self.update_game_feed.cancel()

    @tasks.loop(minutes=10)
    async def update_game_feed(self):
        guild = self.bot.get_guild(TARGET_GUILD_ID)

        if guild is None:
            return

        channel = guild.get_channel(TARGET_CHANNEL_ID)

        if channel is None:
            return

        try:
            message = await channel.fetch_message(MESSAGE_ID)
        except discord.NotFound:
            return

        lol_lines = []
        other_lines = []

        for member in guild.members:
            if member.bot:
                continue

            has_role = any(role.id in ROLES_ID for role in member.roles)
            if not has_role:
                continue

            if not member.activities:
                continue

            for activity in member.activities:

                if isinstance(activity, discord.CustomActivity):
                    continue

                if isinstance(activity, (discord.Game, discord.Activity)):

                    game_name = activity.name
                    if not game_name:
                        continue

                    game_lower = game_name.lower()

                    started_text = "nieznany czas"

                    if activity.start:
                        now = datetime.now(timezone.utc)
                        delta = now - activity.start

                        total_seconds = int(delta.total_seconds())
                        hours = total_seconds // 3600
                        minutes = (total_seconds % 3600) // 60

                        if hours > 0:
                            started_text = f"{hours}h {minutes}m"
                        else:
                            started_text = f"{minutes}m"

                    line = f"- <@!{member.id}> w grze **{game_name}** od `{started_text}`"

                    # klasyfikacja LoL vs reszta
                    if "league of legends" in game_lower or "lol" == game_lower:
                        lol_lines.append(line)
                    else:
                        other_lines.append(line)

                    break

        content = "# League of Legends\n||[Voice Gold+]||\n"

        if lol_lines:
            content += "\n".join(lol_lines)
        else:
            content += "Brak graczy w League of Legends."

        content += "\n\n# Inne Aktywności\n||[Voice Gold+]||\n"

        if other_lines:
            content += "\n".join(other_lines)
        else:
            content += "Brak innych aktywności."

        await message.edit(content=content[:2000])

    @update_game_feed.before_loop
    async def before_update_game_feed(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(GameTracker(bot))
