from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import json
import sqlite3
import datetime
from models import User, Brief, Question, UserState, Answer



def connect_to_database(db_path='db.sqlite3'):
    try:
        db = sqlite3.connect(db_path)
        print("DB is connected")
        return db
    except Exception as e:
        print(f'ERROR DB connection: {e}')
        return None
    
db = connect_to_database()



async def update_user_name(telegram_user_id, user_answer):
    try:
        # Получаем пользователя по ID
        user = await User.get(telegram_user_id=telegram_user_id)
        # Обновляем имя пользователя текстом ответа пользователя
        user.name = user_answer
        # Сохраняем изменения
        await user.save()
        return "Имя пользователя обновлено."
    except Exception as e:
        return f"Ошибка обновления имени пользователя: {e}"


async def handle_question_consultation(callback_query, current_question, user_answer):
    # Предположим, что функция уже имеет доступ к current_question и user_answer
    if user_answer == "Нужна консультация":
        # Отправляем URL для консультации пользователю, так как предполагается, что он существует
        await callback_query.answer(current_question.consultation_url)


async def handle_special_question_5(user_state, user_answer):
    # Сначала проверяем, что в context_data уже есть данные, если нет, создаем новый словарь
    if not user_state.context_data:
        user_state.context_data = {}

    # Обновление context_data в зависимости от ответа пользователя
    if user_answer == "Нужны все разделы":
        user_state.context_data.update({"vodosnab": False,
                                        "otoplen": False,
                                        "kanaliz": False,
                                        "uzel": False
                                        })
    elif user_answer == "Водоснабжение":
        user_state.context_data.update({"vodosnab": False})
    elif user_answer == "Отопление":
        user_state.context_data.update({"otoplen": False})
    elif user_answer == "Канализация":
        user_state.context_data.update({"kanaliz": False})
    elif user_answer == "Узел ввода":
        user_state.context_data.update({"uzel": False})


async def handle_special_question_1002(user_state, user_answer):
    # Сначала проверяем, что в context_data уже есть данные, если нет, создаем новый словарь
    if not user_state.context_data:
        user_state.context_data = {}
    # Обновление context_data в зависимости от ответа пользователя
    if user_answer == "Есть и то и то":
        user_state.context_data.update({"design_project": False, "plumbing_project": False})
    elif user_answer == "Есть дизайн проект":
        user_state.context_data.update({"design_project": False})
    elif user_answer == "Есть проект сантехнических работ":
        user_state.context_data.update({"plumbing_project": False})
    # Сохранение обновленного состояния в базу данных
    await user_state.save()
    print("Context data updated:", user_state.context_data)


async def process_unconfigured_nodes_count(user_state, current_question):
    # Получаем количество не настроенных узлов из context_data
    unconfigured_nodes_count = user_state.context_data.get("unconfigured_nodes_count", 0)

    # Уменьшаем количество на 1, если оно больше 0
    if unconfigured_nodes_count > 0:
        unconfigured_nodes_count -= 1
        user_state.context_data["unconfigured_nodes_count"] = unconfigured_nodes_count
        await user_state.save()  # Предполагаем, что у user_state есть метод save()

        # Если после уменьшения, количество все еще больше 0, возвращаем 1101
        if unconfigured_nodes_count > 0:
            return 1101

    # В противном случае, возвращаем next_question_id как обычно из текущего вопроса
    return current_question.next_question_id


async def handle_special_question_1100(user_state, user_answer):
    # Сначала проверяем, что в context_data уже есть данные, если нет, создаем новый словарь
    if not user_state.context_data:
        user_state.context_data = {}
    # Обновление context_data в зависимости от ответа пользователя
    if not user_answer == "Нужна консультация":
        user_state.context_data.update({"unconfigured_node_count": int(user_answer)})
    # Сохранение обновленного состояния в базу данных
    await user_state.save()
    print("Context data updated:", user_state.context_data)


async def process_unconfigured_bathroom_in_node_count(user_state, current_question):
    # Получаем количество не настроенных узлов из context_data
    unconfigured_bathroom_in_node_count = user_state.context_data.get("unconfigured_bathroom_in_node_count", 0)

    # Уменьшаем количество на 1, если оно больше 0
    if unconfigured_bathroom_in_node_count > 0:
        unconfigured_bathroom_in_node_count -= 1
        user_state.context_data["unconfigured_bathroom_in_node_count"] = unconfigured_bathroom_in_node_count
        await user_state.save()  # Предполагаем, что у user_state есть метод save()

        # Если после уменьшения, количество все еще больше 0, возвращаем 1101
        if unconfigured_bathroom_in_node_count > 0:
            return 1109

    # В противном случае, возвращаем next_question_id как обычно из текущего вопроса
    return current_question.next_question_id


async def handle_special_question_1101(user_state, user_answer):
    # Сначала проверяем, что в context_data уже есть данные, если нет, создаем новый словарь
    if not user_state.context_data:
        user_state.context_data = {}
    # Обновление context_data в зависимости от ответа пользователя
        user_state.context_data.update({"unconfigured_bathroom_in_node_count": int(user_answer)})
    # Сохранение обновленного состояния в базу данных
    await user_state.save()
    print("Context data updated:", user_state.context_data)



