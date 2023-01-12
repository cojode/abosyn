from aiogram import Bot, Dispatcher, executor, types
import datetime
import json
import recipe_model



rp = recipe_model.RecipeModel("havai/awesome_recipes")

context = {}
context_uptime = datetime.datetime.now()



with open("config.json") as f:
    config = json.load(f)
    
settings = config["settings"]
lits = config["str_literals"]


COOLDOWN = settings["delay"]
DEFAULT_DATE = datetime.datetime(2010,1,1, 0, 0, 0)

bot = Bot(token=settings["token"])
dp = Dispatcher(bot)



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
    print(lits["log_mes"]\
    % {"time": datetime.datetime.now(), "name": message.from_user.first_name,\
    "nick": message.from_user.username, "id": message.from_user.id, "text": text})



async def get_answer():
    return lits["pecipe_first"] + rp.generate_recipe(max_length=settings["max_length"])



@dp.message_handler(commands=["start", "help"])
async def get_help(message:types.Message):
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=lits["gen_com"])],],
        resize_keyboard=True,
        input_field_placeholder=lits["input_place"]
    )
    await message.answer(lits["help_mes"]\
                        % {"com": lits["gen_com"].lower()},\
                        reply_markup=keyboard)

@dp.message_handler(lambda message: message.text.lower() == lits["gen_com"].lower())
async def get_messages(message:types.Message):
    check_context_uptime()

    last_command_use_time = check_id_in_context(message.from_user.id)
    
    if (datetime.datetime.now() - last_command_use_time).seconds > COOLDOWN:
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
        % {"delay": COOLDOWN, "left": COOLDOWN - (datetime.datetime.now() - last_command_use_time).seconds})



if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)