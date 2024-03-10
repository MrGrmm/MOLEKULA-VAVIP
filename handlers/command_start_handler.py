from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.markdown import hbold
from models import User



async def command_start_handler(message: Message):
    telegram_user = message.from_user
    # Пытаемся получить пользователя из БД по его идентификатору в Telegram
    user = await User.get_or_none(telegram_user_id=telegram_user.id)
    if user is None:
        # Если пользователь не найден, создаем новую запись
        user = await User.create(
            telegram_user_id=telegram_user.id,
            telegram_fullname=telegram_user.full_name,
            username=telegram_user.username,
        )
        welcome_text = f"Привет, {telegram_user.full_name}! Меня зовут MOLEKULA, приятно познакомиться."
    else:
        # Если пользователь уже существует, просто отправляем приветствие
        welcome_text = f"С возвращением, {user.telegram_fullname}! MOLEKULA, к вашим услугам."

    # Отправляем соответствующее приветственное сообщение пользователю
    await message.answer(welcome_text, reply_markup=ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[KeyboardButton(text="Привет")]]))