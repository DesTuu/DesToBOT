from discord.ext import commands
import discord
import time

REQUEST_CHANNEL_ID = 1502586028135809125
VOICE_CATEGORY_ID = 1261094785779765248
EXCLUDED_CHANNEL_ID = 1412829208018812938

ALLOWED_USER_ID = 354712325053218819

# cooldown cache
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


# =========================
# MAIN PANEL
# =========================

class RequestMainView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Przenieś mnie",
        style=discord.ButtonStyle.primary,
        custom_id="req_move"
    )
    async def move_me(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        category = interaction.guild.get_channel(VOICE_CATEGORY_ID)

        if not isinstance(category, discord.CategoryChannel):
            return await interaction.response.send_message(
                "Nie znaleziono kategorii.",
                ephemeral=True
            )

        await interaction.response.send_message(
            "Wybierz kanał voice:",
            view=ChannelSelectView("move", category),
            ephemeral=True
        )

    @discord.ui.button(
        label="Daj mi dostęp",
        style=discord.ButtonStyle.success,
        custom_id="req_access"
    )
    async def access_me(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        category = interaction.guild.get_channel(VOICE_CATEGORY_ID)

        if not isinstance(category, discord.CategoryChannel):
            return await interaction.response.send_message(
                "Nie znaleziono kategorii.",
                ephemeral=True
            )

        await interaction.response.send_message(
            "Wybierz kanał voice:",
            view=ChannelSelectView("access", category),
            ephemeral=True
        )


# =========================
# CHANNEL SELECT VIEW
# =========================

class ChannelSelectView(discord.ui.View):
    def __init__(self, action: str, category: discord.CategoryChannel):
        super().__init__(timeout=60)

        valid_channels = []

        for ch in category.voice_channels:

            # ukryj wybrany kanał
            if ch.id == EXCLUDED_CHANNEL_ID:
                continue

            # ownerzy = osoby z manage_channels
            owners = [
                member for member in ch.members
                if ch.permissions_for(member).manage_channels
            ]

            # pokazuj tylko kanały gdzie owner siedzi
            if owners:
                valid_channels.append(ch)

        # brak aktywnych ownerów
        if not valid_channels:

            options = [
                discord.SelectOption(
                    label="Brak kanałów",
                    value="0"
                )
            ]

            placeholder = "Żaden właściciel nie siedzi na swoim kanale"

        else:

            options = [
                discord.SelectOption(
                    label=ch.name[:100],
                    value=str(ch.id)
                )
                for ch in valid_channels[:25]
            ]

            placeholder = "Wybierz kanał voice"

        self.add_item(ChannelSelect(action, options, placeholder))


# =========================
# CHANNEL SELECT
# =========================

class ChannelSelect(discord.ui.Select):
    def __init__(self, action: str, options, placeholder):
        self.action = action

        super().__init__(
            placeholder=placeholder,
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        if self.values[0] == "0":
            return await interaction.response.send_message(
                "Aktualnie żaden właściciel nie siedzi na swoim kanale prywatnym.",
                ephemeral=True
            )

        channel = interaction.guild.get_channel(int(self.values[0]))
        user = interaction.user

        if not isinstance(channel, discord.VoiceChannel):
            return await interaction.response.send_message(
                "Błąd kanału.",
                ephemeral=True
            )

        if self.action == "move":
            await self.handle_move(interaction, channel, user)
        else:
            await self.handle_access(interaction, channel, user)

    # =========================
    # MOVE SYSTEM
    # =========================

    async def handle_move(self, interaction, channel, user):

        # brak cooldownu jeśli nie siedzi na VC
        if not user.voice or not user.voice.channel:
            return await interaction.response.send_message(
                "Musisz być na kanale głosowym.",
                ephemeral=True
            )

        cd, left = is_on_cooldown(move_cooldown, user.id, 60)

        if cd:
            return await interaction.response.send_message(
                f"⏳ Poczekaj {left}s.",
                ephemeral=True
            )

        managers = get_manage_channel_users(channel)

        if not managers:
            return await interaction.response.send_message(
                "Brak ownera kanału.",
                ephemeral=True
            )

        try:
            await user.move_to(channel)

        except discord.Forbidden:
            return await interaction.response.send_message(
                "Brak permisji do przenoszenia.",
                ephemeral=True
            )

        ping = " ".join(m.mention for m in managers)

        request_channel = interaction.guild.get_channel(REQUEST_CHANNEL_ID)

        if request_channel:
            await request_channel.send(
                f"🔔 {ping}\n"
                f"{user.mention} został przeniesiony do {channel.mention}"
            )

        await interaction.response.send_message(
            f"Przeniesiono do {channel.mention}",
            ephemeral=True
        )

    # =========================
    # ACCESS SYSTEM
    # =========================

    async def handle_access(self, interaction, channel, user):

        # brak cooldownu jeśli nie siedzi na VC
        if not user.voice or not user.voice.channel:
            return await interaction.response.send_message(
                "Musisz być na kanale głosowym.",
                ephemeral=True
            )

        cd, left = is_on_cooldown(access_cooldown, user.id, 60)

        if cd:
            return await interaction.response.send_message(
                f"⏳ Poczekaj {left}s.",
                ephemeral=True
            )

        owners = get_manage_channel_users(channel)

        if not owners:
            return await interaction.response.send_message(
                "Brak osób z Manage Channels.",
                ephemeral=True
            )

        request_channel = interaction.guild.get_channel(REQUEST_CHANNEL_ID)

        if not request_channel:
            return await interaction.response.send_message(
                "Nie znaleziono kanału requestów.",
                ephemeral=True
            )

        await request_channel.send(
            f"🔔 PROŚBA O DOSTĘP\n"
            f"User: {user.mention}\n"
            f"Channel: {channel.mention}\n\n"
            f"Decydują: {' '.join(o.mention for o in owners)}",
            view=AccessDecisionView(user.id, channel.id)
        )

        await interaction.response.send_message(
            "Wysłano request.",
            ephemeral=True
        )


# =========================
# ACCEPT / REJECT
# =========================

class AccessDecisionView(discord.ui.View):
    def __init__(self, user_id: int, channel_id: int):
        super().__init__(timeout=None)

        self.user_id = user_id
        self.channel_id = channel_id

    @discord.ui.button(
        label="Akceptuj",
        style=discord.ButtonStyle.success
    )
    async def accept(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        channel = interaction.guild.get_channel(self.channel_id)
        user = interaction.guild.get_member(self.user_id)

        if channel and user:
            overwrite = channel.overwrites_for(user)
            overwrite.connect = True

            await channel.set_permissions(
                user,
                overwrite=overwrite
            )

        await interaction.message.edit(
            content="✅ Prośba zaakceptowana",
            view=None
        )

        await interaction.response.send_message(
            "OK",
            ephemeral=True
        )

    @discord.ui.button(
        label="Odrzuć",
        style=discord.ButtonStyle.danger
    )
    async def reject(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.message.edit(
            content="❌ Prośba odrzucona",
            view=None
        )

        await interaction.response.send_message(
            "OK",
            ephemeral=True
        )


# =========================
# COMMAND
# =========================

@commands.hybrid_command()
async def button_requests(ctx: commands.Context):

    # tylko Ty możesz tworzyć panel
    if ctx.author.id != ALLOWED_USER_ID:
        return await ctx.send(
            "Brak dostępu.",
            ephemeral=True
        )

    await ctx.send(
        "# Prośby do właścicieli kanałów",
        view=RequestMainView()
    )


# =========================
# SETUP
# =========================

async def setup(bot: commands.Bot):
    bot.add_command(button_requests)
    bot.add_view(RequestMainView())