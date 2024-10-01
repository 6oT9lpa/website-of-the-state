import disnake
from disnake.ext import commands
import json
import time

with open('./python/config.json', 'r') as f:
    config = json.load(f)

intents = disnake.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)

    async def send_dm(self, discord_id, message):
        try:
            user = await self.fetch_user(discord_id)
            await user.send(message)
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {discord_id}: {e}")

    async def check_updates(self, pasw, disid):
        if self.is_closed():
            return

        try:
            await self.send_dm(disid, f"Ваш код: {pasw}")
        except Exception as e:
            print(f"Ошибка при отправкa сообщения пользователю {disid}: {e}")


bot = MyBot(command_prefix=config['prefix'], intents=intents)


@bot.event
async def on_ready():
    print(f"Бот {bot.user} готов к работе!")
    
    for command in bot.commands:
        print(f"Зарегистрированная команда: {command.name}")


    


def run_bot():
    bot.run(config['token'])
