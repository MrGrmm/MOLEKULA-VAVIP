

import logging
from tortoise import Tortoise
import os

# Настройка логгирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init():
    db_url = os.getenv('DB_URL', 'sqlite://db.sqlite3')
    modules = {'models': ['models']}
    
    try:
        logger.info("Инициализация соединения с базой данных...")
        await Tortoise.init(
            db_url=db_url,
            modules=modules
        )
        logger.info("Соединение с базой данных успешно установлено.")
        
        logger.info("Создание таблиц в базе данных...")
        await Tortoise.generate_schemas()
        logger.info("Таблицы успешно созданы.")
        
    except Exception as e:
        logger.error(f"Ошибка при инициализации базы данных: {e}")
        raise
