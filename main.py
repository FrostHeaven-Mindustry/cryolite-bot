from disnake.ext import commands
from disnake.utils import search_directory
from config import TOKEN

import disnake

bot = commands.InteractionBot(
    intents=disnake.Intents.all(),
    test_guilds=[1265638410685780019]
)

@bot.command()
@commands.is_owner()
async def load(ctx, extension: str) -> None:
  bot.load_extension(f"cogs.{extension}")
  print(f"[Bot] Cog \"{extension}\" uploaded successfully.")
  await ctx.send(f"Cog `{extension}` uploaded successfully.")


@bot.command()
@commands.is_owner()
async def reload(ctx, extension: str) -> None:
  bot.unload_extension(f"cogs.{extension}")
  bot.load_extension(f"cogs.{extension}")
  print(f"[Bot] Cog \"{extension}\" successful reloaded.")
  await ctx.send(f"Cog `{extension}` is successfully reloaded.")


@bot.command()
@commands.is_owner()
async def unload(ctx, extension: str) -> None:
  bot.unload_extension(f"cogs.{extension}")
  print(f"[Bot] Cog \"{extension}\" is successfully unloaded.")
  await ctx.send(f"Cog `{extension}` is successfully unloaded.")


@bot.event
async def on_connect():
  print(f"[Bot] Connecting the bot \"{bot.user}\" to the discord...")

@bot.event
async def on_disconnect():
  print(
    f"[Bot] Bot \"{bot.user}\" disconnected or could not get to the discord.")

@bot.event
async def on_ready():
  print("The bot is ready to work.)
        
for name in search_directory('cogs'):
    bot.load_extension(name)

bot.run(TOKEN)
