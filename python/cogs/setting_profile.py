import disnake, json, redis, asyncio, traceback
from disnake.ext import commands, tasks
from disnake import ButtonStyle
import os, time
import __init__

class SettingProfile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot     
        self.data_file_path = os.path.join(os.getcwd(), "btn-data-change.json")
        self.messages = {}
        self.channel_id = 1324476770644135996
        self.message_data = {}
        self.allowed_role_ids = [1285215465853026471, 1323246976719912980]
        
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

    async def create_moderation_view(self, message_id):
        """Создает или восстанавливает View с кнопками для конкретного сообщения."""
        view = disnake.ui.View(timeout=None)

        message_data = self.messages.get(message_id)
        if not message_data:
            print(f"Данные для message_id {message_id} отсутствуют в messages.")
            return view  # возвращаем пустой view, если данных нет

        print(f"Восстановление View для message_id {message_id}")
        
        def remove_message(message_id):
            """Удаляет сообщение из self.messages и сохраняет изменения в JSON."""
            if message_id in self.messages:
                del self.messages[message_id]  # Удаляем запись из self.messages
                # Сохраняем изменения в JSON файл
                with open('messages.json', 'w') as file:
                    json.dump(self.messages, file, indent=4)
                print(f"Message with ID {message_id} has been removed from messages.")

        # Создание кнопок
        def create_callback(action):
            async def button_callback(interaction):
                self.message_data = self.messages.get(message_id)
                if not self.message_data:
                    await interaction.response.send_message("Данные сообщения недоступны.", ephemeral=True)
                    print(f"Нет данных для message_id: {message_id}")
                    return

                if not any(role.id in self.allowed_role_ids for role in interaction.user.roles):
                    await interaction.response.send_message("У вас нет прав для выполнения этого действия.", ephemeral=True)
                    return

                if action == "Принять":
                    self.messages[message_id]["status"] = "Принято"
                    self.messages[message_id]["is_active"] = False
                    with __init__.app.app_context():
                        user = __init__.Users.query.filter_by(static=self.messages[message_id]["static"]).first()
                        user.nikname = self.messages[message_id]["nickname"]
                        __init__.db.session.commit()
                    
                    userDS = await self.bot.fetch_user(self.messages[message_id]["discordid"])
                    embed = disnake.Embed(
                    title="Запрос на смену Nickname • ОДОБРЕНО",
                    description=(
                    f"> Одобрен: <@{interaction.user.id}> (`{interaction.user.id} | {interaction.user.name}`)\n\n"
                    f"> - **{"Ваш текущий nickname и static."}**\n"
                    f"``` {self.messages[message_id]["nickname"]} | #{self.messages[message_id]["static"]}```\n\n"
                    ))
                    embed.set_footer(text="Если вы считаете, что это ошибочное сообщение, свяжитесь с 6ot9lpa")
                    await userDS.send(embed=embed)

                    
                elif action == "Отклонить":
                    self.messages[message_id]["status"] = "Отклонено"
                    self.messages[message_id]["is_active"] = False
                    
                    userDS = await self.bot.fetch_user(self.messages[message_id]["discordid"])
                    embed = disnake.Embed(
                    title="Запрос на смену Nickname • ОТКАЗАНО",
                    description=(
                    f"> Отказано: <@{interaction.user.id}> (`{interaction.user.id} | {interaction.user.name}`)\n\n"
                    f"> - **{"Ваш текущий nickname и static."}**\n"
                    f"``` {self.messages[message_id]["nickname"]} | #{self.messages[message_id]["static"]}```\n\n"
                    ))
                    embed.set_footer(text="Если вы считаете, что это ошибочное сообщение, свяжитесь с 6ot9lpa")
                    await userDS.send(embed=embed)
                    

                # Обновляем футер с результатом
                embed = interaction.message.embeds[0]
                embed.set_footer(text=f"Статус: {self.messages[message_id]['status']}")

                # Удаляем кнопки из View
                await interaction.message.edit(view=None, embed=embed)

                # Сохраняем данные
                self.save_message_data()
                await self.update_message_view(message_id)

                await interaction.response.send_message(f"Смена nickname изменен на {self.messages[message_id]['status']}.", ephemeral=True)
                remove_message(message_id)
                
            return button_callback

        # Создаем кнопки
        accept_button = disnake.ui.Button(label="Принять", style=ButtonStyle.green, custom_id=f"accept_{message_id}")
        reject_button = disnake.ui.Button(label="Отклонить", style=ButtonStyle.red, custom_id=f"reject_{message_id}")

        accept_button.callback = create_callback("Принять")
        reject_button.callback = create_callback("Отклонить")

        view.add_item(accept_button)
        view.add_item(reject_button)

        # Убираем кнопки, если статус уже изменен
        if self.messages.get(message_id, {}).get("status") in ["Принято", "Отклонено"]:
            view.clear_items()

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
        """Обновляет или восстанавливает View для конкретного сообщения."""
        message_data = self.messages.get(message_id)
        if not message_data:
            print(f"Данные для сообщения {message_id} не найдены")
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
            
            view = await self.create_moderation_view(message_id)

            await message.edit(view=view) 

        except Exception as e:
            print(f"Ошибка при восстановлении View для сообщения {message_id}: {e}")
            traceback.print_exc()

    @tasks.loop(minutes=10)
    async def update_buttons(self):
        """Обновляет кнопки каждые 10 минут."""
        for message_id, message_data in self.messages.items():
            await self.update_message_view(message_id)
    
    async def send_dm_change(self, old_nickname, new_nickname, static, discordid, reason):
        try:
            self.message_data = {
                "channel_id": self.channel_id,
                "button_label": "Модерация",
                "message_id": None,
                "static": static,
                "discordid": discordid,
                "nickname": new_nickname,
                "status": None,
                "is_active": True 
            }

            # Пытаемся получить канал
            channel = await self.get_channel_with_retry(self.channel_id)
            if not channel:
                print(f"Канал с ID {self.channel_id} не найден после нескольких попыток")
                return
            
            user = await self.bot.fetch_user(discordid)
            embed = disnake.Embed(
                title=f":bookmark_tabs: Заявление на смену имени!",
                description=(
                    f"> Автор заявления: <@{discordid}> (`{discordid} | {user.name}`)\n\n"
                    f"> - **{"Текущий nickname и static."}**\n"
                    f"``` {old_nickname} | #{static}```\n"
                    f"> - **{"Новый nickname и static."}**\n"
                    f"``` {new_nickname} | #{static}```\n"
                    f"> - **{"Причина смены nickname."}**\n"
                    f"``` {reason} ```\n"
                )
            )
            embed.set_footer(text="Статус: Ожидание модерации")

            # Отправляем сообщение в канал
            message = await channel.send(embed=embed)

            # Обновляем message_id в данных и сохраняем их
            self.message_data["message_id"] = str(message.id)
            self.messages[self.message_data["message_id"]] = self.message_data
            self.save_message_data()

            # Создаем View с кнопками и обновляем сообщение
            view = await self.create_moderation_view(self.message_data["message_id"])  # Важно использовать await
            await message.edit(view=view)

            print(f"Сообщение отправлено в канал {self.channel_id} с ID {message.id}")

        except Exception as e:
            print(f"Ошибка при отправке сообщения в канал {self.channel_id}: {e}")

        

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
async def process_change_nickname(setting_profile):
    pubsub = redis_client.pubsub()
    pubsub.subscribe('change_nickname')

    while True:
        message = pubsub.get_message()
        if message and message['type'] == 'message':
            try:
                print(f"Получено сообщение: {message['data']}")
                data = json.loads(message['data'])
                old_nickname = data['old_nickname']
                static = data['static']
                reason = data['reason']
                discordid = data['discordid']
                new_nickname = data['new_nickname']
                
                await setting_profile.send_dm_change(old_nickname, new_nickname, static, discordid, reason)
            except Exception as e:
                print(f"Ошибка обработки сообщения: {e}")
                traceback.print_exc()
        await asyncio.sleep(1)

def setup(bot):
    setting_profile = SettingProfile(bot)
    bot.loop.create_task(process_change_nickname(setting_profile))
    bot.add_cog(SettingProfile(bot))
    time.sleep(5)
    setting_profile.load_message_data()
    bot.loop.create_task(setting_profile.update_buttons())