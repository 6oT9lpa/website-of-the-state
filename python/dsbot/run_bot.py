import disnake
from disnake.ext import commands, tasks
import os
import sys
import json
import asyncio
from datetime import datetime, timedelta
import redis

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from __init__ import Users, app, db  # Импорт модели Users из Flask-приложения
from main import password

with open('./python/dsbot/config.json', 'r') as f:
    config = json.load(f)

intents = disnake.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.last_checked_id = 0
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)  # Инициализация Redis
        self.check_updates.start()  # Запуск задачи при инициализации

    async def send_dm(self, discord_id, message):
        try:
            user = await self.fetch_user(discord_id)
            await user.send(message)
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {discord_id}: {e}")

    @tasks.loop(seconds=1)
    async def check_updates(self):
        if self.is_closed():
            return

        # Получаем пользователей с action == Invite, используя кеш
        users_to_send = self.get_users_from_cache()

        # Отправляем сообщения асинхронно
        await asyncio.gather(*[self.send_message(user) for user in users_to_send])

        # Обновляем кеш после отправки сообщений
        self.update_cache(users_to_send)

    async def send_message(self, user):
        time_delta = datetime.now() - user.timespan
        if time_delta < timedelta(minutes=1):
            try:
                await self.send_dm(user.discordid, f'Ваш пароль: {password}')
                print(f"Сообщение отправлено пользователю {user.discordid}")
            except Exception as e:
                print(f"Ошибка при отправке сообщения пользователю {user.discordid}: {e}")
        else:
            print(f"Слишком рано отправлять сообщение пользователю {user.discordid}.")

    def get_users_from_cache(self):
        users_to_send = []
        for user_id in self.redis_client.smembers("users_to_send"):
            # Получение данных пользователя из базы данных Flask
            with app.app_context():
                user = db.session.query(Users).filter_by(discordid=user_id).first()
            if user:
                users_to_send.append(user)
        return users_to_send

    def update_cache(self, users):
        for user in users:
            self.redis_client.sadd("users_to_send", user.discordid)

    @check_updates.before_loop
    async def before_check_updates(self):
        await self.wait_until_ready() 

bot = MyBot(command_prefix=config['prefix'], intents=intents)

@bot.event
async def on_ready():
    print(f"Бот {bot.user} готов к работе!")
    for command in bot.commands:
        print(f"Зарегистрированная команда: {command.name}")

def run_bot():
    bot.run(config['token'])
