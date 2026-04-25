from discord.ext import commands
import discord
import settings
import time
import asyncio

CHANNEL_ID = 1495334311703085097
OWNER_ID = 354712325053218819

ROLE_MAP = {
    "ranked": 1286456167568113685,
    "clash": 1449462109879406803,
    "normal": 1286456104582123520,
    "aram": 1344395311233372190,
    "tft": 1286456220961472512,
}

active_lobbies = {}


# ========================
# 🔧 CHANNEL CLEANER
# ========================

async def channel_cleaner(bot: commands.Bot):
    await bot.wait_until_ready()

    while not bot.is_closed():
        channel = bot.get_channel(CHANNEL_ID)

        if channel:
            cutoff = discord.utils.utcnow().timestamp() - 1200
            messages = []

            async for msg in channel.history(limit=200):
                messages.append(msg)

            messages = list(reversed(messages))
            to_check = messages[2:]

            for msg in to_check:
                if msg.created_at.timestamp() < cutoff:
                    try:
                        await msg.delete()
                    except:
                        pass

        await asyncio.sleep(60)


# ========================
# 🔧 ROLE SYSTEM
# ========================

def get_roles_from_mode(mode: str):
    mode = mode.lower()
    roles = set()

    if any(x in mode for x in ["solo", "duo", "ranked", "flex"]):
        roles.add(ROLE_MAP["ranked"])

    if "clash" in mode:
        roles.add(ROLE_MAP["clash"])

    if any(x in mode for x in ["draft", "normal", "swift", "szybka"]):
        roles.add(ROLE_MAP["normal"])

    if any(x in mode for x in ["aram", "chaos", "mayhem"]):
        roles.add(ROLE_MAP["aram"])

    if any(x in mode for x in ["tft", "double up"]):
        roles.add(ROLE_MAP["tft"])

    return roles


# ========================
# 🔧 VOICE LINK
# ========================

def get_voice_info(member: discord.Member, guild: discord.Guild):
    if member and member.voice and member.voice.channel:
        return f"https://discord.com/channels/{guild.id}/{member.voice.channel.id}"
    return None


# ========================
# 🔧 LOBBY SYSTEM
# ========================

async def delete_lobby(owner_id: int):
    lobby = active_lobbies.get(owner_id)
    if not lobby:
        return

    try:
        await lobby["message"].delete()
    except:
        pass

    del active_lobbies[owner_id]


async def lobby_expire_task(owner_id: int):
    await asyncio.sleep(600)

    if owner_id in active_lobbies:
        await delete_lobby(owner_id)


class LobbyModal(discord.ui.Modal, title="Tworzenie Lobby"):
    game_mode = discord.ui.TextInput(label="Tryb gry", placeholder="np. aram / flex / ranked / draft / clash")

    def __init__(self, author):
        super().__init__()
        self.author = author

    async def on_submit(self, interaction: discord.Interaction):
        user_id = self.author.id

        if user_id in active_lobbies:
            return await interaction.response.send_message("Masz już aktywne lobby!", ephemeral=True)

        asyncio.create_task(lobby_expire_task(user_id))

        roles = get_roles_from_mode(self.game_mode.value)
        role_mentions = " ".join(f"<@&{r}>" for r in roles)

        mode = self.game_mode.value.title()
        max_players = 2 if any(x in mode for x in ["Solo", "Duo", "Ranked"]) else 5

        expire_time = int(time.time()) + 600

        embed = discord.Embed(
            title="Lobby",
            description=(
                f"Tryb: **{mode}**\n"
                f"Właściciel: <@!{user_id}>\n"
                f"Gracze: 1/{max_players}\n"
                f"Zamykanie Lobby: <t:{expire_time}:R>"
            ),
            color=discord.Color.green()
        )

        view = LobbyView(user_id, max_players)

        owner = interaction.guild.get_member(user_id)
        voice_link = get_voice_info(owner, interaction.guild)

        if voice_link:
            content = f"{role_mentions}\n{voice_link}" if role_mentions else voice_link
        else:
            content = f"{role_mentions}\n## Wejdź na jakiś kanał głosowy!" if role_mentions else "## Wejdź na jakiś kanał głosowy!"

        msg = await interaction.channel.send(content=content, embed=embed, view=view)

        active_lobbies[user_id] = {
            "message": msg,
            "players": [user_id],
            "max": max_players,
            "expire": expire_time,
            "mode": mode
        }

        await interaction.response.send_message("Lobby utworzone!", ephemeral=True)


# ========================
# 🔧 LOBBY VIEW
# ========================

