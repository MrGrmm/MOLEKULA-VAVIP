import asyncio
import logging


from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart

from config import API_TOKEN

from handlers import command_start_handler, echo_handler


bot = Bot(API_TOKEN, parse_mode=ParseMode.HTML)

# Создание роутера и регистрация обработчиков сообщений
router = Router()

router.message.register(command_start_handler, CommandStart())
router.message.register(echo_handler)

# Создание диспетчера и включение роутера
dp = Dispatcher()
dp.include_router(router)

# Функция для запуска бота
async def start_bot():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start_bot())