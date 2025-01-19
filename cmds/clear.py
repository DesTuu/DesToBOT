from discord.ext import commands
import settings
import discord


@commands.hybrid_command(
    brief=f"{settings.PREFIX}clear liczba - usuwa wszystkie wiadomości od podanej wiadomości (id) [DesTu only]"
)
async def cls(ctx: commands.Context, message_id: str) -> None:
    await ctx.defer()

    if ctx.author.id != 354712325053218819:
        await ctx.send("Przykro mi, nie masz uprawnień, żeby użyć tej komendy!", ephemeral=True)
        return

    try:
        message_id = int(message_id)

        msg = await ctx.channel.fetch_message(message_id)
    except ValueError:
        await ctx.send("Nieprawidłowy format ID wiadomości.", ephemeral=True)
        return
    except discord.NotFound:
        await ctx.send("Nie znaleziono wiadomości o podanym ID.", ephemeral=True)
        return
    except discord.Forbidden:
        await ctx.send("Brak uprawnień do usunięcia wiadomości.", ephemeral=True)
        return
    except discord.HTTPException:
        await ctx.send("Wystąpił błąd podczas pobierania wiadomości.", ephemeral=True)
        return

    def check(message):
        return message.id >= message_id

    try:
        deleted = await ctx.channel.purge(check=check)
    except discord.errors.HTTPException as e:
        if isinstance(e, discord.errors.NotFound):
            print(f"Message not found: {e}")
        else:
            print(f"HTTP Exception: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


async def setup(bot: commands.Bot):
    bot.add_command(cls)
