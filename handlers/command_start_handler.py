from aiogram.types import Message
from aiogram.utils.markdown import hbold
from models import User


async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Предполагаем, что у объекта message есть атрибут from_user,
    # который возвращает объект пользователя Telegram.
    telegram_user = message.from_user
    
    # Использование get_or_create для предотвращения дублирования данных пользователя
    user, created = await User.get_or_create(
        telegram_user_id=telegram_user.id,
        defaults={
            'fullname': telegram_user.full_name,
            'username': telegram_user.username,
            'phone_number': None,  # Замените None на актуальные данные, если они у вас есть
            'email': None,         # Замените None на актуальные данные
            'location': None       # Замените None на актуальные данные
        }
    )
    
    if created:
        # Если пользователь был создан
        await message.answer(f"Привет, {hbold(user.fullname)}! Меня зовут MOLEKULA, приятно познакомится.")
    else:
        # Если пользователь уже существует
        await message.answer(f"С возвращением, {hbold(user.fullname)}! MOLEKULA, к вашим услугам.")
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    pass
