from disnake.ext import commands
from basefuncs import add_to_db, get_from_db, update_db, in_clan

import disnake


class Clans(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command()
    async def create_clan(self, inter: disnake.ApplicationCommandInteraction, name, prefix,
                          emblem_url: str = 'https://avatars.mds.yandex.net/'
                                            'i?id=1b8d32839ef85bb972d76605ba2608eb49466647-9065817-images-thumbs&n=13'):
        if in_clan(inter.author.id):
            await inter.response.send_message('Вы уже состоите в клане')
            return
        if len(prefix) > 3:
            await inter.response.send_message('Длина префикса не должна превышать 3 символа')
            return
        add_to_db('clans', name=name, emblem_url=emblem_url, owner=inter.author.id, prefix=prefix)
        update_db('users', "id", inter.author.id, clan=get_from_db("clans", "owner", inter.author.id, 'id')[0])
        await inter.response.send_message(f'Вы успешно создали клан {name}!')


def setup(bot):
    bot.add_cog(Clans(bot))
