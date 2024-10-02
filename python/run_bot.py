import disnake, json, redis, asyncio
from disnake.ext import commands
from disnake import ButtonStyle
from disnake.ui import View, Button

with open('./python/config.json', 'r') as f:
    config = json.load(f)

intents = disnake.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)

    async def send_dm(self, discord_id, password, static, organ):
        try:
            print(f"Попытка отправить сообщение пользователю с ID: {discord_id}")
            user = await self.fetch_user(discord_id)

            # Создаем embed сообщение
            embed = disnake.Embed(
                title=f"Вы были приняты во фракцию **{ organ }**",
                description=(
                    f"Ваш логин от аккаунта: **{static}**\n"
                    f"Ваш пароль от аккаунта: **{password}**\n\n"
                    "Вам нужно сменить пароль на свой, чтобы повысить безопасность вашего аккаунта."
                ),
                color=disnake.Color.green()  # Вы можете выбрать другой цвет
            )
            embed.set_footer(text="Пожалуйста, измените пароль как можно скорее.")

            # Создаем кнопку с перенаправлением на сайт
            button = Button(
                label="Сменить пароль",
                url="http://26.184.54.209:8000/auth",  # Укажите реальный URL
                style=ButtonStyle.link
            )

            # Создаем View, чтобы прикрепить кнопку к сообщению
            view = View()
            view.add_item(button)

            # Отправляем сообщение с embed и кнопкой
            await user.send(embed=embed, view=view)
            print(f"Сообщение отправлено пользователю {discord_id}")
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {discord_id}: {e}")

bot = MyBot(command_prefix=config['prefix'], intents=intents)

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

async def process_messages():
    pubsub = redis_client.pubsub()
    pubsub.subscribe('bot_channel')

    for message in pubsub.listen():
        if message['type'] == 'message':
            data = json.loads(message['data'])
            discord_id = data['discord_id']
            password = data['password']
            static = data['static']
            organ = data['organ']
            await bot.send_dm(discord_id, password, static, organ)

@bot.event
async def on_ready():
    print(f"Бот {bot.user} готов к работе!")
    bot.loop.create_task(process_messages())

def run_bot():
    bot.run(config['token'])
