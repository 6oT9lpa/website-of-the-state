import disnake, json, redis, asyncio, traceback
from disnake.ext import commands, tasks
from disnake import ButtonStyle, Intents
from datetime import datetime
from disnake.ui import View, Button
import os, time, sys

class ManagerAuditMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = 1286759030257221714
    
    async def handle_action(self, action, static_to, discord_id_from, discord_id_to, curr_rank, prev_rank, nikname_from, nikname_to, reason):
        channel = self.bot.get_channel(self.channel_id)
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

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)     
async def process_ka_messages(manager_audit):
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
                reason = data['reason']
                
                await manager_audit.handle_action(action, static_to, discord_id_from, discord_id_to, curr_rank, prev_rank, nikname_from, nikname_to, reason)
            except Exception as e:
                print(f"Ошибка обработки сообщения: {e}")
                traceback.print_exc()
        await asyncio.sleep(1)     
        
def setup(bot):
    manager_audit =  ManagerAuditMessage(bot)
    bot.loop.create_task(process_ka_messages(manager_audit))
    bot.add_cog(ManagerAuditMessage(bot))