from discord.ext import commands
import discord
import settings
import json
import os
import asyncio

options_to_buy = (
    "Grappa Premium (1 month) - 10000$",
    "Custom Rank (1 month) - 10000$",
    "Custom Channel (1 month) - 10000$"
)


def eco_load_points():
    if os.path.exists(settings.ECO_POINTS_FILE):
        with open(settings.ECO_POINTS_FILE, "r") as f:
            return json.load(f)
    return {}


def save_eco_points(eco_points):
    with open(settings.ECO_POINTS_FILE, "w") as f:
        json.dump(eco_points, f, indent=4)


class ShopView(discord.ui.View):
    def __init__(self, user_points: int, user_id: int):
        super().__init__(timeout=120)  # 2 minutes timeout
        self.user_points = user_points
        self.user_id = user_id
        self.select_menu = None

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        # When the timeout triggers, we need to edit the original message to disable the buttons
        if hasattr(self, 'message'):
            await self.message.edit(view=self)

    @discord.ui.button(label="Buy", style=discord.ButtonStyle.green)
    async def buy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn't your shop session.", ephemeral=True)
            return

        self.clear_items()  # Remove the Buy button after clicking

        # Create select menu from options
        select = discord.ui.Select(
            placeholder="Choose an item...",
            options=[
                discord.SelectOption(label=option.split(" - ")[0], description=option)
                for option in options_to_buy
            ]
        )

        async def select_callback(interaction_select: discord.Interaction):
            selected_label = interaction_select.data["values"][0]
            selected_option = next(o for o in options_to_buy if selected_label in o)

            *_, price_str = selected_option.split(" - ")
            price = int(price_str.replace("$", ""))

            log_channel = interaction_select.client.get_channel(1396024376775802921)

            if self.user_points >= price:
                self.user_points -= price
                eco_points = eco_load_points()
                eco_points[str(self.user_id)] = self.user_points
                save_eco_points(eco_points)
                await log_channel.send(
                    f"✅ Accepted Payment — User: <@{self.user_id}> bought **{selected_label}** for {price}$")
                await interaction_select.response.send_message(f"You bought **{selected_label}** for {price}$ ✅",
                                                               ephemeral=True)
            else:
                await log_channel.send(
                    f"❌ Payment Denied — User: <@{self.user_id}> tried to buy **{selected_label}** but had only {self.user_points}$")
                await interaction_select.response.send_message(
                    f"You don't have enough money to buy **{selected_label}** ❌", ephemeral=True)

            # Disable further interaction
            for child in self.children:
                child.disabled = True
            await self.message.edit(view=self)

        select.callback = select_callback
        self.add_item(select)
        await interaction.response.edit_message(view=self)


@commands.hybrid_command(
    brief=f"{settings.PREFIX}shop - zakupy za dolary",
)
async def shop(ctx: commands.Context, is_private: bool = True) -> None:
    if not isinstance(is_private, bool):
        await ctx.send("Wariant `is_private` przyjmuje tylko wartości True lub False.", ephemeral=True)
        return

    eco_points = eco_load_points()
    user_points = eco_points.get(str(ctx.author.id), 0)

    description = ""
    for option in options_to_buy:
        description += f"{option}\n"

    shop_embed = discord.Embed(title="$ Sklep $", color=discord.Color.blue())
    shop_embed.description = description
    shop_embed.set_footer(text="You have {}$".format(user_points))

    view = ShopView(user_points, ctx.author.id)
    view.message = await ctx.send(embed=shop_embed, view=view, ephemeral=is_private)


async def setup(bot: commands.Bot):
    bot.add_command(shop)
