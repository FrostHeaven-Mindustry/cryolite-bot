from disnake.ext import commands
from asyncio import sleep
from datetime import datetime
from database import create_user

from config import greeting_channel


import disnake


class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.c = 0

    @commands.Cog.listener()
    async def on_member_join(self, member: disnake.Member):
        if await create_user(member.id):  # Приветствуем только пользователей, зашедших впервые
            emb = disnake.Embed(title='Добро пожаловать!', description=f'{member.name}, рады видеть вас на сервере!')
            emb.set_footer(text=f'Теперь нас {member.guild.member_count}')
            await self.bot.get_channel(greeting_channel).send(embed=emb)

    @commands.Cog.listener()
    async def on_ready(self):
        await sleep(2)  # Необходимо, чтобы информация успевала подгружаться
        for guild in self.bot.guilds:
            for user in guild.members:
                await create_user(user.id)
        print('ready')

    @commands.Cog.listener()
    async def on_slash_command_error(self, inter: disnake.Interaction, error):
        if isinstance(error, commands.CommandOnCooldown):
            await inter.response.send_message(f'Попробуйте снова через {round(error.retry_after, 2)} сек.')
        else:
            await inter.response.send_message('При выполнении команды произошла ошибка. Вы можете написать разработчику'
                                              ' (<@817312010000924732>), при этом желательно указать время и'
                                              ' обстоятельства, при которых произошла ошибка (название команды и '
                                              'использованные аргументы)', ephemeral=True)
            print(error)
            with open('logs.txt', 'a', encoding='utf-8') as f:
                f.write(f'\n{str(datetime.now())}\n{str(error)}\n{str(inter.data)}\n')


def setup(bot):
    bot.add_cog(Events(bot))
