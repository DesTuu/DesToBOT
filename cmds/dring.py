from discord.ext import commands
import requests
import settings


@commands.hybrid_command(
    brief=f"{settings.PREFIX}dring składnik1, składnik2, ... - przecinki pomiędzy - pokazuje jakie drinki można zrobić"
)
async def dring(ctx: commands.Context, ingredients_names) -> None:
    nm = []
    api_url = 'https://api.api-ninjas.com/v1/cocktail?ingredients={}'.format(ingredients_names)
    response = requests.get(api_url, headers={'X-Api-Key': 'VVSwNaegofgRjxxwrVUgUQ==xz7IaJNkEh6SJFuy'})
    data = response.json()
    if data:
        for cocktail in data:
            names = cocktail.get('name')
            nm.append(names.title())
        nm = ",\n".join(nm)
        await ctx.send(f"Nazwy drinków, które można wykonać z {ingredients_names} (max 10 drinków): \n{nm}")
    else:
        await ctx.send(f"No data found for the cocktail: {ingredients_names}")


async def setup(bot: commands.Bot):
    bot.add_command(dring)
