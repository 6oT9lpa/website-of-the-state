import disnake
import json
from disnake.ext import commands, tasks
import asyncio
import datetime
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from __init__ import db, Users, app, PermissionUsers

servers = [
    {'id': 1150681470634049668, 'fraction_name': 'LSPD', 'rank': 16},
    {'id': 1285214538144153630, 'fraction_name': 'FIB', 'rank': 13}
]

ROLE_NAME = "Leader"

class lid_cog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.start_monitoring())

    async def monitor_and_update_roles(self):
        for server_info in servers:
            guild = next((g for g in self.bot.guilds if g.id == server_info['id']), None)
            if not guild:
                print(f"Сервер с ID {server_info['id']} не найден")
                continue
            role = disnake.utils.get(guild.roles, name=ROLE_NAME)
            if role is None:
                print(f"Роль '{ROLE_NAME}' в {server_info['fraction_name']} {server_info['id']} не найдена!")
                continue
            if role:
                found_member = False
                for member in guild.members:
                    if role in member.roles:
                            with app.app_context():
                                # Ищем запись пользователя в БД или создаём новую
                                newleader = db.session.query(Users).filter_by(discordid=member.id).first()
                                if newleader:
                                    fraction_name = server_info.get('fraction_name')
                                    rank = server_info.get('rank')
                                    db.session.query(Users).filter_by(discordid=member.id).update({
                                        "curr_rank": rank,
                                        "organ": fraction_name,
                                        "action": "Invite"
                                    })
                                    db.session.query(PermissionUsers).filter_by(user_static=newleader.static).update({
                                        "lider": True
                                    })
                                    db.session.commit()
                                    print(f'Информация о лидере {server_info['fraction_name']} обновлена!')
                                else:
                                    print(f'Лидера {server_info['fraction_name']} нет в базе.')
                                found_member = True
                if not found_member:
                    with app.app_context():
                        # Ищем запись пользователя в БД или создаём новую
                        fraction_name = server_info.get('fraction_name')
                        rank = server_info.get('rank')
                        newleader = db.session.query(Users).filter_by(rankuser=rank, organ=fraction_name).first()
                        if newleader:
                            db.session.query(Users).filter_by(rankuser=rank, organ=fraction_name).update({
                                "rankuser": 0,
                                "action": "Dismissal"
                            })
                            db.session.query(PermissionUsers).filter_by(user_static=newleader.static).update({
                                "lider": False
                            })
                            db.session.commit()
                            print(f'Лидер {server_info['fraction_name']} не найден!')

    async def start_monitoring(self):
        await self.bot.wait_until_ready()
        while True:
            now = datetime.datetime.now()
            next_run = (datetime.datetime.combine(now + datetime.timedelta(days=1), datetime.time.min) - now).total_seconds()
            await asyncio.sleep(next_run)
            await self.monitor_and_update_roles()  # Выполняем проверку ролей
            #await asyncio.sleep(10)
def setup(bot):
    bot.add_cog(lid_cog(bot))