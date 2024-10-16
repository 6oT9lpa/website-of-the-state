import disnake, json, redis, asyncio, traceback
from disnake.ext import commands
from disnake import ButtonStyle
from datetime import datetime
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

    async def send_dm_invite(self, discord_id, password, static, organ):
        try:
            print(f"Попытка отправить сообщение пользователю с ID: {discord_id}")
            user = await self.fetch_user(discord_id)

            embed = disnake.Embed(
                title=f"Вы были приняты во фракцию **{organ}**",
                description=(
                    f"Ваш логин от аккаунта: **{static}**\n"
                    f"Ваш пароль от аккаунта: **{password}**\n\n"
                    "Вам нужно сменить пароль на свой, чтобы повысить безопасность вашего аккаунта."
                ),
                color=disnake.Color.green()
            )
            embed.set_footer(text="Если вы считаете, что это ошибочное сообщение, свяжитесь с 6ot9lpa")

            button = Button(
                label="Сменить пароль",
                url="http://26.184.54.209:8000/auth",
                style=ButtonStyle.link
            )

            view = View()
            view.add_item(button)

            await user.send(embed=embed, view=view)
            print(f"Сообщение отправлено пользователю {discord_id}")
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {discord_id}: {e}")
            traceback.print_exc()
    
    async def send_dm_resolution(self, uid, nickname, static, discrodid):
        channel_id = 1286759030257221714
        try:
            channel = self.get_channel(channel_id)
            if not channel:
                print(f"Канал с ID {channel_id} не найден")
                return

            embed = disnake.Embed(
                title=f"Пришло новое постановление от **{nickname} {static}** ||<@{discrodid}>||",
                description=(
                    f"Требуется модерация постановления!\n"
                    f"Чтобы начать модерацию нажмите на кнопку ниже\n\n"
                ),
                color=disnake.Color.blue()
            )
            embed.set_footer(text="Если вы считаете, что это ошибочное сообщение, свяжитесь с 6ot9lpa")

            button = Button(
                label="Модерация",
                url=f"http://26.184.54.209:8000/resolution?uid={uid}",
                style=ButtonStyle.green
            )
            view = View()
            view.add_item(button)
            message = await channel.send(embed=embed, view=view)
            self.message_id = message.id
            print(f"Сообщение отправлено в канал {channel_id}")
            
        except Exception as e:
            print(f"Не удалось отправить сообщение в канал {channel_id}: {e}")
            traceback.print_exc()

    async def send_dm_dismissal(self, discord_id, static, organ):
        try:
            print(f"Попытка отправить сообщение пользователю с ID: {discord_id}")
            user = await self.fetch_user(discord_id)

            embed = disnake.Embed(
                title=f"Вы были уволены из фракции **{organ}**",
                description=(
                    f"Ваш логин от аккаунта: **{static}**\n\n"
                    "Ваш аккаунт был заморожен, так как вы больше не находитесь в данной фракции."
                ),
                color=disnake.Color.red()
            )
            embed.set_footer(text="Если вы считаете, что это ошибочное сообщение, свяжитесь с 6ot9lpa")

            await user.send(embed=embed)
            print(f"Сообщение об увольнении отправлено пользователю {discord_id}")
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {discord_id}: {e}")
            traceback.print_exc()

    async def handle_action(self, action, static_to, discord_id_from, discord_id_to, curr_rank, prev_rank, channel_id, nikname_from, nikname_to, reason):
        channel = self.get_channel(channel_id)
        if action == "Invite":
            embed = disnake.Embed(
                title="Кадровый аудит • Принятие",
                color=disnake.Color.green()
            )
             
            embed.add_field(name="Принял", value=f"<@{discord_id_from}> | {nikname_from}", inline=True)
            embed.add_field(name="Принят", value=f"<@{discord_id_to}> | {nikname_to}", inline=True)

            embed.add_field(name="Номер паспорта", value=static_to, inline=False)
            embed.add_field(name="Действие", value='Принятие во фракцию', inline=False)
            embed.add_field(name="Причина", value=reason, inline=False)
            embed.add_field(name="Ранг", value=f"Предыдущий **{prev_rank}** | Текущий  **{curr_rank}**", inline=True)
            
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            embed.set_footer(text=f"Дата: {current_datetime}")
            await channel.send(embed=embed)
 
        elif action == "Dismissal":
            embed = disnake.Embed(
                title="Кадровый аудит • Увольнение",
                color=disnake.Color.red()
            )
             
            embed.add_field(name="Уволил", value=f"<@{discord_id_from}> | {nikname_from}", inline=True)
            embed.add_field(name="Уволен", value=f"<@{discord_id_to}> | {nikname_to}", inline=True)

            embed.add_field(name="Номер паспорта", value=static_to, inline=False)
            embed.add_field(name="Действие", value='Увольнение из фракцию', inline=False)
            embed.add_field(name="Причина", value=reason, inline=False)
            
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            embed.set_footer(text=f"Дата: {current_datetime}")
            await channel.send(embed=embed)

        elif action == "Raising":
            embed = disnake.Embed(
                title="Кадровый аудит • Повышение",
                color=disnake.Color.yellow()
            )
             
            embed.add_field(name="Повысил", value=f"<@{discord_id_from}> | {nikname_from}", inline=True)
            embed.add_field(name="Повышен", value=f"<@{discord_id_to}> | {nikname_to}", inline=True)

            embed.add_field(name="Номер паспорта", value=static_to, inline=False)
            embed.add_field(name="Действие", value='Повышение в должности', inline=False)
            embed.add_field(name="Причина", value=reason, inline=False)
            embed.add_field(name="Ранг", value=f"Предыдущий **{prev_rank}** | Текущий  **{curr_rank}**", inline=True)
            
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            embed.set_footer(text=f"Дата: {current_datetime}")
            await channel.send(embed=embed)
            
        elif action == "Demotion":
            embed = disnake.Embed(
                title="Кадровый аудит • Понижение",
                color=disnake.Color.yellow()
            )
             
            embed.add_field(name="Понизил", value=f"<@{discord_id_from}> | {nikname_from}", inline=True)
            embed.add_field(name="Понижен", value=f"<@{discord_id_to}> | {nikname_to}", inline=True)

            embed.add_field(name="Номер паспорта ", value=static_to, inline=False)
            embed.add_field(name="Действи", value='Понижение в должности', inline=False)
            embed.add_field(name="Ранг", value=f"Предыдущий **{prev_rank}** | Текущий  **{curr_rank}**", inline=True)
            embed.add_field(name="Причина", value=reason, inline=False)
            
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            embed.set_footer(text=f"Дата: {current_datetime}")
            await channel.send(embed=embed)

bot = MyBot(command_prefix=config['prefix'], intents=intents)

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

async def process_new_resolution_message():
    pubsub = redis_client.pubsub()
    pubsub.subscribe('new_resolution')

    while True:
        message = pubsub.get_message()
        if message and message['type'] == 'message':
            try:
                print(f"Получено сообщение: {message['data']}")
                data = json.loads(message['data'])
                uid = data['uid']
                nickname = data['nickname']
                static = data['static']
                discrodid = data['discrodid']
                
                await bot.send_dm_resolution(uid, nickname, static, discrodid)
            except Exception as e:
                print(f"Ошибка обработки сообщения: {e}")
                traceback.print_exc()
        await asyncio.sleep(1)

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


@bot.event
async def on_ready():
    print(f"Бот {bot.user} готов к работе!")
    bot.loop.create_task(process_invite_messages())
    bot.loop.create_task(process_dismissal_messages())
    bot.loop.create_task(process_ka_messages())
    bot.loop.create_task(process_new_resolution_message())

def run_bot():
    bot.run(config['token'])
