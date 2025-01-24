import discord
from discord.ext import commands, tasks
import settings
from db.my_token import DISCORD_TOKEN

if __name__ == "__main__":
    intents = discord.Intents().all()
    bot = commands.Bot(command_prefix=settings.PREFIX, intents=intents,
                       heartbeat_timeout=settings.HEARTBEAT_TIMEOUT)

    bot.remove_command('help')


    @commands.hybrid_command(
        brief=f"{settings.PREFIX}help - wyświetla wszystkie komendy i ich opisy"
    )
    async def help(ctx: commands.Context) -> None:
        embed = discord.Embed(title="Available Commands (Dostępne Komendy)", color=discord.Color.blue())
        commands_sorted = sorted(bot.commands, key=lambda cmd: cmd.name)
        for command in commands_sorted:
            if not command.hidden and command.name != 'help':
                embed.add_field(name=f"{settings.PREFIX}{command.name}", value=command.brief, inline=False)
        await ctx.send(embed=embed)


    @bot.event
    async def on_ready():
        for cmd_file in settings.CMD_DIR.glob('*.py'):
            if cmd_file.name != '__init__.py':
                await bot.load_extension(f"cmds.{cmd_file.name[:-3]}")

        bot.add_command(help)

        await bot.tree.sync()

        settings.on_ready_message(bot)


    bot.run(DISCORD_TOKEN)