class LobbyView(discord.ui.View):
    def __init__(self, owner_id, max_players):
        super().__init__(timeout=None)
        self.owner_id = owner_id
        self.max_players = max_players

    @discord.ui.button(label="Dołącz", style=discord.ButtonStyle.green, custom_id="lobby_join")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        lobby = active_lobbies.get(self.owner_id)

        if not lobby:
            return await interaction.response.send_message("Lobby nie istnieje.", ephemeral=True)

        if interaction.user.id in lobby["players"]:
            return await interaction.response.send_message("Już jesteś w lobby!", ephemeral=True)

        if len(lobby["players"]) >= lobby["max"]:
            return await interaction.response.send_message("Lobby pełne!", ephemeral=True)

        lobby["players"].append(interaction.user.id)

        await self.update_embed(interaction, lobby)

        if len(lobby["players"]) >= lobby["max"]:
            await self.start_lobby(interaction, lobby)

        await interaction.response.defer()

    @discord.ui.button(label="Opuść", style=discord.ButtonStyle.red, custom_id="lobby_leave")
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        lobby = active_lobbies.get(self.owner_id)

        if interaction.user.id == self.owner_id:
            return await interaction.response.send_message("Właściciel nie może opuścić!", ephemeral=True)

        if interaction.user.id not in lobby["players"]:
            return await interaction.response.send_message("Nie jesteś w lobby!", ephemeral=True)

        lobby["players"].remove(interaction.user.id)

        await self.update_embed(interaction, lobby)
        await interaction.response.defer()

    @discord.ui.button(label="Wystartuj", style=discord.ButtonStyle.blurple, custom_id="lobby_start")
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.owner_id:
            return await interaction.response.send_message("Tylko właściciel!", ephemeral=True)

        lobby = active_lobbies.get(self.owner_id)
        await self.start_lobby(interaction, lobby)

    async def update_embed(self, interaction, lobby):
        players_mentions = "\n".join(f"<@!{uid}>" for uid in lobby["players"])

        embed = lobby["message"].embeds[0]
        embed.description = (
            f"Tryb: **{lobby['mode']}**\n"
            f"Gracze:\n{len(lobby['players'])}/{lobby['max']}\n{players_mentions}\n"
            f"Właściciel: <@!{self.owner_id}>\n"
            f"Dołączać można do: <t:{lobby['expire']}:R>"
        )

        owner = interaction.guild.get_member(self.owner_id)

        if owner and owner.voice and owner.voice.channel:
            content = f"https://discord.com/channels/{interaction.guild.id}/{owner.voice.channel.id}"
        else:
            content = "## Wejdź na jakiś kanał głosowy!"

        await lobby["message"].edit(content=content, embed=embed, view=self)

    async def start_lobby(self, interaction, lobby):
        msg = lobby["message"]
        channel = interaction.guild.get_channel(CHANNEL_ID)

        owner = interaction.guild.get_member(self.owner_id)

        voice_link = ""
        if owner and owner.voice and owner.voice.channel:
            voice_link = f"https://discord.com/channels/{interaction.guild.id}/{owner.voice.channel.id}"

        await msg.delete()

        mentions = " ".join(f"<@!{uid}>" for uid in lobby["players"])

        await channel.send(
            f"### {mentions}\n### Lobby {lobby['mode']} gracza <@!{self.owner_id}> "
            f"{len(lobby['players'])}/{lobby['max']} wystartowało! {voice_link}"
        )

        del active_lobbies[self.owner_id]


# ========================
# 🔧 MAIN PANEL (PERSISTENT)
# ========================

class MainView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Stwórz", style=discord.ButtonStyle.green, custom_id="lobby_create")
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(LobbyModal(interaction.user))

    @discord.ui.button(label="Usuń", style=discord.ButtonStyle.red, custom_id="lobby_delete")
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in active_lobbies:
            return await interaction.response.send_message("Nie masz lobby!", ephemeral=True)

        await delete_lobby(interaction.user.id)
        await interaction.response.send_message("Lobby usunięte!", ephemeral=True)


# ========================
# 🔧 COMMAND
# ========================

@commands.hybrid_command()
async def lobby_setup(ctx: commands.Context):
    await ctx.defer()

    if ctx.author.id != OWNER_ID:
        return await ctx.send("Brak uprawnień!", ephemeral=True)

    channel = ctx.bot.get_channel(CHANNEL_ID)

    await channel.send("# Zarządzanie Lobby", view=MainView())
    await ctx.send("Panel utworzony", ephemeral=True)


# ========================
# 🔧 SETUP
# ========================

async def setup(bot: commands.Bot):
    bot.add_command(lobby_setup)
    bot.add_view(MainView())

    asyncio.create_task(channel_cleaner(bot))