import disnake, json, redis, asyncio, traceback
from disnake.ext import commands
from disnake import ButtonStyle
from disnake.ui import View, Button

class SendDmMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = 1323283005086760991
        
    async def send_dm_resolution(self, uid, nickname, static, discordid):
        try:
            # Подготавливаем данные сообщения
            self.message_data = {
                "channel_id": self.channel_id,
                "button_label": "Модерация",
                "uid": uid,
                "button_url": None,
                "message_id": None,
                "is_active": False  
            }

            # Пытаемся получить канал
            channel = await self.get_channel_with_retry(self.channel_id)
            if not channel:
                print(f"Канал с ID {self.channel_id} не найден после нескольких попыток")
                return

            # Создаем сообщение с встраиванием
            embed = disnake.Embed(
                title=f"Пришло новое постановление от прокурора `{nickname} #{static}` ||<@{discordid}>||",
                description=(
                    "Требуется модерация постановления!\n"
                    "Чтобы начать модерацию, нажмите на кнопку ниже\n\n"
                ),
                color=disnake.Color.blue()
            )
            embed.set_footer(text="Если вы считаете, что это ошибочное сообщение, свяжитесь с 6ot9lpa")

            # Отправляем сообщение в канал
            message = await channel.send(embed=embed)

            # Обновляем message_id в данных и сохраняем их
            self.message_data["message_id"] = str(message.id)
            self.messages[self.message_data["message_id"]] = self.message_data
            self.save_message_data()

            # Создаем View и обновляем сообщение с кнопкой
            view = self.create_moderation_view(self.message_data["message_id"])
            await message.edit(view=view)
            await self.update_message_view(self.message_data["message_id"])

            print(f"Сообщение отправлено в канал {self.channel_id} с ID {message.id}")

        except Exception as e:
            print(f"Ошибка при отправке сообщения в канал {self.channel_id}: {e}")


    async def send_dm_invite(self, discord_id, password, static, organ):
        try:
            print(f"Попытка отправить сообщение пользователю с ID: {discord_id}")
            user = await self.bot.fetch_user(discord_id)

            embed = disnake.Embed(
                title=f"Вы были приняты во фракцию **{organ}**",
                description=(
                    f"Ваш логин (static) от аккаунта: ```{static}```\n"
                    f"Ваш пароль от аккаунта: ```{password}```\n\n"
                    "Вам нужно сменить пароль на свой, чтобы повысить безопасность вашего аккаунта."
                ),
                color=disnake.Color.green()
            )
            embed.set_footer(text="Если вы считаете, что это ошибочное сообщение, свяжитесь с 6ot9lpa")

            button1 = Button(
                label="Сменить пароль",
                url="http://217.114.0.37:8000/auth?next=http://217.114.0.37:8000/change_password",
                style=ButtonStyle.link
            )
            button2 = Button(
                label="Перейти на сайт",
                url="http://217.114.0.37:8000/",
                style=ButtonStyle.link
            )

            view = View()
            view.add_item(button1)
            view.add_item(button2)

            await user.send(embed=embed, view=view)
            print(f"Сообщение отправлено пользователю {discord_id}")
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {discord_id}: {e}")
            traceback.print_exc()
            
    async def send_dm_dismissal(self, discord_id, static, organ):
        try:
            print(f"Попытка отправить сообщение пользователю с ID: {discord_id}")
            user = await self.bot.fetch_user(discord_id)

            embed = disnake.Embed(
                title=f"Вы были уволены из фракции **{organ}**",
                description=(
                    f"Ваш логин от аккаунта: ```{static}```\n\n"
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
            
    async def send_dm_message_resolution(self, discord_to, discord_from, moderation, reason, uid):
        if moderation:
            try:
                print(f"Попытка отправить сообщение пользователю с ID: {discord_to}")
                user = await self.bot.fetch_user(discord_to)

                embed = disnake.Embed(
                    title="Вам было одобренно постановление!",
                    description=(
                        f"<@{discord_from}> одобрил ваше постановление \n"
                        f"и оно было направленно в официальную пуликацию\n\n"
                        "его можно увидеть во вкладке /doc или по кнопке ниже"
                    ),
                    color=disnake.Color.green()
                )
                embed.set_footer(text="Если вы считаете, что это ошибочное сообщение, свяжитесь с 6ot9lpa")
                
                button = Button(
                    label="Осмотреть постановление",
                    url=f"http://217.114.0.37:8000/resolution?uid={ uid }",
                    style=ButtonStyle.link
                )

                view = View()
                view.add_item(button)

                await user.send(embed=embed, view=view)
                print(f"Сообщение об увольнении отправлено пользователю {discord_to}")
            except Exception as e:
                print(f"Не удалось отправить сообщение пользователю {discord_to}: {e}")
                traceback.print_exc()
                
        else:
            try:
                print(f"Попытка отправить сообщение пользователю с ID: {discord_to}")
                user = await self.bot.fetch_user(discord_to)

                embed = disnake.Embed(
                    title="Вам было отклоненно постановление!",
                    description=(
                        f"<@{discord_from}> отклонил ваше постановление \n"
                        f"с причинной {reason}\n\n"
                        "вы его можете исправить нажав на кнопку, ниже"
                    ),
                    color=disnake.Color.red()
                )
                embed.set_footer(text="Если вы считаете, что это ошибочное сообщение, свяжитесь с 6ot9lpa")
                
                button = Button(
                    label="Исправить постановление",
                    url=f"http://217.114.0.37:8000/auth?next=http://217.114.0.37:8000/edit_doc?uid={uid}",
                    style=ButtonStyle.link
                )

                view = View()
                view.add_item(button)

                await user.send(embed=embed, view=view)
                print(f"Сообщение об увольнении отправлено пользователю {discord_to}")
            except Exception as e:
                print(f"Не удалось отправить сообщение пользователю {discord_to}: {e}")
                traceback.print_exc()   
    async def send_dm_changepass(self, discord_id, code):
        try:
            print(f"Попытка отправить сообщение пользователю с ID: {discord_id}")
            user = await self.bot.fetch_user(discord_id)

            embed = disnake.Embed(
                title=f"Попытка смены пароля!",
                description=(
                    f"Ваш код для смены пароля: **{code}**\n"
                    "Не передавайте этот код!"
                ),
                color=disnake.Color.green()
            )
            embed.set_footer(text="Если вы считаете, что это ошибочное сообщение, свяжитесь с Arnetik")

            view = View()

            await user.send(embed=embed, view=view)
            print(f"Сообщение отправлено пользователю {discord_id}")
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {discord_id}: {e}")
            traceback.print_exc()

    async def send_notifdm(self, text, discord_id, url):
        try:
            print(f"Попытка отправить сообщение пользователю с ID: {discord_id}")
            user = await self.bot.fetch_user(discord_id)

            embed = disnake.Embed(
                title=f"Внимание!",
                description=(
                    text
                ),
                color=disnake.Color.orange()
            )
            embed.set_footer(text="Если вы считаете, что это ошибочное сообщение, свяжитесь с Arnetik")
            if url:
                button = Button(
                        label="Подробнее",
                        url=url,
                        style=ButtonStyle.link
                    )

            view = View()
            if url:
                view.add_item(button)

            await user.send(embed=embed, view=view)
            print(f"Сообщение отправлено пользователю {discord_id}")
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {discord_id}: {e}")
            traceback.print_exc()

    async def send_log(self, header, text):
        try:
            channel = self.bot.get_channel(1323976134307876864)
            embed = disnake.Embed(
                title=header,
                description=(
                    text
                ),
                color=disnake.Color.red()
            )
            embed.set_footer(text="Если вы считаете, что это ошибочное сообщение, свяжитесь с Arnetik")

            view = View()

            await channel.send(embed=embed, view=view)
        except Exception as e:
            print(f"Не удалось отправить сообщение лога: {e}")
            traceback.print_exc()       


redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
async def process_new_resolution_message(dm_message):
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
                discordid = data['discordid']
                
                await dm_message.send_dm_resolution(uid, nickname, static, discordid)
            except Exception as e:
                print(f"Ошибка обработки сообщения: {e}")
                traceback.print_exc()
        await asyncio.sleep(1)

async def process_invite_messages(dm_message):
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
                await dm_message.send_dm_invite(discord_id, password, static, organ)
            except Exception as e:
                print(f"Ошибка обработки сообщения: {e}")
                traceback.print_exc()
        await asyncio.sleep(1)

async def process_dismissal_messages(dm_message):
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
                await dm_message.send_dm_dismissal(discord_id, static, organ)
            except Exception as e:
                print(f"Ошибка обработки сообщения: {e}")
                traceback.print_exc()
        await asyncio.sleep(1)

async def process_invite_changepass(dm_message):
    pubsub = redis_client.pubsub()
    pubsub.subscribe('changepass_channel')

    while True:
        message = pubsub.get_message()
        if message and message['type'] == 'message':
            try:
                data = json.loads(message['data'])
                discord_id = data['discord_id']
                code = data['code']
                await dm_message.send_dm_changepass(discord_id, code)
            except Exception as e:
                print(f"Ошибка обработки сообщения: {e}")
                traceback.print_exc()
        await asyncio.sleep(1)

async def process_notifdm(dm_message):
    pubsub = redis_client.pubsub()
    pubsub.subscribe('notificationdm_channel')

    while True:
        message = pubsub.get_message()
        if message and message['type'] == 'message':
            try:
                data = json.loads(message['data'])
                discord_id = data['discord_id']
                text = data['text']
                url = data['url']
                await dm_message.send_notifdm(text, discord_id, url)
            except Exception as e:
                print(f"Ошибка обработки сообщения: {e}")
                traceback.print_exc()
        await asyncio.sleep(1)
        
async def process_information_resolution_message(dm_message):
    pubsub = redis_client.pubsub()
    pubsub.subscribe('information_resolution')
    
    while True:
        message = pubsub.get_message()
        if message and message['type'] == 'message':
            try:
                print(f"Получено сообщение: {message['data']}")
                data = json.loads(message['data'])
                
                moderation = data['moderation']
                discord_to = data['discord_to']
                discord_from = data['discord_from']
                uid = data['uid']
                reason = data['reason']
                
                await dm_message.send_dm_message_resolution(discord_to, discord_from, moderation, reason, uid)
                
            except Exception as e:
                print(f"Ошибка обработки сообщения: {e}")
                traceback.print_exc()
        await asyncio.sleep(1)

async def process_log_messages(dm_message):
    pubsub = redis_client.pubsub()
    pubsub.subscribe('log_dump')

    while True:
        message = pubsub.get_message()
        if message and message['type'] == 'message':
            try:
                print(f"Получено сообщение: {message['data']}")
                data = json.loads(message['data'])
                header = data['header']
                text = data['text']
                
                await dm_message.send_log(header, text,)
            except Exception as e:
                print(f"Ошибка обработки сообщения: {e}")
                traceback.print_exc()
        await asyncio.sleep(1)    

async def process_get_dsname(bot):
    pubsub = redis_client.pubsub()
    pubsub.subscribe('get_dsname')

    while True:
        message = pubsub.get_message()
        if message and message['type'] == 'message':
            try:
                print(f"Получено сообщение: {message['data']}")
                data = json.loads(message['data'])
                discordid = data['discordid']

                for attempt in range(3):
                    try:
                        user = await bot.fetch_user(discordid)
                        if user:
                            redis_client.set(f'dsname_response_{discordid}', user.name)
                            print(f"Успешно обработан пользователь {discordid} на попытке {attempt + 1}")
                            break
                    except Exception as e:
                        print(f"Попытка {attempt + 1}: Ошибка при получении пользователя с ID {discordid}: {e}")

                    if attempt < 2: 
                        await asyncio.sleep(0.3)
                else:
                    print(f"Не удалось получить пользователя с ID {discordid} после 3 попыток")

            except Exception as e:
                print(f"Ошибка обработки сообщения: {e}")
                traceback.print_exc()

        await asyncio.sleep(1)

def setup(bot):
    dm_message = SendDmMessage(bot)
    bot.loop.create_task(process_invite_messages(dm_message))
    bot.loop.create_task(process_dismissal_messages(dm_message))
    bot.loop.create_task(process_new_resolution_message(dm_message))
    bot.loop.create_task(process_information_resolution_message(dm_message))
    bot.loop.create_task(process_invite_changepass(dm_message))
    bot.loop.create_task(process_notifdm(dm_message))
    bot.loop.create_task(process_log_messages(dm_message))
    bot.loop.create_task(process_get_dsname(bot))
    bot.add_cog(SendDmMessage(bot))
