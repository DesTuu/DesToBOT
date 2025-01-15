from discord.ext import commands
import requests
import settings
import discord
import json


@commands.hybrid_command(
    brief=f"{settings.PREFIX}drink nazwa drinka - jeśli jest spacja to zostawić - opis nazwa drinka"
)
async def drink(ctx: commands.Context, drink_name) -> None:
    ing = []
    api_url = 'https://api.api-ninjas.com/v1/cocktail?name={}'.format(drink_name)
    response = requests.get(api_url, headers={'X-Api-Key': 'VVSwNaegofgRjxxwrVUgUQ==xz7IaJNkEh6SJFuy'})
    data = response.json()
    if data:
        for cocktail in data:
            ingredients = cocktail.get('ingredients')
            instructions = cocktail.get('instructions')
            names = cocktail.get('name')
            for ingredient in ingredients:
                ing.append(ingredient)
        ing = ",\n".join(ing)
        await ctx.send(
            f"Nazwa Drinku: {names.title()} \n\nWszystkie Składniki: \n{ing} \n\nInstrukcja: {instructions} \n\nJednostki: \n1 oz (fluid ounce) = 30ml, \n1 pinch = 0.3ml, \n1 tablespoon = 14,7 ml, \n1 teaspoon = 4,9ml, \n1 ds (dash) = 0.6 ml")
    else:
        await ctx.send(f"No data found for the cocktail: {drink_name}")


async def setup(bot: commands.Bot):
    bot.add_command(drink)
