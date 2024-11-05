import disnake, json
from disnake.ext import commands
import sys

with open('./python/config.json', 'r') as f:
    config = json.load(f)
    
def setup_cogs(bot):
     for extension in disnake.utils.search_directory("python/cogs"):
        try:
            bot.load_extension(extension)
        except Exception as error:
            print(f'Failed to load extension {error}', file=sys.stderr)

bot = commands.Bot(command_prefix=config['prefix'], intents=disnake.Intents.all())

@bot.event
async def on_ready():
    print(f"Бот {bot.user} готов к работе!")
    

def run_bot():
    setup_cogs(bot)
    bot.run(config['token'])
