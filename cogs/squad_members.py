import discord
from discord.ext import commands


class SquadMembers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = 1497525213531738112

        self.voice_message_id = 1497529627835629618
        self.text_message_id = 1497529663428235376

        self.voice_master_role_id = 1408897749654442004
        self.voice_diamond_role_id = 1315707236776935474

        self.text_master_role_id = 1310041042728517662
        self.text_diamond_role_id = 1310038363805319238

        self.mention_voice_master_role = "<@&1408897749654442004>"
        self.mention_voice_diamond_role = "<@&1315707236776935474>"

        self.mention_text_master_role = "<@&1310041042728517662>"
        self.mention_text_diamond_role = "<@&1310038363805319238>"

    def mention_user(self, id: int) -> str:
        return f"<@!{id}>"

    def get_users_with_role(self, guild: discord.Guild, role_id: int):
        role = guild.get_role(role_id)
        if role is None:
            return []
        return [member.id for member in role.members]

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member) -> None:
        if not after.guild:
            return

        if after.guild.id != 1056134342826528808:
            return

        if before.roles == after.roles:
            return

        target_roles = [self.voice_master_role_id, self.voice_diamond_role_id, self.text_master_role_id, self.text_diamond_role_id]

        after_role_ids = [role.id for role in after.roles]

        if not any(role_id in after_role_ids for role_id in target_roles):
            return

        voice_string_to_send = "# Najaktywniejsi - Kanały Głosowe\n"
        text_string_to_send = "# Najaktywniejsi - Kanały Tekstowe\n"


        channel = after.guild.get_channel(self.channel_id)
        if not channel:
            return

        try:
            voice_message = await channel.fetch_message(self.voice_message_id)
            text_message = await channel.fetch_message(self.text_message_id)
        except discord.NotFound:
            print(f"❌ Nie znaleziono wiadomości o ID {self.voice_message_id} lub {self.text_message_id}")
            return
        except discord.Forbidden:
            print("❌ Brak uprawnień do edycji wiadomości!")
            return
        except discord.HTTPException:
            print("❌ Błąd pobierania wiadomości!")
            return

        users_with_voice_master_role = self.get_users_with_role(after.guild, self.voice_master_role_id)
        users_with_voice_diamond_role = self.get_users_with_role(after.guild, self.voice_diamond_role_id)

        users_with_text_master_role = self.get_users_with_role(after.guild, self.text_master_role_id)
        users_with_text_diamond_role = self.get_users_with_role(after.guild, self.text_diamond_role_id)

        voice_string_to_send += f"## {self.mention_voice_master_role}\n"
        if users_with_voice_master_role:
            for user in users_with_voice_master_role:
                if self.mention_user(user) not in voice_string_to_send:
                    voice_string_to_send += f"- {self.mention_user(user)}\n"
        else:
            voice_string_to_send += "- <brak>\n"

        voice_string_to_send += f"## {self.mention_voice_diamond_role}\n"
        if users_with_voice_diamond_role:
            for user in users_with_voice_diamond_role:
                if self.mention_user(user) not in voice_string_to_send:
                    voice_string_to_send += f"- {self.mention_user(user)}\n"
        else:
            voice_string_to_send += "- <brak>\n"



        voice_string_to_send = voice_string_to_send[:2000]
        await voice_message.edit(content=voice_string_to_send)

        # -----

        text_string_to_send += f"## {self.mention_text_master_role}\n"
        if users_with_text_master_role:
            for user in users_with_text_master_role:
                if self.mention_user(user) not in text_string_to_send:
                    text_string_to_send += f"- {self.mention_user(user)}\n"
        else:
            text_string_to_send += "- <brak>\n"

        text_string_to_send += f"## {self.mention_text_diamond_role}\n"
        if users_with_text_diamond_role:
            for user in users_with_text_diamond_role:
                if self.mention_user(user) not in text_string_to_send:
                    text_string_to_send += f"- {self.mention_user(user)}\n"
        else:
            text_string_to_send += "- <brak>\n"



        text_string_to_send = text_string_to_send[:2000]
        await text_message.edit(content=text_string_to_send)


async def setup(bot):
    await bot.add_cog(SquadMembers(bot))
