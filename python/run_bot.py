import disnake, json, redis, asyncio, traceback
from disnake.ext import commands, tasks
from disnake import ButtonStyle
from datetime import datetime
from disnake.ui import View, Button
import os, time

with open('./python/config.json', 'r') as f:
    config = json.load(f)

intents = disnake.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
        
        self.data_file_path = os.path.join(os.getcwd(), "message_data.json")
        self.messages = {}
        self.channel_id = 1286759030257221714
        self.message_data = {}
        
    def save_message_data(self):
        """Сохраняет данные всех сообщений в JSON."""
        data = {
            "messages": self.messages
        }
        try:
            with open(self.data_file_path, "w") as json_file:
                json.dump(data, json_file, indent=4)
            print(f"Данные сообщений сохранены в {self.data_file_path}")
        except Exception as e:
            print(f"Ошибка при сохранении данных в JSON: {e}")

    def load_message_data(self):
        """Загружает данные сообщений из JSON при перезагрузке бота."""
        try:
            if os.path.exists(self.data_file_path):
                with open(self.data_file_path, "r") as json_file:
                    data = json.load(json_file)
                    self.messages = data.get("messages", {})
                    
                    if not self.messages:
                        print("Нет сохраненных сообщений в JSON или данные не загружены корректно.")
                    else:
                        print("Данные успешно загружены из message_data.json")
            else:
                print("Файл message_data.json не найден.")
        except json.JSONDecodeError:
            print("Ошибка при чтении JSON файла. Убедитесь, что файл имеет правильный формат.")
        except Exception as e:
            print(f"Произошла ошибка при загрузке данных из JSON: {e}")

    def create_moderation_view(self, message_id):
        """Создает View с кнопкой модерации для конкретного сообщения."""
        view = disnake.ui.View(timeout=None)

        message_data = self.messages.get(message_id)
        if not message_data:
            print(f"Данные для message_id {message_id} отсутствуют в messages.")
            return view  # Возвращаем пустой View, если данные не найдены

        button_label = message_data.get("button_label", "Модерация")
        custom_id = f"moderation_{message_id}"

        button = disnake.ui.Button(
            label=button_label,
            style=disnake.ButtonStyle.green,
            custom_id=custom_id
        )

        async def button_callback(interaction):
            print(f"Кнопка нажата для message_id: {message_id}")

            # Проверка данных сообщения
            self.message_data = self.messages.get(message_id)
            if not self.message_data:
                await interaction.response.send_message("Данные сообщения недоступны.", ephemeral=True)
                print(f"Нет данных для message_id: {message_id}")
                return

            uid = self.message_data.get("uid", "")
            if not uid:
                await interaction.response.send_message("UID не установлен, невозможно создать ссылку.", ephemeral=True)
                print(f"UID не установлен для message_id: {message_id}")
                return

            # Если права есть, обновляем URL, помечаем кнопку как активную и сохраняем данные
            self.messages[message_id]["button_url"] = f"http://26.184.54.209:8000/resolution?uid={uid}"
            self.messages[message_id]["is_active"] = True
            self.save_message_data()

            await interaction.response.send_message(
                f"Вы начали модерацию постановления [перейти к модерации]({self.messages[message_id]['button_url']})",
                ephemeral=True
            )    
            # Проверка прав
            permission_none = await process_permission_messages()
            if permission_none:
                try:
                    # Отправляем сообщение об ошибке в личные сообщения пользователю
                    await interaction.user.send("У вас нет прав на модерацию постановлений.")
                    print(f"Пользователь {interaction.user.id} не имеет прав на модерацию. Сообщение отправлено в ЛС.")
                except disnake.Forbidden:
                    # Если не удалось отправить в ЛС, отправляем ответ прямо в чат
                    if not interaction.response.is_done():
                        await interaction.response.send_message(
                            "У вас нет прав на модерацию постановлений, и я не смог отправить вам сообщение в личные сообщения.",
                            ephemeral=True
                        )
                    print(f"Не удалось отправить сообщение в ЛС пользователю {interaction.user.id}. Сообщение отправлено в чат.")
                
                # Обновляем статус кнопки и сохраняем изменения
                self.messages[message_id]["is_active"] = False
                self.save_message_data()
                await self.update_message_view(message_id)
                return

            # Обновляем embed, чтобы показать, что пользователь выполняет модерацию
            embed = interaction.message.embeds[0]
            embed.add_field(name="Модерируется", value=f"<@{interaction.user.id}>", inline=False)
            view.clear_items()  # Удаляем кнопку
            await interaction.message.edit(embed=embed, view=view)

        button.callback = button_callback
        view.add_item(button)
        return view


    async def get_channel_with_retry(self, channel_id):
        """Пытается получить канал с указанным ID несколько раз с задержкой."""
        if not channel_id:
            print("Ошибка: channel_id отсутствует или равен None.")
            return None

        for attempt in range(3):
            try:
                channel = await self.fetch_channel(channel_id)
                if channel:
                    print(f"Канал с ID {channel_id} успешно найден на попытке {attempt + 1}")
                    return channel
            except Exception as e:
                print(f"Попытка {attempt + 1}: Ошибка при получении канала с ID {channel_id}: {e}")

            print(f"Канал с ID {channel_id} не найден, попытка {attempt + 1}/3")
            await asyncio.sleep(5)
        
        print(f"Канал с ID {channel_id} не найден после 3 попыток")
        return None
    
    async def update_message_view(self, message_id):
        """Обновляет View для конкретного сообщения, если оно не активно."""
        message_data = self.messages.get(message_id)
        if not message_data:
            print(f"Данные для сообщения {message_id} не найдены")
            return

        # Проверка, активна ли кнопка
        if message_data.get("is_active", False):
            print(f"Кнопка для сообщения {message_id} уже активирована, обновление пропущено.")
            return

        channel = await self.get_channel_with_retry(message_data["channel_id"])
        if not channel:
            print(f"Канал с ID {message_data['channel_id']} не найден")
            return

        try:
            message = await channel.fetch_message(int(message_id))
            if not message:
                print(f"Сообщение с ID {message_id} не найдено")
                return

            # Восстанавливаем кнопку в View
            view = self.create_moderation_view(message_id)
            await message.edit(view=view)
            print(f"View обновлен для сообщения {message_id}")

        except Exception as e:
            print(f"Ошибка при обновлении View для сообщения {message_id}: {e}")
            traceback.print_exc()


    @tasks.loop(minutes=10)
    async def update_buttons(self):
        """Обновляет кнопки каждые 10 минут."""
        for message_id, message_data in self.messages.items():
            await self.update_message_view(message_id)
            
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
                title=f"Пришло новое постановление от **{nickname} {static}** ||<@{discordid}>||",
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
            
    async def send_dm_message_resolution(self, discord_to, discord_from, moderation, reason, uid):
        if moderation:
            try:
                print(f"Попытка отправить сообщение пользователю с ID: {discord_to}")
                user = await self.fetch_user(discord_to)

                embed = disnake.Embed(
                    title="Вам было одобренно постановление!",
                    description=(
                        f"<@{discord_from}> одобрил ваше постановление \n"
                        f"и оно было направленно в официальную пуликацию\n\n"
                        "его можно увидеть во вкладке /doc"
                    ),
                    color=disnake.Color.green()
                )
                embed.set_footer(text="Если вы считаете, что это ошибочное сообщение, свяжитесь с 6ot9lpa")
                
                button = Button(
                    label="Осмотреть постановление",
                    url="http://26.184.54.209:8000/auth",
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
                user = await self.fetch_user(discord_to)

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
                    url="http://26.184.54.209:8000/edit_doc?uid=01860222690775097111881819",
                    style=ButtonStyle.link
                )

                view = View()
                view.add_item(button)

                await user.send(embed=embed, view=view)
                print(f"Сообщение об увольнении отправлено пользователю {discord_to}")
            except Exception as e:
                print(f"Не удалось отправить сообщение пользователю {discord_to}: {e}")
                traceback.print_exc()

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

async def process_permission_messages():
    pubsub = redis_client.pubsub()
    pubsub.subscribe('user_permission')
    
    while True:
        message = pubsub.get_message()
        if message and message['type'] == 'message':
            try:
                print(f"Получено сообщение: {message['data']}")
                data = json.loads(message['data'])
                
                permission_none = data['permission_none']
                print(f"Значение none_permission обновлено: {permission_none}")
                
                return permission_none
                
            except Exception as e:
                print(f"Ошибка обработки сообщения: {e}")
                traceback.print_exc()
        await asyncio.sleep(1)
        
async def process_information_resolution_message():
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
                
                await bot.send_dm_message_resolution(discord_to, discord_from, moderation, reason, uid)
                
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
    bot.loop.create_task(process_information_resolution_message())
    
    time.sleep(5)
    bot.load_message_data()
    bot.loop.create_task(bot.update_buttons())
    

def run_bot():
    bot.run(config['token'])
