import discord
from discord.ext import commands
from discord.ui import Button, View
from itertools import islice
import settings


class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        brief=f"{settings.PREFIX}help - wyświetla wszystkie komendy i ich opisy"
    )
    async def help(self, ctx: commands.Context) -> None:
        embed = discord.Embed(title="Available Commands (Dostępne Komendy)", color=discord.Color.blue())
        commands_sorted = sorted(self.bot.commands, key=lambda cmd: cmd.name)
        commands_chunks = list(self.chunks(commands_sorted, 15))
        view = HelpPaginationView(commands_chunks, ctx)
        message = await ctx.send(embed=self.generate_help_embed(commands_chunks[0], 1, len(commands_chunks)), view=view)
        view.message = message

    def chunks(self, iterable, size):
        it = iter(iterable)
        for first in it:
            yield [first] + list(islice(it, size - 1))

    def generate_help_embed(self, commands_list, current_page, total_pages):
        embed = discord.Embed(title="Available Commands (Dostępne Komendy)", color=discord.Color.blue())
        embed.set_footer(text=f"Page {current_page}/{total_pages}")
        for command in commands_list:
            if not command.hidden and command.name != 'help':
                embed.add_field(name=f"{settings.PREFIX}{command.name}", value=command.brief, inline=False)
        return embed


class HelpPaginationView(View):
    def __init__(self, commands_chunks, ctx):
        super().__init__(timeout=300)
        self.commands_chunks = commands_chunks
        self.ctx = ctx
        self.page = 0

        self.previous_button = Button(label="Previous", style=discord.ButtonStyle.secondary)
        self.next_button = Button(label="Next", style=discord.ButtonStyle.secondary)
        self.previous_button.callback = self.previous_page
        self.next_button.callback = self.next_page

        self.add_item(self.previous_button)
        self.add_item(self.next_button)

        self.update_buttons()

    async def update_embed(self):
        self.update_buttons()
        embed = self.generate_help_embed(self.commands_chunks[self.page], self.page + 1, len(self.commands_chunks))
        await self.message.edit(embed=embed, view=self)

    def update_buttons(self):
        self.previous_button.disabled = self.page == 0
        self.next_button.disabled = self.page == len(self.commands_chunks) - 1

    async def previous_page(self, interaction: discord.Interaction):
        if self.page > 0:
            self.page -= 1
        await self.update_embed()
        await interaction.response.defer()

    async def next_page(self, interaction: discord.Interaction):
        if self.page < len(self.commands_chunks) - 1:
            self.page += 1
        await self.update_embed()
        await interaction.response.defer()

    def generate_help_embed(self, commands_list, current_page, total_pages):
        embed = discord.Embed(title="Available Commands (Dostępne Komendy)", color=discord.Color.blue())
        embed.set_footer(text=f"Page {current_page}/{total_pages}")
        for command in commands_list:
            if not command.hidden and command.name != 'help':
                embed.add_field(name=f"{settings.PREFIX}{command.name}", value=command.brief, inline=False)
        return embed


async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
