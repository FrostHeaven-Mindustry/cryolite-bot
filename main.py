from disnake.ext import commands
from disnake.utils import search_directory
from config import TOKEN

import disnake

bot = commands.InteractionBot(
    intents=disnake.Intents.all(),
    test_guilds=[1265638410685780019]
)


@bot.slash_command()
@commands.is_owner()
async def load(inter: disnake.ApplicationCommandInteraction, extension: str):
    bot.load_extension(f"cogs.{extension}")
    await inter.response.send_message(f"Cog `{extension}` uploaded successfully.", ephemeral=True)


@bot.slash_command()
@commands.is_owner()
async def reload(inter: disnake.ApplicationCommandInteraction, extension: str):
    bot.unload_extension(f"cogs.{extension}")
    bot.load_extension(f"cogs.{extension}")
    await inter.response.send_message(f"Cog `{extension}` is successfully reloaded.", ephemeral=True)


@bot.slash_command()
@commands.is_owner()
async def unload(inter: disnake.ApplicationCommandInteraction, extension: str):
    bot.unload_extension(f"cogs.{extension}")
    await inter.response.send_message(f"Cog `{extension}` is successfully unloaded.", ephemeral=True)


for name in search_directory('cogs'):
    bot.load_extension(name)

bot.run(TOKEN)
