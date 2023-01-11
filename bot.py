from aiogram import Bot, Dispatcher, executor, types
import datetime
import recipe_model



#в конфиге токен и время кулдауна
config_read = open("config", "r")
config = config_read.read().split()
config_read.close()

bot = Bot(token=config[0])
dp = Dispatcher(bot)

COOLDOWN = int(config[1])
DEFAULT_DATE = datetime.datetime(2010,1,1, 0, 0, 0)



context = {}
context_uptime = datetime.datetime.now()

def check_context_uptime():
    global context_uptime
    if (datetime.datetime.now() - context_uptime).seconds > 3600:
        context = {}
        context_uptime = datetime.datetime.now()

def check_id_in_context(uid):
    if uid not in context:
        context[uid] = DEFAULT_DATE
    return context[uid]

    
    
async def get_answer():
    rp = recipe_model.RecipeModel("havai/awesome_recipes")
    return "Ваш рецепт:\n\n" + rp.generate_recipe(max_length=1000)



@dp.message_handler(commands=["start", "help"])
async def get_help(message):
    await message.answer("Напишите \"хочу рецепт\" или просто \"рецепт\" для генерации рецепта")

@dp.message_handler(content_types=['text'])
async def get_messages(message):
    check_context_uptime()

    message_text = message.text.lower()
    
    if message_text == "хочу рецепт" or message_text == "рецепт":
        last_command_use_time = check_id_in_context(message.from_user.id)
        
        if (datetime.datetime.now() - last_command_use_time).seconds > COOLDOWN:
            context[message.from_user.id] = datetime.datetime.now()
            
            await message.answer("Ваш рецепт генерируется...")
            
            try:
                received_answer = await get_answer()
                for x in range(0, len(received_answer), 4096):
                    await message.answer(received_answer[x:x+4096])
            except:
                context[message.from_user.id] = DEFAULT_DATE
                await message.answer("Произошла какая-то ошибка!\nПожалуйста, пробуйте снова")
            
        else:
            await message.answer("Пожалуйста, пожалейте сервер!\nПерерыв между запросами "\
            + str(COOLDOWN) + " секунд\nМожно вызвать через "\
            + str(COOLDOWN - (datetime.datetime.now() - last_command_use_time).seconds) + " секунд")



if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)