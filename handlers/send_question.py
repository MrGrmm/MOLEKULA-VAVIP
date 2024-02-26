"""
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
# Предполагается, что у вас уже есть функция для извлечения вариантов ответов из БД

async def send_question(user_id):
    # Извлечение вопроса и вариантов ответов из БД
    question, answer_options = await get_question_and_answers_from_db(user_id)
    
    # Создание клавиатуры
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    
    # Добавление кнопок в клавиатуру
    for option in answer_options.split(','):
        keyboard.add(KeyboardButton(option.strip()))
    
    # Отправка сообщения пользователю с вопросом и клавиатурой
    await bot.send_message(user_id, question, reply_markup=keyboard)
"""