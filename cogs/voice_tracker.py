import discord
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio


class VoiceTracker(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.voice_logs_channel_id = 1309420577269874729
        self.private_channels_category_id = 1261094785779765248
        self.private_channels_archive_category_id = 1488535784003997747
        self.lobby_id = 1412829208018812938

    # 🔹 pobieranie wiadomości z logów (max 10k, tylko 40 dni)
    async def fetch_voice_logs_messages(self):
        channel = self.bot.get_channel(self.voice_logs_channel_id)
        if not channel:
            print("Nie znaleziono kanału logów")
            return []

        messages = []
        limit_date = datetime.now() - timedelta(days=40)

        async for message in channel.history(limit=10000):
            if message.created_at < limit_date:
                break
            messages.append(message)

        return messages

    # 🔹 sprawdzenie czy kanał był używany (po ID w linku)
    def channel_used_in_logs(self, channel_id: int, messages):
        channel_id_str = str(channel_id)

        for message in messages:
            text = message.content or ""

            # obsługa embedów (Dyno często używa embedów)
            if message.embeds:
                embed = message.embeds[0]

                if embed.description:
                    text += embed.description

                if embed.footer and embed.footer.text:
                    text += embed.footer.text

                for field in embed.fields:
                    if field.value:
                        text += field.value

            # 🔥 kluczowe sprawdzenie (ID w linku)
            if f"/{channel_id_str}" in text:
                return True

        return False

    # 🔹 główna logika
    async def process_channels(self):
        log_messages = await self.fetch_voice_logs_messages()

        category = self.bot.get_channel(self.private_channels_category_id)
        archive_category = self.bot.get_channel(self.private_channels_archive_category_id)

        if not category or not archive_category:
            print("Nie znaleziono kategorii")
            return

        for channel in category.voice_channels:

            # pomiń lobby
            if channel.id == self.lobby_id:
                continue

            used = self.channel_used_in_logs(channel.id, log_messages)

            if not used:
                print(f"Przenoszę kanał: {channel.name}")
                try:
                    await channel.edit(category=archive_category)
                    await asyncio.sleep(10)  # mały delay żeby uniknąć rate limit
                except Exception as e:
                    print(f"Błąd przy przenoszeniu {channel.name}: {e}")
            else:
                print(f"OK (aktywny): {channel.name}")

    # 🔹 event bana
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        print(f"Ban wykryty: {user}")

        await self.process_channels()


async def setup(bot):
    await bot.add_cog(VoiceTracker(bot))
