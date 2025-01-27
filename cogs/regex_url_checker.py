import discord
from discord.ext import commands
import re


class RegexUrlChecker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.bot.user:
            return

        if message.guild.id == 1056134342826528808 and isinstance(message.author, discord.Member):
            discord_admin_role_id = 1300612523179118683
            if not any(role.id == discord_admin_role_id for role in message.author.roles):
                # print("Użytkownik nie jest w administracji")
                url_pattern = r"https?://"
                url_regex = re.search(url_pattern, message.content)

                if url_regex:
                    # print("Wysłano link")
                    acceptable_pattern = (r"https?://(www\.)?"
                                          r"(youtube\.com|instagram\.com|facebook\.com|tiktok\.com|[a-z]*\.?discordapp\.(net|com)|tenor\.com)")
                    acceptable_regex = re.search(acceptable_pattern, message.content)

                    if not acceptable_regex:
                        url_logs_channel = self.bot.get_channel(1332562572129472564)
                        # print("Nieakceptowalny link, należy sprawdzić")
                        await url_logs_channel.send(f"<@&{discord_admin_role_id}>\n"
                                                    f"Na kanale {message.channel.name} {message.author.mention} ({message.author.name}) wysłał nietypowy dla mnie link:\n\n"
                                                    f"{message.content[:1800]}")
                        bannable_pattern = r"https?://(www\.)?discord\.(gg|com)/\w+"
                        bannable_regex = re.search(bannable_pattern, message.content)

                        if bannable_regex and "ssejEDNpJ7" not in message.content and "grappa-destiny" not in message.content and "9VDNv2jAcH" not in message.content:
                            # print("Użytkownik został automatycznie zbanowany")
                            await url_logs_channel.send(
                                f"**Zbanowałem** {message.author.mention} **({message.author.name}) za wysłanie linku z zaproszeniem na inny discord:**\n\n"
                                f"{message.content[:1800]}\n\n"
                                f"Jeśli powyżej faktycznie znajduje się link z zaproszeniem na innego discorda to nie jest wymagana żadna dodatkowa akcja administracji!")
                            await message.author.ban(reason="[AutoBan]: Wysłano link na innego Discorda",
                                                     delete_message_days=7)
                            await message.delete()


async def setup(bot):
    await bot.add_cog(RegexUrlChecker(bot))
