import disnake
from disnake.ext import commands
import json
import time
import redis
from disnake import ButtonStyle
from datetime import datetime
from disnake.ui import View, Button
import sys
#import os
import asyncio
#from sqlalchemy.orm import sessionmaker
#from sqlalchemy import create_engine

#engine = create_engine('mysql://root:arnetik1@localhost:3306/site')
#Session = sessionmaker(bind=engine)
#db_session = Session()

with open('./python/dsbot/config.json', 'r') as f:
    config = json.load(f)

intents = disnake.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True

def setup_cogs(bot):
     for extension in disnake.utils.search_directory("python/dsbot/cogs"):
        try:
            bot.load_extension(extension)
        except Exception as error:
            print(f'Failed to load extension {extension}', file=sys.stderr)
            #errors = traceback.format_exception(type(error), error, error.__traceback__)
            print({error})

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

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

async def process_invite_messages():
    pubsub = redis_client.pubsub()
    pubsub.subscribe('invite_channel')

    while True:
        message = pubsub.get_message()
        if message and message['type'] == 'message':
            try:
                print(f"Получено сообщение: {message['data']}")
                data = json.loads(message['data'])
                discord_id = data['discord_id']
                password = data['password']
                static = data['static']
                organ = data['organ']
                await bot.send_dm_invite(discord_id, password, static, organ)
            except Exception as e:
                print(f"Ошибка обработки сообщения: {e}")
                traceback.print_exc()
        await asyncio.sleep(1)

async def process_dismissal_messages():
    pubsub = redis_client.pubsub()
    pubsub.subscribe('dismissal_channel')

    while True:
        message = pubsub.get_message()
        if message and message['type'] == 'message':
            try:
                print(f"Получено сообщение: {message['data']}")
                data = json.loads(message['data'])
                discord_id = data['discord_id']
                static = data['static']
                organ = data['organ']
                await bot.send_dm_dismissal(discord_id, static, organ)
            except Exception as e:
                print(f"Ошибка обработки сообщения: {e}")
                traceback.print_exc()
        await asyncio.sleep(1)

async def process_ka_messages():
    pubsub = redis_client.pubsub()
    pubsub.subscribe('ka_channel')

    while True:
        message = pubsub.get_message()
        if message and message['type'] == 'message':
            try:
                print(f"Получено сообщение: {message['data']}")
                data = json.loads(message['data'])
                action = data['action']
                discord_id_from = data['discord_id_from']
                discord_id_to = data['discord_id_to']
                curr_rank = data['curr_rank']
                prev_rank = data['prev_rank']
                static_to = data['static_to']
                nikname_from = data['nikname_from']
                nikname_to = data['nikname_to']
                channel_id = 1286759030257221714
                reason = data['reason']
                
                await bot.handle_action(action, static_to, discord_id_from, discord_id_to, curr_rank, prev_rank, channel_id, nikname_from, nikname_to, reason)
            except Exception as e:
                print(f"Ошибка обработки сообщения: {e}")
                traceback.print_exc()
        await asyncio.sleep(1)

#


@bot.event
async def on_ready():
    print(f"Бот {bot.user} готов к работе!")
    
    for command in bot.commands:
        print(f"Зарегистрированная команда: {command.name}")


    


def run_bot():
    setup_cogs(bot)
    bot.run(config['token'])
