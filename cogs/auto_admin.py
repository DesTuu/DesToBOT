import discord
from discord.ext import commands

# === ROLE IDS ===
CEO_ROLE_ID = 1169392520309002350
HEADADMIN_ROLE_ID = 1257981571579773012
VICEADMIN_ROLE_ID = 1279902404128669726
MODERATOR_ROLE_ID = 1279903108419289108
HELPER_ROLE_ID = 1356487064740302859

ADMIN_ROLE_ID = 1300612523179118683

SENIOR_ROLE_ID = 1503733299028164668
MID_ROLE_ID = 1503733358277034014
JUNIOR_ROLE_ID = 1503733406075326504
INTERN_ROLE_ID = 1503733459498303612

# === CONFIG ===
CHANNEL_ID = 1269975070625763378
MESSAGE_ID = 1504492501636219011
LOG_CHANNEL_ID = 1504493007343194223


class AdminList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_rank(self, member: discord.Member):
        if discord.utils.get(member.roles, id=SENIOR_ROLE_ID):
            return "Senior"

        if discord.utils.get(member.roles, id=MID_ROLE_ID):
            return "Mid"

        if discord.utils.get(member.roles, id=JUNIOR_ROLE_ID):
            return "Junior"

        if discord.utils.get(member.roles, id=INTERN_ROLE_ID):
            return "Intern"

        return "Intern"

    def format_member(self, member: discord.Member):
        return f"{self.get_rank(member)} <@{member.id}>"

    def get_sections(self, guild):
        sections = {
            "ceo": [],
            "headadmin": [],
            "viceadmin": [],
            "moderator": [],
            "helper": []
        }

        for m in guild.members:
            role_ids = [r.id for r in m.roles]

            if CEO_ROLE_ID in role_ids:
                sections["ceo"].append(m)

            elif HEADADMIN_ROLE_ID in role_ids:
                sections["headadmin"].append(m)

            elif VICEADMIN_ROLE_ID in role_ids:
                sections["viceadmin"].append(m)

            elif MODERATOR_ROLE_ID in role_ids:
                sections["moderator"].append(m)

            elif HELPER_ROLE_ID in role_ids:
                sections["helper"].append(m)

        return sections

    def sort_members(self, members):
        order = {
            "Senior": 0,
            "Mid": 1,
            "Junior": 2,
            "Intern": 3,
        }

        return sorted(members, key=lambda m: order[self.get_rank(m)])

    def build_section(self, role_id, members):
        if not members:
            return ""

        text = f"# <@&{role_id}>\n"

        for m in self.sort_members(members):
            text += f"## - {self.format_member(m)}\n"

        return text

    async def send_log(self, guild, user_id, role_id, action):
        log_channel = guild.get_channel(LOG_CHANNEL_ID)

        if not log_channel:
            return

        if action == "added":
            text = f"## ✅ <@!{user_id}> zyskał rolę <@&{role_id}>"

        else:
            text = f"## ❌ <@!{user_id}> stracił rolę <@&{role_id}>"

        await log_channel.send(text)

    async def update_list(self, guild):
        channel = guild.get_channel(CHANNEL_ID)

        if not channel:
            return

        sections = self.get_sections(guild)

        content = "# Skład Administracji\n"

        content += self.build_section(
            CEO_ROLE_ID,
            sections["ceo"]
        )

        content += self.build_section(
            HEADADMIN_ROLE_ID,
            sections["headadmin"]
        )

        content += self.build_section(
            VICEADMIN_ROLE_ID,
            sections["viceadmin"]
        )

        content += self.build_section(
            MODERATOR_ROLE_ID,
            sections["moderator"]
        )

        content += self.build_section(
            HELPER_ROLE_ID,
            sections["helper"]
        )

        content = content[:2000]

        msg = await channel.fetch_message(MESSAGE_ID)
        await msg.edit(content=content)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        before_roles = set(r.id for r in before.roles)
        after_roles = set(r.id for r in after.roles)

        watched_roles = {
            CEO_ROLE_ID,
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

                await self.update_list(after.guild)

                added_roles = after_roles - before_roles
                removed_roles = before_roles - after_roles

                for role_id in added_roles:
                    if role_id in watched_roles:
                        await self.send_log(
                            after.guild,
                            after.id,
                            role_id,
                            "added"
                        )

                for role_id in removed_roles:
                    if role_id in watched_roles:
                        await self.send_log(
                            after.guild,
                            after.id,
                            role_id,
                            "removed"
                        )


async def setup(bot):
    await bot.add_cog(AdminList(bot))