from discord.ext import commands
import settings


@commands.hybrid_command(
    brief=f"{settings.PREFIX}users - sprawdza ilość osób z daną rangą",
)
async def users(ctx: commands.Context, role_id: str = "1296535472796995624", is_private: bool = True) -> None:
    if ctx.author.id != 354712325053218819:
        is_private = True

    try:
        role_id = int(role_id)
    except ValueError:
        await ctx.send("Podane role_id musi być liczbą!", ephemeral=True)
        return

    role = ctx.guild.get_role(role_id)
    if role is None:
        await ctx.send("Nie znaleziono roli o podanym ID.", ephemeral=True)
        return

    members_with_role = [member for member in ctx.guild.members if role in member.roles]

    if not members_with_role:
        await ctx.send(f"Nikt nie ma roli: {role.name}", ephemeral=True)
        return

    users_list = ", ".join([f"{member.mention}" for member in members_with_role])
    await ctx.send(f"Lista użytkowników z rolą **{role.name}**:\n{users_list}", ephemeral=is_private)


async def setup(bot: commands.Bot):
    bot.add_command(users)
