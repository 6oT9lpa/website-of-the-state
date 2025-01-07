import disnake, json, redis, asyncio, traceback
from disnake.ext import commands

class SendVerificationCodeToUser(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def sendCode(self, discord, code):
        try:
            print(f"Попытка отправить сообщение пользователю с ID: {discord}")
            user = await self.bot.fetch_user(discord)

            embed = disnake.Embed(
                title=f"Ваш Discord ID был использован для регистрации на Majestic",
                description=(
                    f"Если это не вы, никому не передавйте код авторизации\n"
                    f"Ваш код для авторизации: {code} \n"
                ),
                color=disnake.Color.green()
            )
            embed.set_footer(text="Если вы считаете, что это ошибочное сообщение, свяжитесь с 6ot9lpa")

            await user.send(embed=embed)
            print(f"Сообщение отправлено пользователю {discord}")
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {discord}: {e}")
            traceback.print_exc()

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)     
async def process_verification_code(manager):
    pubsub = redis_client.pubsub()
    pubsub.subscribe('verification_code')

    while True:
        message = pubsub.get_message()
        if message and message['type'] == 'message':
            try:
                print(f"Получено сообщение: {message['data']}")
                data = json.loads(message['data'])
                discord = data['discord']
                code = data['code']
                
                await manager.sendCode(discord, code)
            except Exception as e:
                print(f"Ошибка обработки сообщения: {e}")
                traceback.print_exc()
        await asyncio.sleep(1)     
        
def setup(bot):
    manager = SendVerificationCodeToUser(bot)
    bot.loop.create_task(process_verification_code(manager))
    bot.add_cog(SendVerificationCodeToUser(bot))
   