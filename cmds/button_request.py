from discord.ext import commands
import discord
import time
import asyncio

REQUEST_CHANNEL_ID = 1502586028135809125
VOICE_CATEGORY_ID = 1261094785779765248
EXCLUDED_CHANNEL_ID = 1412829208018812938

ALLOWED_USER_ID = 354712325053218819

move_cooldown = {}
access_cooldown = {}


# =========================
# HELPERS
# =========================

def is_on_cooldown(cache: dict, user_id: int, cooldown: int = 60):
    now = time.time()
    last = cache.get(user_id, 0)

    if now - last < cooldown:
        return True, int(cooldown - (now - last))

    cache[user_id] = now
    return False, 0


def get_manage_channel_users(channel: discord.VoiceChannel):
    return [
        member for member in channel.members
        if channel.permissions_for(member).manage_channels
    ]


def has_connect_permission(channel: discord.VoiceChannel, user: discord.Member):
    return channel.permissions_for(user).connect


# =========================
# MAIN PANEL
# =========================

class RequestMainView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Przenieś mnie", style=discord.ButtonStyle.primary, custom_id="req_move")
    async def move_me(self, interaction, button):

        category = interaction.guild.get_channel(VOICE_CATEGORY_ID)

        if not isinstance(category, discord.CategoryChannel):
            return await interaction.response.send_message("Brak kategorii", ephemeral=True)

        await interaction.response.send_message(
            "Wybierz kanał:",
            view=ChannelSelectView("move", category),
            ephemeral=True
        )

    @discord.ui.button(label="Daj mi dostęp", style=discord.ButtonStyle.success, custom_id="req_access")
    async def access_me(self, interaction, button):

        category = interaction.guild.get_channel(VOICE_CATEGORY_ID)

        if not isinstance(category, discord.CategoryChannel):
            return await interaction.response.send_message("Brak kategorii", ephemeral=True)

        await interaction.response.send_message(
            "Wybierz kanał:",
            view=ChannelSelectView("access", category),
            ephemeral=True
        )


# =========================
# SELECT VIEW
# =========================

class ChannelSelectView(discord.ui.View):
    def __init__(self, action, category):
        super().__init__(timeout=60)

        valid_channels = []

        for ch in category.voice_channels:
            if ch.id == EXCLUDED_CHANNEL_ID:
                continue

            if get_manage_channel_users(ch):
                valid_channels.append(ch)

        if not valid_channels:
            options = [discord.SelectOption(label="Brak kanałów", value="0")]
        else:
            options = [
                discord.SelectOption(label=ch.name[:100], value=str(ch.id))
                for ch in valid_channels[:25]
            ]

        self.add_item(ChannelSelect(action, options))


# =========================
# SELECT
# =========================

class ChannelSelect(discord.ui.Select):
    def __init__(self, action, options):
        self.action = action

        super().__init__(
            placeholder="Wybierz kanał",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction):

        if self.values[0] == "0":
            return await interaction.response.send_message("Brak kanałów", ephemeral=True)

        channel = interaction.guild.get_channel(int(self.values[0]))
        user = interaction.user

        if self.action == "move":
            await self.handle_move(interaction, channel, user)
        else:
            await self.handle_access(interaction, channel, user)

    # =========================
    # MOVE
    # =========================

    async def handle_move(self, interaction, channel, user):

        if has_connect_permission(channel, user):
            return await interaction.response.send_message("Masz już dostęp", ephemeral=True)

        if not user.voice:
            return await interaction.response.send_message("Wejdź na VC", ephemeral=True)

        cd, left = is_on_cooldown(move_cooldown, user.id)

        if cd:
            return await interaction.response.send_message(f"⏳ {left}s", ephemeral=True)

        await user.move_to(channel)

        ch = interaction.guild.get_channel(REQUEST_CHANNEL_ID)
        await ch.send(f"✅ {user.mention} → {channel.mention}")

        await interaction.response.send_message("OK", ephemeral=True)

    # =========================
    # ACCESS
    # =========================

    async def handle_access(self, interaction, channel, user):

        if has_connect_permission(channel, user):
            return await interaction.response.send_message("Masz już dostęp", ephemeral=True)

        if not user.voice:
            return await interaction.response.send_message("Wejdź na VC", ephemeral=True)

        cd, left = is_on_cooldown(access_cooldown, user.id)

        if cd:
            return await interaction.response.send_message(f"⏳ {left}s", ephemeral=True)

        view = AccessDecisionView(user.id, channel.id)

        ch = interaction.guild.get_channel(REQUEST_CHANNEL_ID)

        msg = await ch.send(
            f"🔔 PROŚBA\n{user.mention} → {channel.mention}",
            view=view
        )

        view.message = msg

        await interaction.response.send_message("Wysłano", ephemeral=True)


# =========================
# ACCEPT / REJECT
# =========================

class AccessDecisionView(discord.ui.View):
    def __init__(self, user_id, channel_id):
        super().__init__(timeout=600)  # ✅ 10 min
        self.user_id = user_id
        self.channel_id = channel_id
        self.message = None

    def is_owner(self, interaction):
        channel = interaction.guild.get_channel(self.channel_id)
        return channel.permissions_for(interaction.user).manage_channels

    # ✅ AUTO DELETE
    async def on_timeout(self):
        try:
            if self.message:
                await self.message.delete()
        except:
            pass

    @discord.ui.button(label="Akceptuj", style=discord.ButtonStyle.success)
    async def accept(self, interaction, button):

        if not self.is_owner(interaction):
            return await interaction.response.send_message("Nie jesteś ownerem", ephemeral=True)

        channel = interaction.guild.get_channel(self.channel_id)
        user = interaction.guild.get_member(self.user_id)

        overwrite = channel.overwrites_for(user)
        overwrite.connect = True

        await channel.set_permissions(user, overwrite=overwrite)

        await interaction.message.edit(
            content=(
                f"✅ Zaakceptowano\n"
                f"👤 Decyzja: {interaction.user.mention}\n"
                f"📥 Dostęp otrzymał: <@{self.user_id}>"
            ),
            view=None
        )

        await interaction.response.send_message("OK", ephemeral=True)

    @discord.ui.button(label="Odrzuć", style=discord.ButtonStyle.danger)
    async def reject(self, interaction, button):

        if not self.is_owner(interaction):
            return await interaction.response.send_message("Nie jesteś ownerem", ephemeral=True)

        await interaction.message.edit(
            content=(
                f"❌ Odrzucono\n"
                f"👤 Decyzja: {interaction.user.mention}\n"
                f"📥 Dotyczyło: <@{self.user_id}>"
            ),
            view=None
        )

        await interaction.response.send_message("OK", ephemeral=True)


# =========================
# COMMAND
# =========================

@commands.hybrid_command()
async def button_requests(ctx):

    if ctx.author.id != ALLOWED_USER_ID:
        return await ctx.send("Brak dostępu", ephemeral=True)

    await ctx.send("# Panel requestów", view=RequestMainView())


# =========================
# SETUP
# =========================

async def setup(bot):
    bot.add_command(button_requests)
    bot.add_view(RequestMainView())