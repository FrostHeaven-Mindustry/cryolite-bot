from disnake.ext import commands
import database as db

import disnake


class Clans(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command()
    async def clans(self, inter):
        emb = disnake.Embed(title='Все кланы')
        for i in await db.get_all_clans():
            emb.add_field(name=f'[{i.prefix}]{i.title}',
                          value=f'Глава клана: <@{i.owner}>\nУчастников: {await i.members_count()}', inline=False)
        await inter.response.send_message(embed=emb)

    @commands.slash_command()
    async def create_clan(self, inter: disnake.ApplicationCommandInteraction, title, prefix, slogan,
                          emblem_url: str = 'https://avatars.mds.yandex.net/'
                                            'i?id=1b8d32839ef85bb972d76605ba2608eb49466647-9065817-images-thumbs&n=13'):
        if await db.in_clan(inter.author.id):
            await inter.response.send_message('Вы уже состоите в клане')
        elif len(prefix) != 3:
            await inter.response.send_message('Длина префикса - 3 символа')
        else:
            await db.create_clan(title=title, emblem_url=emblem_url, slogan=slogan, owner=inter.author.id,
                                 prefix=prefix)
            await inter.response.send_message(f'Вы успешно создали клан {title}!')

    @commands.slash_command()
    async def clan_info(self, inter: disnake.ApplicationCommandInteraction, clan_title=None):
        if clan_title is not None:
            if not await db.is_clan_exist(clan_title):
                clan_title = None

        if clan_title is None:
            if await db.in_clan(inter.author.id):
                user = await db.get_user(inter.author.id)
                clan = await db.get_clan_by_id(user.clan_id)
                clan_title = clan.title
            else:
                emb = disnake.Embed(title='Нет клана', description='На данный момент вы не состоите в клане.')
                await inter.response.send_message(embed=emb)
                return

        clan = await db.get_clan_by_title(clan_title)

        owner = clan.owner
        clan_members = [f'<@{i.user_id}>' for i in await clan.members() if i.user_id != owner]

        emb = disnake.Embed(title=f'[{clan.prefix}]{clan_title}')
        emb.add_field('Девиз:', clan.slogan, inline=False)
        emb.add_field('Глава клана:', f'<@{owner}>', inline=False)
        emb.add_field('Участники:', '\n'.join(clan_members), inline=False)
        emb.set_image(clan.emblem_url)
        await inter.response.send_message(embed=emb)

    @commands.slash_command()
    async def join_clan(self, inter: disnake.ApplicationCommandInteraction, clan_title):
        if await db.in_clan(inter.author.id):
            embed_title, desc = 'Невозможно присоединиться', 'Вы уже состоите в клане'
        elif not await db.is_clan_exist(clan_title):
            embed_title, desc = 'Невозможно присоединиться', 'Клана с таким названием не существует'
        else:
            await db.join_clan(inter.author.id, clan_title)
            embed_title, desc = 'Успешно', f'Вы присоединились к клану {clan_title}'
        await inter.response.send_message(embed=disnake.Embed(title=embed_title, description=desc))


def setup(bot):
    bot.add_cog(Clans(bot))
