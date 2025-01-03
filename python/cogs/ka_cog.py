import disnake
from disnake import Intents
from disnake.ext import commands
import sys
import os
import json
import asyncio
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import datetime
from enum import Enum
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from __init__ import Users

engine = create_engine('mysql://root:arnetik1@localhost:3306/site')
Session = sessionmaker(bind=engine)
db_session = Session()

print('123')
intents = Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix=".", intents=intents)

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'servers_config.json')

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as file:
            config = json.load(file)
    except FileNotFoundError:
        config = {'servers': {}}
    return config

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w') as file:
            json.dump(config, file, indent=4)
    except Exception as e:
        print(f"Error saving configuration: {e}")

class warn_variants(str, Enum):
    Устный = 'ustnik'
    Строгий = 'strogaj'

class warn_variants_set(str, Enum):
    Устный = 'ustnik'
    Строгий1 = 'strogaj'
    Строгий2 = 'strogaj2'

class ka_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
    #@bot.group()
    #async def settings(self, inter: disnake.ApplicationCommandInteraction):
    #    """Группа команд для настройки системы."""
    #    await inter.response.send_message("Доступные команды настройки:", ephemeral=True)

    @commands.slash_command()
    async def add_department_role(self, inter: disnake.ApplicationCommandInteraction, department: str, role: disnake.Role):
        author = db_session.query(Users).filter(Users.discordid == inter.author.id).all()
        permtot = False
        for user in author:
            if user.permissions[0].lider or user.permissions[0].admin:
                permtot = True
                break
        if permtot:
            config = load_config()
            server_id = str(inter.guild.id)
            if server_id not in config['servers']:
                config['servers'][server_id] = {}
            
            if 'departments' not in config['servers'][server_id]:
                config['servers'][server_id]['departments'] = {}
            
            if department not in config['servers'][server_id]['departments']:
                config['servers'][server_id]['departments'][department] = []
            
            if str(role.id) not in config['servers'][server_id]['departments'][department]:
                config['servers'][server_id]['departments'][department].append(str(role.id))
            
            save_config(config)
            
            await inter.response.send_message(f"Роль <@&{role.id}> добавлена для отдела {department}.", ephemeral=True)
        else:
            await inter.response.send_message(f"Только лидер и админитсрация может менять информацию о ролях!", ephemeral=True)
    
    @commands.slash_command()
    async def remove_department_role(self, inter: disnake.ApplicationCommandInteraction, department: str):
        author = db_session.query(Users).filter(Users.discordid == inter.author.id).all()
        permtot = False
        for user in author:
            if user.permissions[0].lider or user.permissions[0].admin:
                permtot = True
                break
        if permtot:
            config = load_config()
            server_id = str(inter.guild.id)
            if server_id not in config['servers']:
                config['servers'][server_id] = {}
            
            if 'departments' not in config['servers'][server_id]:
                config['servers'][server_id]['departments'] = {}
            
            if department in config['servers'][server_id]['departments']:
                del config['servers'][server_id]['departments'][department]
                save_config(config)
                
                await inter.response.send_message(f"Информация об отделе {department} удалена.")
            else:
                await inter.response.send_message(f"Отдел {department} не существует.", ephemeral=True)
        else:
            await inter.response.send_message(f"Только лидер и админитсрация может менять информацию о ролях!", ephemeral=True)

    @commands.slash_command()
    async def add_department_otrab(self, inter: disnake.ApplicationCommandInteraction, department: str, warning_type: warn_variants, otrabotka: str):
        author = db_session.query(Users).filter(Users.discordid == inter.author.id).all()
        permtot = False
        for user in author:
            if user.permissions[0].lider or user.permissions[0].admin:
                permtot = True
                break
        if permtot:
            config = load_config()
            server_id = str(inter.guild.id)
            departmentj = str(department)
            if server_id not in config['servers']:
                config['servers'][server_id] = {}
        
            if 'otrabotaika' not in config['servers'][server_id]:
                config['servers'][server_id]['otrabotaika'] = {}
        
            if 'messages' not in config['servers'][server_id]['otrabotaika']:
                config['servers'][server_id]['otrabotaika']['messages'] = {}
            if department not in config['servers'][server_id]['otrabotaika']['messages']:
                config['servers'][server_id]['otrabotaika']['messages'][department] = {}
            if warning_type not in config['servers'][server_id]['otrabotaika']['messages'][department]:
                config['servers'][server_id]['otrabotaika']['messages'][department][warning_type] = []
            if str(otrabotka) not in config['servers'][server_id]['otrabotaika']['messages'][departmentj][warning_type]:
                config['servers'][server_id]['otrabotaika']['messages'][department][warning_type].append(str(otrabotka))
            
            save_config(config)
            
            await inter.response.send_message(f"Отработка добавлена для отдела {department}.", ephemeral=True)
        else:
            await inter.response.send_message(f"Только лидер и админитсрация может менять информацию о отработках!", ephemeral=True)

    @commands.slash_command()
    async def remove_department_otrab(self, inter: disnake.ApplicationCommandInteraction, warning_type: warn_variants, department: str):
        author = db_session.query(Users).filter(Users.discordid == inter.author.id).all()
        permtot = False
        for user in author:
            if user.permissions[0].lider or user.permissions[0].admin:
                permtot = True
                break
        if permtot:
            config = load_config()
            server_id = str(inter.guild.id)
        
            # Проверяем, существует ли сервер в конфиге
            if server_id in config['servers']:
                server_config = config['servers'][server_id]  # Инициализируем переменную 'server_config'
                
                # Проверяем, существует ли раздел 'otrabotaika' для сервера
                if 'otrabotaika' in server_config and 'messages' in server_config['otrabotaika']:
                    # Проверяем, существует ли департамент в 'messages' (приводим к единому регистру)
                    department_lower = department.lower()  # Приводим департамент к нижнему регистру для сравнения
                    messages = server_config['otrabotaika']['messages']
                    
                    # Печать для отладки - какие департаменты есть в конфиге
                    #print(f"Существующие департаменты: {list(messages.keys())}")

                    # Ищем департамент в конфиге (без учёта регистра)
                    matching_department = next((dept for dept in messages if dept.lower() == department_lower), None)
                    
                    if matching_department:
                        department_config = messages[matching_department]

                        # Проверяем, существует ли указанный тип выговора для департамента
                        if warning_type in department_config:
                            # Удаляем информацию о выговоре для департамента
                            del department_config[warning_type]

                            # Если департамент пустой после удаления, убираем его из списка
                            if not department_config:
                                del messages[matching_department]

                            save_config(config)
                            await inter.response.send_message(f"Информация об отделе {matching_department} и типе выговора {warning_type} удалена.", ephemeral=True)
                        else:
                            await inter.response.send_message(f"Тип выговора {warning_type} не найден в отделе {matching_department}.", ephemeral=True)
                    else:
                        await inter.response.send_message(f"Отдел {department} не существует.", ephemeral=True)
                else:
                    await inter.response.send_message(f"Информация об отработках не найдена для этого сервера.", ephemeral=True)
            else:
                await inter.response.send_message(f"Сервер не найден в конфигурации.", ephemeral=True)
        else:
            await inter.response.send_message(f"Только лидер и администрация могут менять информацию об отработках!", ephemeral=True)

    @commands.slash_command()
    async def set_warn_role(self, inter: disnake.ApplicationCommandInteraction, warning_type: warn_variants_set, role: disnake.Role = None):
        author = db_session.query(Users).filter(Users.discordid == inter.author.id).all()
        permtot = False
        for user in author:
            if user.permissions[0].lider or user.permissions[0].admin:
                permtot = True
                break
        if permtot:
            config = load_config()
            server_id = str(inter.guild.id)
            if server_id not in config['servers']:
                config['servers'][server_id] = {}

            if 'otrabotaika' not in config['servers'][server_id]:
                config['servers'][server_id]['otrabotaika'] = {}

            if 'warn_roles' not in config['servers'][server_id]['otrabotaika']:
                config['servers'][server_id]['otrabotaika']['warn_roles'] = {}
            if role is None:
                if warning_type in config['servers'][server_id]['otrabotaika']['warn_roles']:
                    del config['servers'][server_id]['otrabotaika']['warn_roles'][warning_type]
                    save_config(config)

                if warning_type.lower() == 'ustnik':
                    await inter.response.send_message("Роль для устного выговора удалена.", ephemeral=True)
                elif warning_type.lower() == 'strogaj1':
                    await inter.response.send_message("Роль для строгого выговора 1/3 удалена.", ephemeral=True)
                elif warning_type.lower() == 'strogaj2':
                    await inter.response.send_message("Роль для строгого выговора 2/3 удалена.", ephemeral=True)
                else:
                    await inter.response.send_message(f"Нет информации о роли для типа выговора '{warning_type}'.", ephemeral=True)

            else:
                # Добавляем роль в конфигурацию
                if warning_type not in config['servers'][server_id]['otrabotaika']['warn_roles']:
                    config['servers'][server_id]['otrabotaika']['warn_roles'][warning_type] = []

                if str(role.id) not in config['servers'][server_id]['otrabotaika']['warn_roles'][warning_type]:
                    config['servers'][server_id]['otrabotaika']['warn_roles'][warning_type].append(str(role.id))

                save_config(config)

                if warning_type.lower() == 'ustnik':
                    await inter.response.send_message(f"Роль <@&{role.id}> установлена как роль выговора для устного выговора.", ephemeral=True)
                elif warning_type.lower() == 'strogaj':
                    await inter.response.send_message(f"Роль <@&{role.id}> установлена как роль выговора для строгого выговора.", ephemeral=True)
        else:
            await inter.response.send_message(f"Только лидер и админитсрация может менять информацию о отработках!", ephemeral=True)

    @commands.slash_command()
    async def warn(inter: disnake.ApplicationCommandInteraction, member: disnake.Member, passport: int, warning_type: warn_variants, reason_type: str):
        author = db_session.query(Users).filter(Users.discordid == inter.author.id).all()
        permtot = False
        for user in author:
            if user.permissions[0].high_staff:
                permtot = True
                break
        if permtot:
            config = load_config()
            server_config = config['servers'].get(str(inter.guild.id), {})
            otrabotaika_messages = server_config.get('otrabotaika', {}).get('messages', {})
            warn_roles = server_config.get('otrabotaika', {}).get('warn_roles', {})
            departments = server_config.get('departments', {})
            user_department = None
            for dept, roles in departments.items():
                for role_id in roles:
                    if any(isinstance(r, disnake.Role) and r.id == int(role_id) for r in member.roles):
                        user_department = dept
                        break
                # Если департамент найден
            if user_department:
                user = db_session.query(Users).filter_by(static=passport).first()
                if user:
                    otrabotaika_message = otrabotaika_messages.get(user_department, {}).get(warning_type.lower(), "Не указано")
                    if isinstance(otrabotaika_message, list):
                        otrabotaika_message = ', '.join(otrabotaika_message)
                    else:
                        otrabotaika_message = otrabotaika_message
                    warn_role = 0
                    # Обновление полей YW и SW в зависимости от типа выговора
                    if warning_type.lower() == 'ustnik':
                            warn_name_embed = 'Устный'
                            color_emb = disnake.Color.yellow()
                            user.YW = user.YW + 1
                    elif warning_type.lower() == 'strogaj':
                            warn_name_embed = 'Строгий'
                            color_emb = disnake.Color.red()
                            user.SW = user.SW + 1
                    if user.YW == 2:
                        warn_role_list = warn_roles.get("ustnik", [])
                        if warn_role_list:
                            await member.remove_roles(disnake.Object(id=int(warn_role)))
                        user.YW = 0
                        user.SW = user.SW + 1
                    if user.SW == 1:
                        warn_role_list = warn_roles.get("strogaj1", [])
                        if warn_role_list:
                            warn_role = warn_role_list[0]
                    elif user.SW == 2:
                        warn_role_list = warn_roles.get("strogaj1", [])
                        if warn_role_list:
                            await member.remove_roles(disnake.Object(id=int(warn_role)))
                        warn_role_list = warn_roles.get("strogaj2", [])
                        if warn_role_list:
                            warn_role = warn_role_list[0]
                    embed = disnake.Embed(
                    title=f"Кадровый аудит • {warn_name_embed} выговор",
                    color=color_emb
                    )
                    embed.add_field(name="Выдал:", value=f"<@{inter.author.id}>", inline=True)
                    embed.add_field(name="Кому:", value=f"<@{member.id}>", inline=True)
                    embed.add_field(name="Паспорт:", value=user.static, inline=True)
                    embed.add_field(name="Причина:", value=reason_type, inline=True)
                    embed.add_field(name="Отработка", value=otrabotaika_message, inline=True)
                    embed.add_field(name="Итого:", value=f"{user.YW}/2, {user.SW}/3", inline=True)
                    db_session.query(Users).filter_by(static=passport).update({
                            "YW": user.YW,
                            "SW": user.SW
                        })
                                
                                #current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                #embed.set_footer(text=f"Дата: {current_datetime}")
                    if warn_role != "0" and warn_role:
                        try:
                            await member.add_roles(disnake.Object(id=int(warn_role)))
                        except disnake.Forbidden:
                            await inter.response.send_message("Бот не имеет прав для выдачи этой роли.", ephemeral=True)
                            return
                        except Exception as e:
                            await inter.response.send_message(f"Произошла ошибка: {e}", ephemeral=True)
                            return
                    await inter.response.send_message(embed=embed)
                    if user.SW == 3:
                        await inter.followup.send(f'<@{inter.author.id}> У <@{member.id}> 3 строгих выговора', ephemeral=True)

                        db_session.commit()  # Сохраняем изменения в базе данных
                else:
                    await inter.response.send_message("Игрок не найден!", ephemeral=True)
            else:
                await inter.response.send_message("Игрок не в отделе!", ephemeral=True)
        else:
            await inter.response.send_message("У вас нет прав!", ephemeral=True)

    @commands.slash_command()
    async def unwarn(inter: disnake.ApplicationCommandInteraction, member: disnake.Member, passport: int, warning_type: warn_variants, reason_type: str):
        author = db_session.query(Users).filter(Users.discordid == inter.author.id).all()
        permtot = False
        for user in author:
            if user.permissions[0].high_staff:
                permtot = True
                break
        if permtot:
                user = db_session.query(Users).filter_by(static=passport).first()
                config = load_config()
                server_config = config['servers'].get(str(inter.guild.id), {})
                warn_roles = server_config.get('otrabotaika', {}).get('warn_roles', {})
                if user:
                # Обновление полей YW и SW в зависимости от типа выговора
                        if warning_type.lower() == 'ustnik':
                            warn_name_embed = 'Устный'
                            warn_role_list = warn_roles.get("ustnik", [])
                            if warn_role_list:
                                warn_role = warn_role_list[0]
                            else:
                                warn_role = 0
                            user.YW = 0
                        elif warning_type.lower() == 'strogaj':
                            warn_name_embed = 'Строгий'
                            warn_role_list = warn_roles.get("strogaj1", [])
                            if warn_role_list:
                                warn_role = warn_role_list[0]
                            else:
                                warn_role = 0
                            user.SW = user.SW - 1
                        if user.SW == 1:
                            warn_role_list = warn_roles.get("strogaj1", [])
                            if warn_role_list:
                                warn_role = warn_role_list[0]
                        elif user.SW == 2:
                            warn_role_list = warn_roles.get("strogaj2", [])
                            if warn_role_list:
                                warn_role = warn_role_list[0]
                        embed = disnake.Embed(
                        title=f"Кадровый аудит • {warn_name_embed} снят",
                        color=disnake.Color.green()
                        )
                        embed.add_field(name="Снял:", value=f"<@{inter.author.id}>", inline=True)
                        embed.add_field(name="Кому:", value=f"<@{member.id}>", inline=True)

                        embed.add_field(name="Причина:", value=reason_type, inline=True)
                        embed.add_field(name="Итого:", value=f"{user.YW}/2, {user.SW}/3", inline=True)
                        db_session.query(Users).filter_by(static=passport).update({
                            "YW": user.YW,
                            "SW": user.SW
                        })
                        if warn_role != 0 and warn_role:
                            await member.remove_roles(disnake.Object(id=int(warn_role)))
                        #current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        #embed.set_footer(text=f"Дата: {current_datetime}")
                        await inter.response.send_message(embed=embed)

                        #db_session.update(new_warn)
                        db_session.commit()  # Сохраняем изменения в базе данных
        else:
            await inter.response.send_message("У вас нет прав для использования этой команды.", ephemeral=True)

def setup(bot):
    bot.add_cog(ka_cog(bot))
