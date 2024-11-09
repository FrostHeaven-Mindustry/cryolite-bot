from disnake.ext import commands
from disnake.utils import search_directory
from config import TOKEN

import disnake

bot = commands.InteractionBot(
    intents=disnake.Intents.all(),
    test_guilds=[1265638410685780019]
)

for name in search_directory('cogs'):
    bot.load_extension(name)

bot.run(TOKEN)
