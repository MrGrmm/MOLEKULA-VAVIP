import asyncio
import logging


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
# router.message.register(file_handler, content_types=types.ContentType.PHOTO)
router.message.register(hi_message)
router.message.register(echo_handler)



# Функция для запуска бота
async def start_bot():
    try:
        await init() # Предполагаемая функция для инициализации, например подключение к БД
        await bot.delete_webhook(drop_pending_updates=True)   # Удаляет сообщения что были получены ботом пока о н был оффлайн
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logging.info('Остановка бота...')
        # Ваш код для корректного завершения работы, если это необходимо
    finally:
        if not dp.stop_polling():                                                                               #TODO
            logging.info('Останавливаем polling...')                                                            #TODO  Решить ошибку при выключении бота
            await dp.stop_polling()                                                                             #TODO

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(start_bot())
    except (SystemExit, KeyboardInterrupt):
        logging.info("Бот остановлен!")