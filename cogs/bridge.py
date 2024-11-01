from disnake.ext import commands
from database import create_user, get_from_db

'''Важное замечание: при попытке запустить данный файл эта строка вернёт ошибку, поскольку файл находится на уровень
выше, и следует писать ..basefuncs. Однако при загрузке файла через disnake.Bot.load_extension он выполняется как часть
основного файла, соответственно, импорты выполняются относительно main.py'''

import disnake


class Bridge(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Bridge(bot))
