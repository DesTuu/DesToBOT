from discord.ext import commands
import discord
import settings


@commands.hybrid_command(
    brief=f"{settings.PREFIX}ban_check ID - sprawdzasz info o banie użytkownika",
)
async def ban_check(ctx: commands.Context, user_id: str) -> None:
    try:
        user = await ctx.bot.fetch_user(int(user_id))
    except ValueError:
        await ctx.send("❌ Invalid user ID format.")
        return
    except discord.NotFound:
        await ctx.send("❌ User not found.")
        return

    try:
        ban_entry = await ctx.guild.fetch_ban(user)
        reason = ban_entry.reason or "No reason provided."
        await ctx.send(f"✅ User **{user}** is **banned**.\nReason: `{reason}`")
    except discord.NotFound:
        await ctx.send(f"ℹ️ User **{user}** is **not banned** on this server.")
    except discord.Forbidden:
        await ctx.send("❌ I don’t have permission to view bans.")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}")


async def setup(bot: commands.Bot):
    bot.add_command(ban_check)
