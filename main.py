from disnake.ext import commands
from config import keys
from os import listdir

import disnake

bot = commands.Bot(
    intents=disnake.Intents.all(),
    test_guilds=[1265638410685780019]
)

for name in listdir('cogs'):
    if name.endswith('.py'):
        bot.load_extension(f'cogs.{name[:-3]}')

bot.run(keys["bot_token"])
