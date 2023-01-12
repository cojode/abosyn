from aiogram import Bot, Dispatcher, executor, types
import datetime
import json
from config_loader import ConfigLoader
import recipe_model



rp = recipe_model.RecipeModel("havai/awesome_recipes")

config = ConfigLoader()
  
settings = config.get_section("bot_settings")
lits = config.get_section("bot_str_literals")

bot = Bot(token=settings["token"])
dp = Dispatcher(bot)



context = {}
context_uptime = datetime.datetime.now()

DEFAULT_DATE = datetime.datetime(2010,1,1, 0, 0, 0)

def check_id_in_context(uid):
    if uid not in context:
        context[uid] = DEFAULT_DATE
    return context[uid]

def check_context_uptime():
    global context_uptime
    if (datetime.datetime.now() - context_uptime).seconds > 3600:
        context = {}
        context_uptime = datetime.datetime.now()



def user_spy(message, text):
    lits = config.get_section("bot_str_literals", True)
    
    print(lits["log_mes"]\
    % {"time": datetime.datetime.now(), "name": message.from_user.first_name,\
    "nick": message.from_user.username, "id": message.from_user.id, "text": text})



async def get_answer():
    config.update()
    settings = config.get_section("bot_settings")
    lits = config.get_section("bot_str_literals")
    
    return lits["pecipe_first"] + rp.generate_recipe(max_length=settings["max_length"])

def update_keyboard():
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=lits["gen_com"])],],
        resize_keyboard=True,
        input_field_placeholder=lits["input_place"]
    )
    return keyboard



@dp.message_handler(commands=["start", "help"])
async def get_help(message:types.Message):
    lits = config.get_section("bot_str_literals", True)
    
    keyboard = update_keyboard()
    
    await message.answer(lits["help_mes"]\
                        % {"com": lits["gen_com"].lower()},\
                        reply_markup=keyboard)

@dp.message_handler(lambda message: message.text.lower() == lits["gen_com"].lower())
async def get_messages(message:types.Message):
    config.update()
    settings = config.get_section("bot_settings")
    lits = config.get_section("bot_str_literals")
    
    check_context_uptime()
    
    keyboard = update_keyboard()

    last_command_use_time = check_id_in_context(message.from_user.id)
    
    if (datetime.datetime.now() - last_command_use_time).seconds > settings["delay"]:
        context[message.from_user.id] = datetime.datetime.now()
        
        user_spy(message, "generating recipe")
        
        try:
            await message.answer(lits["waiting_gen"])
            
            received_answer = await get_answer()
            for x in range(0, len(received_answer), 4096):
                await message.answer(received_answer[x:x+4096])
        except:
            context[message.from_user.id] = DEFAULT_DATE
            await message.answer(lits["error_mes"])
        
    else:
        await message.answer(lits["delay_mes"]\
        % {"delay": settings["delay"], "left": settings["delay"] - (datetime.datetime.now() - last_command_use_time).seconds})



if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)