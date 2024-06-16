
import asyncio
import logging
import tortoise

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart


from config import API_TOKEN
from db import init

from handlers import command_start_handler, echo_handler, hi_message


bot = Bot(API_TOKEN, parse_mode=ParseMode.HTML)

# Создание роутера и регистрация обработчиков сообщений
router = Router()

# Создание диспетчера и включение роутера
dp = Dispatcher()
dp.include_router(router)

router.message.register(command_start_handler, CommandStart())
router.message.register(hi_message)
router.message.register(echo_handler)

async def start_bot():
    logging.info("Запуск бота...")
    try:
        await init()  # Инициализация, например подключение к БД
        await bot.delete_webhook(drop_pending_updates=True)  # Удаление сообщений, полученных ботом в оффлайн
        await dp.start_polling(bot)
    except (KeyboardInterrupt, SystemExit):
        logging.info("Остановка бота...")
    finally:
        await bot.session.close()
        logging.info("Соединение с ботом закрыто.")
        await dp.storage.close()
        logging.info("Хранилище диспетчера закрыто.")
        await tortoise.Tortoise.close_connections()
        logging.info("Соединение с базой данных закрыто.")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(start_bot())
    except (SystemExit, KeyboardInterrupt):
        logging.info("Бот остановлен!")

