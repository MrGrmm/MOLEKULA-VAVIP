from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import json
import sqlite3
import datetime
from models import User, Brief, Question, UserState, Answer


db = sqlite3.connect('db.sqlite3')


async def hi_message(callback_query: types.CallbackQuery):
    # Получаем ID пользователя из запроса
    telegram_user_id = callback_query.from_user.id
    # Проверяем, есть ли пользователь в базе данных
    user = await User.get(telegram_user_id=telegram_user_id)
    if not user:
        await callback_query.answer("Вам необходимо зарегистрироваться.")
        return
    # Проверяем, есть ли у пользователя открытые Brief'ы в базе данных
    brief = await Brief.filter(user=user).first()
    # Если брифа ещё нет, то создаём его
    if not brief:
        brief = await Brief.create(user=user, created_at=datetime.datetime.now())
    # Проверяем текущее состояние пользователя в базе данных
    user_state = await UserState.get_or_none(user=user)
    # Если состояние пользователя существует и есть текущий вопрос
    if user_state and user_state.current_question is not None:
        # Получаем текущий вопрос пользователя
        current_question = await user_state.current_question.first()                          #TODO   Не нужно ли будет использовать словами чтобы дать понять боту именно о каком пользователе идёт речь? 
        # Получаем текущий вопрос пользователя                                                #TODO    чтобы не возникло конфликтов состояний пользователей
        current_question = await Question.get(id=current_question.id)
        # Сохраняем ответ пользователя в переменную
        user_answer = callback_query.text  
        # Пробуем создать запись с ответом пользователя        
        try:
            await Answer.create(user=user, brief=brief, question=current_question, answer=user_answer)                         
        # Проверка на возможные ошибки которые приведут к тому что запись не произойдёт в базе данных
        except Exception as e:
            await callback_query.answer(f"Ошибка: {e}")
        else:
            await callback_query.answer("Ваш ответ успешно сохранен.")
            # Получение ID следующего вопроса из текущего вопроса
            next_question_id = current_question.next_question_id
            if next_question_id is not None:
            # Получение следующего вопроса по ID
                next_question = await Question.get(id=next_question_id)     
                if next_question:
                    # Проверяем, есть ли у следующего вопроса варианты ответа
                    if next_question.answer_options:
                        answer_options = next_question.answer_options
                        # Создаем клавиатуру с кнопками для каждого варианта ответа
                        answer_kb = ReplyKeyboardMarkup(
                                                        resize_keyboard=True,
                                                        one_time_keyboard=True,
                                                        keyboard=[
                                                            [KeyboardButton(text=answer)] for answer in answer_options.keys()
                                                        ]
                                                    )
                        # Обновляем состояние пользователя с id следующего вопроса перед отправкой
                        user_state.current_question = next_question
                        user_state.context_data = {}  # или обновите context_data если это необходимо
                        await user_state.save()
                        # Отправляем следующий вопрос с клавиатурой

                        await callback_query.answer(next_question.question, reply_markup=answer_kb)

                    else:
                        # Отправляем следующий вопрос пользователю
                        await callback_query.answer(next_question.question)
                else:
                    # Следующий вопрос не найден, отправляем сообщение об этом пользователю
                    await callback_query.answer("Следующий вопрос не найден.")
            else:
                # ID следующего вопроса не задан, можно завершить диалог или обработать иначе
                await callback_query.answer("Это был последний вопрос. Спасибо за ваше время!")
    # Если состояние пользователя ещё не существует то:
    else:
        # Извлекаем первый вопрос из базы данных
        first_question = await Question.filter(id=1).first()
        # Если первый вопрос в базе данных существует то задаём его пользователю и создаём новую запись о состоянии пользователя в базе данных
        if first_question is not None:
            await callback_query.answer(first_question.question)
            user_state = await UserState.create(user=user, current_question=first_question, context_data=())

    # Теперь вам нужно добавить логику для обработки ответов пользователя
    # и их сохранения в таблицу Answer, а также логику для получения и отправки
    # следующего вопроса, если это применимо.
    