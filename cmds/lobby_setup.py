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

active_lobbies = {}  # user_id: lobby_data

async def delete_lobby(owner_id: int):
    lobby = active_lobbies.get(owner_id)
    if not lobby:
        return

    msg = lobby["message"]

    try:
        await msg.delete()
    except:
        pass

    del active_lobbies[owner_id]

async def lobby_expire_task(owner_id: int):
    await asyncio.sleep(600)

    if owner_id not in active_lobbies:
        return

    await delete_lobby(owner_id)

class LobbyModal(discord.ui.Modal, title="Tworzenie Lobby"):
    game_mode = discord.ui.TextInput(label="Tryb gry", placeholder="np. aram / flex / ranked / draft / clash / urf")
    # players = discord.ui.TextInput(label="Ilość osób", placeholder="max 5 (solo/duo = 2)")

    def __init__(self, author):
        super().__init__()
        self.author = author

    async def on_submit(self, interaction: discord.Interaction):
        user_id = self.author.id

        if user_id in active_lobbies:
            await interaction.response.send_message("Masz już aktywne lobby!", ephemeral=True)
            return

        asyncio.create_task(lobby_expire_task(user_id))

        roles = get_roles_from_mode(self.game_mode.value)
        role_mentions = " ".join(f"<@&{role_id}>" for role_id in roles)

        # try:
        #     players_input = int(self.players.value)
        # except:
        #     await interaction.response.send_message("Podaj poprawną liczbę!", ephemeral=True)
        #     return

        mode = self.game_mode.value.title()

        if any(x in mode for x in ["Solo", "Duo", "Ranked", "Rankingowy"]):
            max_players = 2
        else:
            max_players = 5

        expire_time = int(time.time()) + 600

        embed = discord.Embed(
            title="Lobby",
            description=(
                f"Tryb: **{self.game_mode.value.title()}**\n"
                f"Właściciel: <@!{user_id}>\n"
                f"Gracze: 1/{max_players}\n"
                f"Zamykanie Lobby: <t:{expire_time}:R>"
            ),
            color=discord.Color.green()
        )

        view = LobbyView(user_id, max_players)

        content = role_mentions if role_mentions else None

        msg = await interaction.channel.send(
            content=content,
            embed=embed,
            view=view
        )

        active_lobbies[user_id] = {
            "message": msg,
            "players": [user_id],
            "max": max_players,
            "expire": expire_time,
            "mode": self.game_mode.value.title()
        }

        await interaction.response.send_message("Lobby utworzone!", ephemeral=True)


class LobbyView(discord.ui.View):
    def __init__(self, owner_id, max_players):
        super().__init__(timeout=None)
        self.owner_id = owner_id
        self.max_players = max_players

    @discord.ui.button(label="Dołącz", style=discord.ButtonStyle.green, custom_id="join_btn")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        lobby = active_lobbies.get(self.owner_id)

        if not lobby:
            await interaction.response.send_message("Lobby nie istnieje.", ephemeral=True)
            return

        if interaction.user.id in lobby["players"]:
            await interaction.response.send_message("Już jesteś w lobby!", ephemeral=True)
            return

        if len(lobby["players"]) >= lobby["max"]:
            await interaction.response.send_message("Lobby pełne!", ephemeral=True)
            return

        lobby["players"].append(interaction.user.id)

        await self.update_embed(lobby)

        if len(lobby["players"]) >= lobby["max"]:
            await self.start_lobby(interaction, lobby)

        await interaction.response.defer()

    @discord.ui.button(label="Opuść", style=discord.ButtonStyle.red, custom_id="leave_btn")
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        lobby = active_lobbies.get(self.owner_id)

        if interaction.user.id == self.owner_id:
            await interaction.response.send_message("Właściciel nie może opuścić lobby!", ephemeral=True)
            return

        if interaction.user.id not in lobby["players"]:
            await interaction.response.send_message("Nie jesteś w lobby!", ephemeral=True)
            return

        lobby["players"].remove(interaction.user.id)

        await self.update_embed(lobby)
        await interaction.response.defer()

    @discord.ui.button(label="Wystartuj", style=discord.ButtonStyle.blurple, custom_id="start_btn")
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message("Tylko właściciel może wystartować!", ephemeral=True)
            return

        lobby = active_lobbies.get(self.owner_id)
        await self.start_lobby(interaction, lobby)

    async def update_embed(self, lobby):
        players_mentions = "\n".join(f"<@!{uid}>" for uid in lobby["players"])
        players_text = f"{len(lobby['players'])}/{lobby['max']}\n{players_mentions}"

        embed = lobby["message"].embeds[0]
        embed.description = (
                embed.description.split("\n")[0] + "\n" +
                f"Gracze:\n{players_text}\n"
                f"Właściciel: <@!{self.owner_id}>\n"
                f"Dołączać można do: <t:{lobby['expire']}:R>"
        )

        await lobby["message"].edit(embed=embed, view=self)

    async def start_lobby(self, interaction, lobby):
        msg = lobby["message"]

        channel = interaction.guild.get_channel(CHANNEL_ID)

        owner = interaction.guild.get_member(self.owner_id)

        voice_link = ""
        if owner and owner.voice and owner.voice.channel:
            voice_link = f" https://discord.com/channels/{interaction.guild.id}/{owner.voice.channel.id}"

        await msg.delete()

        mentions = " ".join(f"<@!{uid}>" for uid in lobby["players"])

        await channel.send(
            f"### {mentions}\n### Lobby {lobby['mode']} gracza <@!{self.owner_id}> {len(lobby['players'])}/{lobby['max']} wystartowało! {voice_link}"
        )

        del active_lobbies[self.owner_id]


class MainView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Stwórz", style=discord.ButtonStyle.green, custom_id="create_lobby")
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(LobbyModal(interaction.user))

    @discord.ui.button(label="Usuń", style=discord.ButtonStyle.red, custom_id="delete_lobby")
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        lobby = active_lobbies.get(interaction.user.id)

        if not lobby:
            await interaction.response.send_message("Nie masz lobby!", ephemeral=True)
            return

        await delete_lobby(interaction.user.id)
        await interaction.response.send_message("Lobby usunięte!", ephemeral=True)


@commands.hybrid_command(brief=f"{settings.PREFIX}lobby_setup - administracyjny panel lobby")
async def lobby_setup(ctx: commands.Context):
    await ctx.defer()

    if ctx.author.id != OWNER_ID:
        await ctx.send("Przykro mi, nie masz uprawnień!", ephemeral=True)
        return

    channel = ctx.bot.get_channel(CHANNEL_ID)

    view = MainView()
    msg = await channel.send("# Zarządzanie Lobby", view=view)

    await ctx.send(f"Panel utworzony", ephemeral=True)


async def setup(bot: commands.Bot):
    bot.add_command(lobby_setup)

    # ważne dla 24/7 działania
    bot.add_view(MainView())
    bot.add_view(LobbyView(0, 0))