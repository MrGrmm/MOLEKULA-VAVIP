from tortoise import Tortoise


async def init():
    # Настройка соединения с базой данных
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',  # Или другой DSN для вашей базы данных
        modules={'models': ['models']}  # Укажите путь к вашим моделям
    )
    # Создание таблиц в базе данных
    await Tortoise.generate_schemas()