async def handle_special_question_1127(user_state, user_answer):
    # Сначала проверяем, что в context_data уже есть данные, если нет, создаем новый словарь
    if not user_state.context_data:
        user_state.context_data = {}

    # Обновление context_data в зависимости от ответа пользователя
    if user_answer == "Проточный":
        user_state.context_data.update({"flow_heater": True})
    elif user_answer == "Накопительный":
        user_state.context_data.update({"storage_heater": True})
    # Сохранение обновленного состояния в базу данных
    await user_state.save()
    print("Context data updated:", user_state.context_data)



async def set_next_question_and_save(user_state, next_question_id, callback_query):
    next_question = await Question.get_or_none(id=next_question_id)

    if next_question is None:
        # Следующий вопрос не найден
        await callback_query.answer("Следующий вопрос не найден.")
        return

    # Обновляем текущий вопрос пользователя в состоянии
    user_state.current_question = next_question
    await user_state.save()

    # Проверяем, есть ли у следующего вопроса варианты ответа
    if next_question.answer_options:
        # Создаем клавиатуру с кнопками для каждого варианта ответа
        answer_options = next_question.answer_options
        answer_kb = ReplyKeyboardMarkup(
            resize_keyboard=True,
            one_time_keyboard=True,
            keyboard=[
                [KeyboardButton(text=answer)] for answer in answer_options.keys()
            ]
        )
        # Отправляем следующий вопрос с клавиатурой
        await callback_query.message.answer(next_question.question, reply_markup=answer_kb)
    else:
        # Отправляем следующий вопрос без клавиатуры
        await callback_query.message.answer(next_question.question)












async def hi_message(callback_query: types.CallbackQuery):
    # Получаем ID пользователя из запроса
    telegram_user_id = callback_query.from_user.id
    # Проверяем, есть ли пользователь в базе данных
    # user = await get_user_info(telegram_user_id)
    user = await User.get_or_none(telegram_user_id=telegram_user_id)
    if user is not None:
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
            current_question = await user_state.current_question.first()                          
            # Получаем текущий вопрос пользователя                                                
            current_question = await Question.get(id=current_question.id)
            # Сохраняем ответ пользователя в переменную
            user_answer = callback_query.text  
            if current_question.id == 1:  # Если это специфический вопрос, где нужно обновить имя
                result_message = await update_user_name(callback_query.from_user.id, user_answer)
                print(result_message)  # Выведет сообщение о статусе обновления

            # Пробуем создать запись с ответом пользователя        
            try:
                await Answer.create(user=user, brief=brief, question=current_question, answer=user_answer)                 
            # Проверка на возможные ошибки которые приведут к тому что запись не произойдёт в базе данных
            except Exception as e:
                await callback_query.answer(f"Ошибка: {e}")
            else:
                print(f"Ответ успешно сохранен.")
                # Получение ID следующего вопроса из текущего вопроса
                print(current_question)
                print(current_question.answer_options)
                if user_answer == "Нужна консультация":
                    await handle_question_consultation(callback_query, current_question, user_answer)
                if current_question.id == 5:
                    await handle_special_question_5(user_state, user_answer)
                if current_question.id == 1002:
                    await handle_special_question_1002(user_state, user_answer)
                if current_question.id == 1100:
                    await handle_special_question_1100(user_state, user_answer)
                if current_question.id == 1127:
                    await handle_special_question_1127(user_state, user_answer)
                if current_question.id == 1165:
                    next_question_id = await process_unconfigured_nodes_count(user_state, current_question)
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
                                await user_state.save()
                                # Отправляем следующий вопрос с клавиатурой
                                print('CheCK1')
                                await callback_query.answer(next_question.question, reply_markup=answer_kb)

                            else:
                                user_state.current_question = next_question
                                await user_state.save()
                                # Отправляем следующий вопрос пользователю
                                print('CheCK2')
                                await callback_query.answer(next_question.question)
                        else:
                            # Следующий вопрос не найден, отправляем сообщение об этом пользователю
                            print('CheCK3')
                            await callback_query.answer("Следующий вопрос не найден.")
                    else:
                        # ID следующего вопроса не задан, можно завершить диалог или обработать иначе
                        await callback_query.answer("Это был последний вопрос. Спасибо за ваше время!")
                else:
                    if current_question.answer_options is not None:
                        next_question_id = current_question.answer_options[user_answer]
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
                                    await user_state.save()
                                    # Отправляем следующий вопрос с клавиатурой
                                    print('CheCK1')
                                    await callback_query.answer(next_question.question, reply_markup=answer_kb)

                                else:
                                    user_state.current_question = next_question
                                    await user_state.save()
                                    # Отправляем следующий вопрос пользователю
                                    print('CheCK2')
                                    await callback_query.answer(next_question.question)
                            else:
                                # Следующий вопрос не найден, отправляем сообщение об этом пользователю
                                print('CheCK3')
                                await callback_query.answer("Следующий вопрос не найден.")
                        else:
                            # ID следующего вопроса не задан, можно завершить диалог или обработать иначе
                            await callback_query.answer("Это был последний вопрос. Спасибо за ваше время!")
                    else:    
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
                                    await user_state.save()
                                    # Отправляем следующий вопрос с клавиатурой
                                    print('CheCK4')
                                    await callback_query.answer(next_question.question, reply_markup=answer_kb)

                                else:
                                    # Отправляем следующий вопрос пользователю
                                    user_state.current_question = next_question
                                    await user_state.save()
                                    print('CheCK5')
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
                print('CheCK6')
                await callback_query.answer(first_question.question)
                user_state = await UserState.create(user=user, current_question=first_question, context_data=())

    else:
        callback_query.answer("Вы не зарегистрированы, чтобы зарегистрироваться воспользуйтесь командой /start")
