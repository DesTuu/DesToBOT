from discord.ext import commands
import settings
import asyncio
import discord


@commands.hybrid_command(
    brief=f"{settings.PREFIX}unban_all reason - unbans all users whose ban reason contains given text [DesTu only]"
)
async def unban_all(ctx: commands.Context, banned_reason: str) -> None:
    await ctx.defer(ephemeral=True)

    if ctx.author.id != 354712325053218819:  # Only you can run this
        await ctx.send("Przykro mi, nie masz uprawnień, żeby użyć tej komendy!", ephemeral=True)
        return

    guild = ctx.bot.get_guild(1056134342826528808)
    if guild is None:
        await ctx.send("Nie znaleziono serwera o podanym ID.", ephemeral=True)
        return

    unbanned_count = 0
    async for ban_entry in guild.bans():
        user = ban_entry.user
        reason = ban_entry.reason or ""

        if banned_reason.lower() in reason.lower():
            try:
                await guild.unban(user, reason=f"Mass unban by {ctx.author}")
                unbanned_count += 1

                # Try to send DM to the unbanned user
                try:
                    await user.send(
                        f"Zostałeś odbanowany na serwerze **{guild.name}**.\n"
                        f"https://discord.gg/9VDNv2jAcH\n"
                        f"*Odbanowany przez: {ctx.author}*"
                    )
                except Exception:
                    pass

                await asyncio.sleep(3)

            except discord.NotFound:
                # User is not actually banned anymore
                print(f"User {user} is not banned anymore, skipping...")
                continue
            except Exception as e:
                print(f"Unexpected error while unbanning {user} ({user.id}): {e}")

    await ctx.send(f"Odbanowano {unbanned_count} użytkowników.", ephemeral=True)


async def setup(bot: commands.Bot):
    bot.add_command(unban_all)
