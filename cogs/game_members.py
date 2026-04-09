import discord
from discord.ext import commands


class GameMembers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.text_master_role_id = 1310041042728517662
        self.text_diamond_role_id = 1310038363805319238
        self.text_gold_role_id = 1306920660680970250

        self.minecraft_role_id = 1261630440394068050
        self.warframe_role_id = 1261630668501422151
        self.pokemon_role_id = 1483865843157700778

        self.minecraft_channel_id = 1491759322353504286
        self.warframe_channel_id = 1491605334144454676
        self.pokemon_channel_id = 1491605428205912189

        self.minecraft_message_id = 1491759353869635825
        self.warframe_message_id = 1491759613840855101
        self.pokemon_message_id = 1491759162718421144

    def mention_user(self, id: int) -> str:
        return f"<@!{id}>"

    def get_users_with_roles(self, guild: discord.Guild, game_role_id: int):
        game_role = guild.get_role(game_role_id)
        if game_role is None:
            return []
        return [member.id for member in game_role.members]

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member) -> None:
        if before.roles == after.roles:
            return

        users_with_gold_role = self.get_users_with_roles(after.guild, self.text_gold_role_id)
        users_with_diamond_role = self.get_users_with_roles(after.guild, self.text_diamond_role_id)
        users_with_master_role = self.get_users_with_roles(after.guild, self.text_master_role_id)

        active_users = users_with_gold_role + users_with_diamond_role + users_with_master_role

        after_role_ids = [role.id for role in after.roles]

        if self.minecraft_role_id in after_role_ids:
            minecraft_string_to_send = "# Najaktywniejsi - Minecraft\n"
            minecraft_channel = after.guild.get_channel(self.minecraft_channel_id)
            if not minecraft_channel:
                return

            try:
                minecraft_message = await minecraft_channel.fetch_message(self.minecraft_message_id)
            except discord.NotFound:
                print(f"❌ Nie znaleziono wiadomości o tym ID")
                return
            except discord.Forbidden:
                print("❌ Brak uprawnień do edycji wiadomości!")
                return
            except discord.HTTPException:
                print("❌ Błąd pobierania wiadomości!")
                return

            users_with_minecraft_role = self.get_users_with_roles(after.guild, self.minecraft_role_id)
            common = list(set(users_with_minecraft_role) & set(active_users))

            if common:
                for user in common:
                    minecraft_string_to_send += f"- {self.mention_user(user)}\n"
            else:
                minecraft_string_to_send += "- <brak>\n"

            await minecraft_message.edit(content=minecraft_string_to_send[:2000])

        if self.warframe_role_id in after_role_ids:
            warframe_string_to_send = "# Najaktywniejsi - Warframe\n"
            warframe_channel = after.guild.get_channel(self.warframe_channel_id)
            if not warframe_channel:
                return

            try:
                warframe_message = await warframe_channel.fetch_message(self.warframe_message_id)
            except discord.NotFound:
                print(f"❌ Nie znaleziono wiadomości o tym ID")
                return
            except discord.Forbidden:
                print("❌ Brak uprawnień do edycji wiadomości!")
                return
            except discord.HTTPException:
                print("❌ Błąd pobierania wiadomości!")
                return

            users_with_warframe_role = self.get_users_with_roles(after.guild, self.warframe_role_id)
            common = list(set(users_with_warframe_role) & set(active_users))

            if common:
                for user in common:
                    warframe_string_to_send += f"- {self.mention_user(user)}\n"
            else:
                warframe_string_to_send += "- <brak>\n"

            await warframe_message.edit(content=warframe_string_to_send[:2000])

        if self.pokemon_role_id in after_role_ids:
            pokemon_string_to_send = "# Najaktywniejsi - Pokemon\n"
            pokemon_channel = after.guild.get_channel(self.pokemon_channel_id)
            if not pokemon_channel:
                return

            try:
                pokemon_message = await pokemon_channel.fetch_message(self.pokemon_message_id)
            except discord.NotFound:
                print(f"❌ Nie znaleziono wiadomości o tym ID")
                return
            except discord.Forbidden:
                print("❌ Brak uprawnień do edycji wiadomości!")
                return
            except discord.HTTPException:
                print("❌ Błąd pobierania wiadomości!")
                return

            users_with_pokemon_role = self.get_users_with_roles(after.guild, self.pokemon_role_id)
            common = list(set(users_with_pokemon_role) & set(active_users))

            if common:
                for user in common:
                    pokemon_string_to_send += f"- {self.mention_user(user)}\n"
            else:
                pokemon_string_to_send += "- <brak>\n"

            await pokemon_message.edit(content=pokemon_string_to_send[:2000])


async def setup(bot):
    await bot.add_cog(GameMembers(bot))
