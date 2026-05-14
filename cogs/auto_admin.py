import discord
from discord.ext import commands

# === ROLE IDS ===
HEADADMIN_ROLE_ID = 0
VICEADMIN_ROLE_ID = 0
MODERATOR_ROLE_ID = 0
HELPER_ROLE_ID = 0

ADMIN_ROLE_ID = 0
SENIOR_ROLE_ID = 0
MID_ROLE_ID = 0
JUNIOR_ROLE_ID = 0
INTERN_ROLE_ID = 0

# === CONFIG ===
CHANNEL_ID = 0
MESSAGE_ID = 0
LOG_CHANNEL_ID = 0


class AdminList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_rank(self, member: discord.Member):
        if discord.utils.get(member.roles, id=SENIOR_ROLE_ID):
            return "senior"
        if discord.utils.get(member.roles, id=MID_ROLE_ID):
            return "mid"
        if discord.utils.get(member.roles, id=JUNIOR_ROLE_ID):
            return "junior"
        if discord.utils.get(member.roles, id=INTERN_ROLE_ID):
            return "intern"
        return "intern"

    def format_member(self, member: discord.Member):
        return f"{self.get_rank(member)} <@{member.id}>"

    def get_sections(self, guild):
        sections = {
            "headadmin": [],
            "viceadmin": [],
            "moderator": [],
            "helper": []
        }

        for m in guild.members:
            role_ids = [r.id for r in m.roles]

            if HEADADMIN_ROLE_ID in role_ids:
                sections["headadmin"].append(m)
            elif VICEADMIN_ROLE_ID in role_ids:
                sections["viceadmin"].append(m)
            elif MODERATOR_ROLE_ID in role_ids:
                sections["moderator"].append(m)
            elif HELPER_ROLE_ID in role_ids:
                sections["helper"].append(m)

        return sections

    def sort_members(self, members):
        order = {"senior": 0, "mid": 1, "junior": 2, "intern": 3}
        return sorted(members, key=lambda m: order[self.get_rank(m)])

    def build_section(self, role_id, members):
        if not members:
            return ""

        text = f"# <@&{role_id}>\n"

        for m in self.sort_members(members):
            text += f"## - {self.format_member(m)}\n"

        return text

    async def send_log(self, guild, description):
        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if not log_channel:
            return

        embed = discord.Embed(
            title="📋 Aktualizacja administracji",
            description=description,
            color=discord.Color.blue()
        )
        embed.timestamp = discord.utils.utcnow()

        await log_channel.send(embed=embed)

    async def update_list(self, guild, reason="Automatyczna aktualizacja"):
        channel = guild.get_channel(CHANNEL_ID)
        if not channel:
            return

        sections = self.get_sections(guild)

        content = "# Skład Administracji\n"
        content += self.build_section(HEADADMIN_ROLE_ID, sections["headadmin"])
        content += self.build_section(VICEADMIN_ROLE_ID, sections["viceadmin"])
        content += self.build_section(MODERATOR_ROLE_ID, sections["moderator"])
        content += self.build_section(HELPER_ROLE_ID, sections["helper"])

        content = content[:2000]

        msg = await channel.fetch_message(MESSAGE_ID)
        await msg.edit(content=content)

        # ✅ LOG
        await self.send_log(guild, f"Lista administracji została zaktualizowana.\nPowód: **{reason}**")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        before_roles = set(r.id for r in before.roles)
        after_roles = set(r.id for r in after.roles)

        watched_roles = {
            HEADADMIN_ROLE_ID,
            VICEADMIN_ROLE_ID,
            MODERATOR_ROLE_ID,
            HELPER_ROLE_ID,
            ADMIN_ROLE_ID,
            SENIOR_ROLE_ID,
            MID_ROLE_ID,
            JUNIOR_ROLE_ID,
            INTERN_ROLE_ID
        }

        if before_roles != after_roles:
            changed = before_roles ^ after_roles

            if watched_roles.intersection(changed):
                await self.update_list(
                    after.guild,
                    reason=f"Zmiana ról u <@{after.id}>"
                )


async def setup(bot):
    await bot.add_cog(AdminList(bot))