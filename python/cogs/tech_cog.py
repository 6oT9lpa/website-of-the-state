import disnake, json, redis, asyncio, traceback
from disnake.ext import commands, tasks
import sys, os
from .ka_cog import db_session
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from __init__ import Users

def read_ranks(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
def get_rank_info(ranks, organization, rank_level):
    rank_info = None
    if organization in ranks:
        for rank_data in ranks[organization]:
            for level, name in rank_data.items():
                if level.strip("[]") == rank_level:
                    rank_info = name.strip()
                break
    return rank_info

class tech_cog(commands.Cog):
    @commands.slash_command(guild_ids=[1285214538144153630])
    async def user_info(self, inter: disnake.ApplicationCommandInteraction, static: str):
        required_role_id = 1298992919491117096 

        user_roles = inter.user.roles
        if not any(role.id == required_role_id for role in user_roles):
            await inter.response.send_message("У вас нет прав для выполнения этой команды.", ephemeral=True)
            return
        user = db_session.query(Users).filter_by(static=static).first()
        if user:
            nikname = user.nikname
            filename = "./python/name-ranks.json"
            rank = user.rankuser
            organ = user.organ
            ranks = read_ranks(filename)
            rank_name = get_rank_info(ranks, organ, rank)
            embed = disnake.Embed(
            title=f"Информация о {nikname}",
            color=disnake.Color.blue()
            )
            embed.add_field(name="Имя Фамилия:", value=nikname, inline=True)
            embed.add_field(name="Статик:", value=static, inline=True)
            embed.add_field(name="Дискорд:", value=f"<@{user.discordid}>", inline=True)
            embed.add_field(name="фракция:", value=user.organ, inline=True)

            embed.add_field(name="Выговоры:", value=f"{user.YW}/2, {user.SW}/3", inline=True)
            embed.add_field(name="Должность:", value=f"{rank} | {rank_name}", inline=True)
            await inter.response.send_message(embed=embed)
        else: 
            await inter.response.send_message("Пользователь не найден!", ephemeral=True)

def setup(bot):
    bot.add_cog(tech_cog(bot))