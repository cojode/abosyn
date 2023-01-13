from aiogram import Bot, Dispatcher, executor, types
import datetime
from config_loader import ConfigLoader
import recipe_model
import logging

config = ConfigLoader()

settings = config.get_section("bot_settings")

log_format = settings["log_format"]
formatter = logging.Formatter(log_format)

console_logger = logging.StreamHandler()
console_logger.setFormatter(formatter)

log_file = settings["log_file"]
file_logger = logging.FileHandler(log_file)
file_logger.setFormatter(formatter)

log_level = settings["log_level"]
logger = logging.getLogger()
logger.addHandler(console_logger)
logger.addHandler(file_logger)
logger.setLevel(log_level * 10)

logger.info("Config loaded")
logger.info("Loading model...")
rp = recipe_model.RecipeModel("havai/awesome_recipes")
logger.info("Model loaded")

bot = Bot(token=settings["token"])
logger.info("Bot login succesful")
dp = Dispatcher(bot)


context = {}
context_uptime = datetime.datetime.now()

DEFAULT_DATE = datetime.datetime(2010, 1, 1, 0, 0, 0)


def check_id_in_context(uid):
    if uid not in context:
        context[uid] = DEFAULT_DATE
    return context[uid]


def check_context_uptime():
    global context_uptime
    if (datetime.datetime.now() - context_uptime).seconds > 3600:
        context = {}
        context_uptime = datetime.datetime.now()


async def get_answer():
    config.update()
    settings = config.get_section("bot_settings")
    lits = config.get_section("bot_str_literals")

    return lits["pecipe_first"] + rp.generate_recipe(max_length=settings["max_length"])


def update_keyboard():
    config.update()
    lits = config.get_section("bot_str_literals")

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=lits["gen_com"])],],
        resize_keyboard=True,
        input_field_placeholder=lits["input_place"]
    )
    return keyboard


@dp.message_handler(commands=["start", "help"])
async def get_help(message: types.Message):
    config.update()
    lits = config.get_section("bot_str_literals")

    keyboard = update_keyboard()

    await message.answer(lits["help_mes"]
                         % {"com": lits["gen_com"].lower()},
                         reply_markup=keyboard)


@dp.message_handler(lambda message: message.text.lower() == config.get_section("bot_str_literals")["gen_com"].lower())
async def get_messages(message: types.Message):
    config.update()
    settings = config.get_section("bot_settings")
    lits = config.get_section("bot_str_literals")

    check_context_uptime()

    keyboard = update_keyboard()

    last_command_use_time = check_id_in_context(message.from_user.id)

    if (datetime.datetime.now() - last_command_use_time).seconds > settings["delay"]:
        context[message.from_user.id] = datetime.datetime.now()

        logger.info("Generating recipe...")
        logger.info("Sender info: " % {
            "name": message.from_user.first_name,
            "nick": message.from_user.username,
            "id": message.from_user.id
        }
        )

        try:
            await message.answer(lits["waiting_gen"], reply_markup=keyboard)

            received_answer = await get_answer()
            for x in range(0, len(received_answer), 4096):
                await message.answer(received_answer[x:x+4096], reply_markup=keyboard)
        except:
            context[message.from_user.id] = DEFAULT_DATE
            await message.answer(lits["error_mes"], reply_markup=keyboard)

    else:
        await message.answer(lits["delay_mes"]
                             % {"delay": settings["delay"], "left": settings["delay"] - (datetime.datetime.now() - last_command_use_time).seconds},
                             reply_markup=keyboard)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
