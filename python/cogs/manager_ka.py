import disnake, json, redis, asyncio, traceback
from disnake.ext import commands
from datetime import datetime


def find_fraction_channel(fraction):
    fraction_channels = {
        "LSPD": 1323282948316725372,
        "FIB": 1323282948316725372,
        "LSCSD": 1323282948316725372,
        "SANG": 1323282948316725372,
        "EMS": 1323282948316725372,
        "GOV": 1323282948316725372,
        "WN": 1323282948316725372
    }
    
    return fraction_channels[fraction]

def read_ranks(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def get_rank_info(ranks, organization, rank_level):
    rank_info = None
    if organization in ranks:
        for rank_data in ranks[organization]:
            if rank_data['id'] == rank_level:
                return rank_data['name']
    return rank_info

class ManagerAuditMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def handle_action(self, action, static_to, discord_id_from, discord_id_to, curr_rank, prev_rank, nikname_from, nikname_to, reason, fraction):
        channel = self.bot.get_channel(find_fraction_channel(fraction))
        filename = "./python/name-ranks.json"
        updated_ranks = read_ranks(filename)
        curr_rank_name = get_rank_info(updated_ranks, fraction, curr_rank)
        prev_rank_name = get_rank_info(updated_ranks, fraction, prev_rank)
        
        if action == "Invite":
            embed = disnake.Embed(
                title=f"Кадровый аудит • Принятие во фракцию {fraction} || {nikname_to} #{static_to} ||",
                color=disnake.Color.green()
            )
            
            embed.add_field(name=" ", value=f"Сотрудник <@{discord_id_from}> | {nikname_from} принял гражданина <@{discord_id_to}> | {nikname_to} #{static_to}", inline=False)
            embed.add_field(name="> Имя Фамилия (гражданина)", value=f"```{nikname_to}```", inline=True)
            embed.add_field(name="> Паспорт (гражданина)", value=f"```{static_to}```", inline=True)
            embed.add_field(name="> Причина", value=f"```{reason}```", inline=False)
            embed.add_field(name="> Ранг", value=f"```Принят на [{curr_rank}] {curr_rank_name}```", inline=False)
            
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            embed.set_footer(text=f"Дата: {current_datetime}")

            await channel.send(
                content=f'Сотрудник оформил кадровый аудит <@{discord_id_from}>',
                embed=embed
            )

        elif action == "Dismissal":
            embed = disnake.Embed(
                title=f"Кадровый аудит • Увольнение с фракции {fraction} || {nikname_to} #{static_to} ||",
                color=disnake.Color.red()
            )
                
            embed.add_field(name=" ", value=f"Сотрудник <@{discord_id_from}> | {nikname_from} уволил сотрудника <@{discord_id_to}> | {nikname_to} #{static_to}", inline=False)
            embed.add_field(name="> Имя Фамилия (сотрудника)", value=f"```{nikname_to}```", inline=True)
            embed.add_field(name="> Паспорт (сотрудника)", value=f"```{static_to}```", inline=True)
            embed.add_field(name="> Причина", value=f"```{reason}```", inline=False)
            embed.add_field(name="> Ранг", value=f"```Уволен с [{prev_rank}] {prev_rank_name}```", inline=False)
            
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            embed.set_footer(text=f"Дата: {current_datetime}")

            await channel.send(
                content=f'Сотрудник оформил кадровый аудит <@{discord_id_from}>',
                embed=embed
            )
        elif action == "Raising":
            embed = disnake.Embed(
                title=f"Кадровый аудит • Повышение || {nikname_to} #{static_to} ||",
                color=disnake.Color.yellow()
            )
                
            embed.add_field(name=" ", value=f"Сотрудник <@{discord_id_from}> | {nikname_from} повысил сотрудника <@{discord_id_to}> | {nikname_to} #{static_to}", inline=False)
            embed.add_field(name="> Имя Фамилия (сотрудника)", value=f"```{nikname_to}```", inline=True)
            embed.add_field(name="> Паспорт (сотрудника)", value=f"```{static_to}```", inline=True)
            embed.add_field(name="> Причина", value=f"```{reason}```", inline=False)
            embed.add_field(name="> Ранг", value=f"```Повышен до [{curr_rank}] {curr_rank_name} - предыдущий [{prev_rank}] {prev_rank_name}```", inline=False)
            
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            embed.set_footer(text=f"Дата: {current_datetime}")

            await channel.send(
                content=f'Сотрудник оформил кадровый аудит <@{discord_id_from}>',
                embed=embed
            )
            
        elif action == "Demotion":
            embed = disnake.Embed(
                title=f"Кадровый аудит • Понижение || {nikname_to} #{static_to} ||",
                color=disnake.Color.yellow()
            )
                
            embed.add_field(name=" ", value=f"Сотрудник <@{discord_id_from}> | {nikname_from} понизил сотрудника <@{discord_id_to}> | {nikname_to} #{static_to}", inline=False)
            embed.add_field(name="> Имя Фамилия (сотрудника)", value=f"```{nikname_to}```", inline=True)
            embed.add_field(name="> Паспорт (сотрудника)", value=f"```{static_to}```", inline=True)
            embed.add_field(name="> Причина", value=f"```{reason}```", inline=False)
            embed.add_field(name="> Ранг", value=f"```Понижен до [{curr_rank}] {curr_rank_name} - предыдущий [{prev_rank}] {prev_rank_name}```", inline=False)
            
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            embed.set_footer(text=f"Дата: {current_datetime}")
            await channel.send(
                content=f'Сотрудник оформил кадровый аудит <@{discord_id_from}>',
                embed=embed
            )

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)     
async def process_ka_messages(manager_audit):
    pubsub = redis_client.pubsub()
    pubsub.subscribe('ka_channel')

    while True:
        message = pubsub.get_message()
        if message and message['type'] == 'message':
            try:
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
                fraction = data['fraction']
                
                await manager_audit.handle_action(action, static_to, discord_id_from, discord_id_to, curr_rank, prev_rank, nikname_from, nikname_to, reason, fraction)
            except Exception as e:
                print(f"Ошибка обработки сообщения: {e}")
                traceback.print_exc()
        await asyncio.sleep(1)    
        
def setup(bot):
    manager_audit =  ManagerAuditMessage(bot)
    bot.loop.create_task(process_ka_messages(manager_audit))
    bot.add_cog(ManagerAuditMessage(bot))