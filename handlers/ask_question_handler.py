from aiogram import types
import sqlite3
import datetime
from models import User, Brief, Question


db = sqlite3.connect('db.sqlite3')


async def hi_message(callback_query: types.CallbackQuery):
    user = await User.get(telegram_user_id=callback_query.from_user.id)
    
    if not user:
        await callback_query.message.answer("You need to register first.")
        return

    brief = await Brief.create(
        user=user,
        created_at=datetime.datetime.now(),
    )

    # Получаем первый вопрос, который не имеет предшественника (предполагая, что это начало цепочки)
    first_question = await Question.filter(next_question_id__isnull=True).first()

    if first_question:
        await callback_query.message.answer(first_question.question)

        # Здесь мы сохраняем текущий вопрос в контекст пользователя
        # Это может быть реализовано разными способами, например, через состояния FSM или кэш
        first_question[user.id] = first_question.id
        
        # Далее нужен механизм для обработки ответа пользователя и получения следующего вопроса
        # ...
    else:
        await callback_query.message.answer("There are no questions to start with.")

    await callback_query.answer()