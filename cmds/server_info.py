import discord
from discord.ext import commands
import settings


@commands.hybrid_command(
    brief=f"{settings.PREFIX}serverinfo - informacje dotyczące serwera",
)
async def server_info(ctx: commands.Context, is_private: bool = True) -> None:
    server_name = ctx.guild.name
    server_created_at = ctx.guild.created_at
    server_owner = ctx.guild.owner.mention
    server_member_count = ctx.guild.member_count

    ctx_author_joined_at = ctx.author.joined_at
    ctx_author_created_at = ctx.author.created_at
    ctx_author_mention = ctx.author.mention

    joined_at_formatted = ctx_author_joined_at.strftime('%Y-%m-%d %H:%M:%S')
    created_at_formatted = ctx_author_created_at.strftime('%Y-%m-%d %H:%M:%S')
    server_created_at_formatted = server_created_at.strftime('%Y-%m-%d %H:%M:%S')

    string_to_send = (f"{ctx_author_mention}: "
                      f"\n- jest z Nami na serwerze od {joined_at_formatted}"
                      f"\n- posiada konto na Discordzie od {created_at_formatted}"
                      f"\n"
                      f"{server_name}: "
                      f"\n- został stworzony {server_created_at_formatted} przez {server_owner}"
                      f"\n- ilość użytkowników wynosi {server_member_count}")

    await ctx.send(string_to_send, ephemeral=is_private)

async def setup(bot: commands.Bot):
    bot.add_command(server_info)
