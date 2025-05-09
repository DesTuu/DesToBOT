import discord
from discord.ext import commands


class SquadMembers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = 1269975070625763378
        self.message_id = 1347834429472505856
        self.legends_id = 1351135683846344726
        self.bestie_id = 1310041042728517662
        self.homie_id = 1310038363805319238
        # self.buddy_id = 1306920660680970250

        self.mention_legends = "<@&1351135683846344726>"
        self.mention_bestie = "<@&1310041042728517662>"
        self.mention_homie = "<@&1310038363805319238>"
        # self.mention_buddy = "<@&1306920660680970250>"
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

        target_roles = [self.bestie_id, self.homie_id] #self.buddy_id
        after_role_ids = [role.id for role in after.roles]

        if not any(role_id in after_role_ids for role_id in target_roles):
            return

        string_to_send = "# Skład Ekipy\n"

        channel = after.guild.get_channel(self.channel_id)
        if not channel:
            return

        try:
            message = await channel.fetch_message(self.message_id)  # Pobranie wiadomości
        except discord.NotFound:
            print(f"❌ Nie znaleziono wiadomości o ID {self.message_id}")
            return
        except discord.Forbidden:
            print("❌ Brak uprawnień do edycji wiadomości!")
            return
        except discord.HTTPException:
            print("❌ Błąd pobierania wiadomości!")
            return

        legends = self.get_users_with_role(after.guild, self.legends_id)
        besties = self.get_users_with_role(after.guild, self.bestie_id)
        homies = self.get_users_with_role(after.guild, self.homie_id)
        # buddies = self.get_users_with_role(after.guild, self.buddy_id)

        string_to_send += f"## {self.mention_legends}\n"
        if legends:
            for legend in legends:
                string_to_send += f"- {self.mention_user(legend)}\n"
        else:
            string_to_send += "- <brak>\n"

        string_to_send += f"## {self.mention_bestie}\n"
        if besties:
            for bestie in besties:
                string_to_send += f"- {self.mention_user(bestie)}\n"
        else:
            string_to_send += "- <brak>\n"

        string_to_send += f"## {self.mention_homie}\n"
        if homies:
            for homie in homies:
                string_to_send += f"- {self.mention_user(homie)}\n"
        else:
            string_to_send += "- <brak>\n"

        # string_to_send += f"## {self.mention_buddy}\n"
        # if buddies:
        #     for buddy in buddies:
        #         string_to_send += f"- {self.mention_user(buddy)}\n"
        # else:
        #     string_to_send += "- <brak>\n"

        string_to_send = string_to_send[:2000]
        await message.edit(content=string_to_send)

async def setup(bot):
    await bot.add_cog(SquadMembers(bot))
