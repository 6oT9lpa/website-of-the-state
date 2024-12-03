import disnake, json, redis, asyncio, traceback
from disnake.ext import commands, tasks
from disnake import ButtonStyle, Intents
from datetime import datetime
from disnake.ui import View, Button
import os, time, sys

class ModerationDoc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot     
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
            self.messages[message_id]["button_url"] = f"http://26.120.213.68:8000/resolution?uid={uid}/moderation"
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
                    await interaction.user.send("У вас нет прав на модерацию постановлений.")
                    print(f"Пользователь {interaction.user.id} не имеет прав на модерацию. Сообщение отправлено в ЛС.")
                except disnake.Forbidden:
                    if not interaction.response.is_done():
                        await interaction.response.send_message(
                            "У вас нет прав на модерацию постановлений, и я не смог отправить вам сообщение в личные сообщения.",
                            ephemeral=True
                        )
                    print(f"Не удалось отправить сообщение в ЛС пользователю {interaction.user.id}. Сообщение отправлено в чат.")
                ""
                self.messages[message_id]["is_active"] = False
                self.save_message_data()
                await self.update_message_view(message_id)
                return

            embed = interaction.message.embeds[0]
            embed.add_field(name="Модерируется", value=f"<@{interaction.user.id}>", inline=False)
            view.clear_items()
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
                channel = await self.bot.fetch_channel(channel_id)
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
    
    async def send_dm_resolution(self, uid, nickname, static, discordid, status, number_resolution):
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
            
            if status == 'moder':
                global embed
                # Создаем сообщение с встраиванием
                embed = disnake.Embed(
                    title=f"Пришло новое постановление **{number_resolution}** от прокурора `{nickname} #{static}`",
                    description=(
                        "Требуется модерация постановления!\n"
                        "Чтобы начать модерацию, нажмите на кнопку ниже\n\n"
                    ),
                    color=disnake.Color.blue()
                )
                embed.set_footer(text="Если вы считаете, что это ошибочное сообщение, свяжитесь с 6ot9lpa")
            
            elif status == 'edit':
                embed = disnake.Embed(
                    title=f"Пришло измененное постановление **{number_resolution}** от прокурора `{nickname} #{static}`",
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
        

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
async def process_new_resolution_message(moderation_doc):
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
                status = data['status']
                number_resolution = data['number_resolution']
                
                await moderation_doc.send_dm_resolution(uid, nickname, static, discordid, status, number_resolution)
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


def setup(bot):
    moderation_doc = ModerationDoc(bot)
    bot.loop.create_task(process_new_resolution_message(moderation_doc))
    bot.add_cog(ModerationDoc(bot))
    
     
    time.sleep(5)
    moderation_doc.load_message_data()
    bot.loop.create_task(moderation_doc.update_buttons())