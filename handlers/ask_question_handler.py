from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import json
import sqlite3
import datetime
from models import User, Brief, Question, UserState, Answer



class QuestionManager:
    class SpecialQuestions:
        def __init__(self, parent):
            self.parent = parent  # Ссылка на экземпляр QuestionManager для доступа к его атрибутам и методам

        async def handle_question_1(self, answer, question, callback_query):
            try:
                # Обновляем имя пользователя в базе данных
                self.parent.user.name = answer
                await self.parent.user.save()
                # Отправляем подтверждение пользователю
                await callback_query.answer("Ваше имя было успешно сохранено.")
            except Exception as e:
                # В случае ошибки, информируем пользователя
                await callback_query.answer(f"Произошла ошибка при сохранении вашего имени: {e}")
                print(f"Error saving user name: {e}")

        async def handle_question_2112(self, answer, question, callback_query):
            selected_options = self.parent.user_state.context_data.get('selected_answers', [])
            if not answer == "ЭТО ВСЁ":
                selected_options.append(answer)
                self.parent.user_state.context_data['selected_answers'] = selected_options
                await self.parent.user_state.save()
                if answer == "ЭЛЕКТРИЧЕСТВО":
                    return await self.parent.handle_choice_answer(answer, question, callback_query)
                # Фильтрация вариантов ответа
                remaining_options = {k: v for k, v in question.answer_options.items() if k not in selected_options or k == "Это всё"}
                
                # Подготовка клавиатуры с новыми вариантами ответа
                keyboard = ReplyKeyboardMarkup(
                    resize_keyboard=True,
                    one_time_keyboard=True,
                    keyboard=[
                        [KeyboardButton(text=option)] for option in remaining_options
                    ]
                )
                # Задаём вопрос заново с новыми вариантами
                return await callback_query.answer(question.question, reply_markup=keyboard)
            
            else:
                # Логика завершения вопроса
                self.parent.user_state.context_data.pop('selected_answers', None)                
                await self.parent.user_state.save()
                await self.parent.handle_choice_answer(answer, question, callback_query)

        async def handle_question_2113(self, answer, question, callback_query):
            next_question_id = question.next_question_id
            next_question = await self.parent.update_user_state_with_next_question(next_question_id)

            selected_options = self.parent.user_state.context_data.get('selected_answers', [])
            remaining_options = {k: v for k, v in next_question.answer_options.items() if k not in selected_options or k == "Это всё"}
            keyboard = ReplyKeyboardMarkup(
                    resize_keyboard=True,
                    one_time_keyboard=True,
                    keyboard=[
                        [KeyboardButton(text=option)] for option in remaining_options
                    ]
                )
                # Задаём вопрос заново с новыми вариантами
            return await callback_query.answer(next_question.question, reply_markup=keyboard)

                # Дополнительные методы для других специальных вопросов

    def __init__(self, user, user_state):
        self.user = user
        self.user_state = user_state
        self.special_questions = self.SpecialQuestions(self)

    async def process_answer(self, answer, callback_query):
        current_question = await self.fetch_current_question()

        if not current_question:
            return "Вопрос не найден."

        # Проверка, является ли вопрос специальным
        if current_question.id in [1, 2112, 2113]:  # ID специальных вопросов
            method = getattr(self.special_questions, f'handle_question_{current_question.id}', None)
            if method:
                if current_question.id in [2112, 2113]:
                    return await method(answer, current_question, callback_query)
                else:
                    await method(answer, current_question, callback_query)

        # Обычная обработка ответов
        answer_type = current_question.answer_type.name
        method_name = f"handle_{answer_type.lower()}_answer"
        handler = getattr(self, method_name, self.handle_unknown_answer)
        return await handler(answer, current_question, callback_query)

    async def fetch_current_question(self):
        try:
            if self.user_state and self.user_state.current_question:
                return await Question.get(id=self.user_state.current_question_id)
        except Exception as e:
            print(f"Error fetching question: {e}")
        return None
    
    async def save_user_answer(self, brief, callback_query):

        current_question = await Question.get_or_none(id=self.user_state.current_question_id)
        if current_question is None:
            return "Вопрос не найден."
        try:
            return await Answer.create(user=self.user, brief=brief, question=current_question, answer=callback_query.text)                 
        # Проверка на возможные ошибки которые приведут к тому что запись не произойдёт в базе данных
        except Exception as e:
            return await callback_query.answer(f"Ошибка: {e}")


    async def update_user_state_with_next_question(self, next_question_id):
        if not next_question_id:
            return "Следующий вопрос не найден."
        next_question = await Question.get_or_none(id=next_question_id)
        if not next_question:
            return "Следующий вопрос не найден."
        
        self.user_state.current_question = next_question
        await self.user_state.save()
        return next_question

    async def answer_keyboard_preparation(self, next_question):
        if not next_question.answer_options:
            return None
        else:
            answer_options = next_question.answer_options
            answer_kb = ReplyKeyboardMarkup(
                resize_keyboard=True,
                one_time_keyboard=True,
                keyboard=[
                    [KeyboardButton(text=answer)] for answer in answer_options.keys()
                ]
            )
            return answer_kb

    async def handle_text_answer(self, answer, current_question, callback_query):
        next_question_id = current_question.next_question_id
        next_question = await self.update_user_state_with_next_question(next_question_id)
        keyboard = await self.answer_keyboard_preparation(next_question)
        if keyboard is not None:
            return await callback_query.answer(next_question.question, reply_markup=keyboard)
        else:
            return await callback_query.answer(next_question.question)

    async def handle_choice_answer(self, answer, question, callback_query):
        next_question_id = question.answer_options.get(answer)
        next_question = await self.update_user_state_with_next_question(next_question_id)
        keyboard = await self.answer_keyboard_preparation(next_question)
        if keyboard is not None:
            return await callback_query.answer(next_question.question, reply_markup=keyboard)
        else:
            return await callback_query.answer(next_question.question)
        

    async def handle_combo_answer(self, answer, question, callback_query):
        if answer in question.answer_options:
            next_question_id = question.answer_options[answer]
        else:
            next_question_id = question.next_question_id
        if next_question_id is not None:
            next_question = await self.update_user_state_with_next_question(next_question_id)
            keyboard = await self.answer_keyboard_preparation(next_question)
        if keyboard is not None:
            return await callback_query.answer(next_question.question, reply_markup=keyboard)
        else:
            return await callback_query.answer(next_question.question)


    async def handle_file_answer(self, answer, question, callback_query):
        await callback_query.answer("Неизвестный тип ответа.")
        return "Неизвестный тип ответа."



    async def handle_unknown_answer(self, answer, question, callback_query):
        await callback_query.answer("Неизвестный тип ответа.")
        return "Неизвестный тип ответа."


    
        



def connect_to_database(db_path='db.sqlite3'):
    try:
        db = sqlite3.connect(db_path)
        print("DB is connected")
        return db
    except Exception as e:
        print(f'ERROR DB connection: {e}')
        return None
    
db = connect_to_database()



async def hi_message(callback_query: types.CallbackQuery):
    try:
        telegram_user_id = callback_query.from_user.id
        user = await User.get_or_none(telegram_user_id=telegram_user_id)
        if not user:
            await callback_query.answer("Вы не зарегистрированы, для регистрации используйте команду /start")
            return
        else:
            brief = await Brief.filter(user=user).first()
        # Если брифа ещё нет, то создаём его
            if not brief:
                brief = await Brief.create(user=user, created_at=datetime.datetime.now())

        user_state = await UserState.get_or_none(user=user)
        if not user_state:
            # Handle new user state scenario.
            first_question = await Question.filter(id=1).first()
            if first_question:
                user_state = await UserState.create(user=user, context_data={}, current_question=first_question)
                await callback_query.answer(first_question.question)
            return

        q_manager = QuestionManager(user, user_state)
        await q_manager.save_user_answer(brief, callback_query)
        await q_manager.process_answer(callback_query.text, callback_query)
    except Exception as e:
        print(f"Error in hi_message: {e}")
        await callback_query.answer("Произошла ошибка, попробуйте позже.")



# async def update_user_name(telegram_user_id, user_answer):
#     try:
#         # Получаем пользователя по ID
#         user = await User.get(telegram_user_id=telegram_user_id)
#         # Обновляем имя пользователя текстом ответа пользователя
#         user.name = user_answer
#         # Сохраняем изменения
#         await user.save()
#         return "Имя пользователя обновлено."
#     except Exception as e:
#         return f"Ошибка обновления имени пользователя: {e}"


# async def handle_question_consultation(callback_query, current_question, user_answer):
#     # Предположим, что функция уже имеет доступ к current_question и user_answer
#     if user_answer == "Нужна консультация":
#         # Отправляем URL для консультации пользователю, так как предполагается, что он существует
#         await callback_query.answer(current_question.consultation_url)


# async def handle_special_question_5(user_state, user_answer):
#     # Сначала проверяем, что в context_data уже есть данные, если нет, создаем новый словарь
#     if not user_state.context_data:
#         user_state.context_data = {}

#     # Обновление context_data в зависимости от ответа пользователя
#     if user_answer == "Нужны все разделы":
#         user_state.context_data.update({"vodosnab": False,
#                                         "otoplen": False,
#                                         "kanaliz": False,
#                                         "uzel": False
#                                         })
#     elif user_answer == "Водоснабжение":
#         user_state.context_data.update({"vodosnab": False})
#     elif user_answer == "Отопление":
#         user_state.context_data.update({"otoplen": False})
#     elif user_answer == "Канализация":
#         user_state.context_data.update({"kanaliz": False})
#     elif user_answer == "Узел ввода":
#         user_state.context_data.update({"uzel": False})


# async def handle_special_question_1002(user_state, user_answer):
#     # Сначала проверяем, что в context_data уже есть данные, если нет, создаем новый словарь
#     if not user_state.context_data:
#         user_state.context_data = {}
#     # Обновление context_data в зависимости от ответа пользователя
#     if user_answer == "Есть и то и то":
#         user_state.context_data.update({"design_project": False, "plumbing_project": False})
#     elif user_answer == "Есть дизайн проект":
#         user_state.context_data.update({"design_project": False})
#     elif user_answer == "Есть проект сантехнических работ":
#         user_state.context_data.update({"plumbing_project": False})
#     # Сохранение обновленного состояния в базу данных
#     await user_state.save()
#     print("Context data updated:", user_state.context_data)


# async def process_unconfigured_nodes_count(user_state, current_question):
#     # Получаем количество не настроенных узлов из context_data
#     unconfigured_nodes_count = user_state.context_data.get("unconfigured_nodes_count", 0)

#     # Уменьшаем количество на 1, если оно больше 0
#     if unconfigured_nodes_count > 0:
#         unconfigured_nodes_count -= 1
#         user_state.context_data["unconfigured_nodes_count"] = unconfigured_nodes_count
#         await user_state.save()  # Предполагаем, что у user_state есть метод save()

#         # Если после уменьшения, количество все еще больше 0, возвращаем 1101
#         if unconfigured_nodes_count > 0:
#             return 1101

#     # В противном случае, возвращаем next_question_id как обычно из текущего вопроса
#     return current_question.next_question_id


# async def handle_special_question_1100(user_state, user_answer):
#     # Сначала проверяем, что в context_data уже есть данные, если нет, создаем новый словарь
#     if not user_state.context_data:
#         user_state.context_data = {}
#     # Обновление context_data в зависимости от ответа пользователя
#     if not user_answer == "Нужна консультация":
#         user_state.context_data.update({"unconfigured_nodes_count": int(user_answer)})
#     # Сохранение обновленного состояния в базу данных
#     await user_state.save()
#     print("Context data updated:", user_state.context_data)


# async def process_unconfigured_bathrooms_in_node_count(user_state, current_question):
#     # Получаем количество не настроенных узлов из context_data
#     unconfigured_bathrooms_in_node_count = user_state.context_data.get("unconfigured_bathrooms_in_node_count", 0)

#     # Уменьшаем количество на 1, если оно больше 0
#     if unconfigured_bathrooms_in_node_count > 0:
#         unconfigured_bathrooms_in_node_count -= 1
#         user_state.context_data["unconfigured_bathrooms_in_node_count"] = unconfigured_bathrooms_in_node_count
#         await user_state.save()  # Предполагаем, что у user_state есть метод save()

#         # Если после уменьшения, количество все еще больше 0, возвращаем 1101
#         if unconfigured_bathrooms_in_node_count > 0:
#             return 1109

#     # В противном случае, возвращаем next_question_id как обычно из текущего вопроса
#     return current_question.next_question_id


# async def handle_special_question_1101(user_state, user_answer):
#     # Сначала проверяем, что в context_data уже есть данные, если нет, создаем новый словарь
#     if not user_state.context_data:
#         user_state.context_data = {}
#     # Обновление context_data в зависимости от ответа пользователя
#     if not user_answer == "Нужна консультация":
#         user_state.context_data.update({"unconfigured_bathrooms_in_node_count": int(user_answer)})
#     # Сохранение обновленного состояния в базу данных
#     await user_state.save()
#     print("Context data updated:", user_state.context_data)



# async def handle_special_question_1127(user_state, user_answer):
#     # Сначала проверяем, что в context_data уже есть данные, если нет, создаем новый словарь
#     if not user_state.context_data:
#         user_state.context_data = {}

#     # Обновление context_data в зависимости от ответа пользователя
#     if user_answer == "Проточный":
#         user_state.context_data.update({"flow_heater": True})
#     elif user_answer == "Накопительный":
#         user_state.context_data.update({"storage_heater": True})
#     # Сохранение обновленного состояния в базу данных
#     await user_state.save()
#     print("Context data updated:", user_state.context_data)



# async def handle_special_question_2100(user_state, user_answer):
#     # Сначала проверяем, что в context_data уже есть данные, если нет, создаем новый словарь
#     if not user_state.context_data:
#         user_state.context_data = {}
#     # Обновление context_data в зависимости от ответа пользователя
#     if user_answer == "ДА" or user_answer == "ПЛАНИРУЕТСЯ":
#         user_state.context_data.update({"architectural_project": False})
        
#     # Сохранение обновленного состояния в базу данных
#     await user_state.save()
#     print("Context data updated:", user_state.context_data)


# async def handle_special_question_2102(user_state, user_answer):
#     # Сначала проверяем, что в context_data уже есть данные, если нет, создаем новый словарь
#     if not user_state.context_data:
#         user_state.context_data = {}
#     # Обновление context_data в зависимости от ответа пользователя
#     if user_answer == "ДА" or user_answer == "ПЛАНИРУЕТСЯ":
#         user_state.context_data.update({"design_project": False})
        
#     # Сохранение обновленного состояния в базу данных
#     await user_state.save()
#     print("Context data updated:", user_state.context_data)


# async def handle_special_question_2104(user_state, user_answer):
#     # Сначала проверяем, что в context_data уже есть данные, если нет, создаем новый словарь
#     if not user_state.context_data:
#         user_state.context_data = {}
#     # Обновление context_data в зависимости от ответа пользователя
#     user_state.context_data.update({"floor_count": int(user_answer)})
#     # Сохранение обновленного состояния в базу данных
#     await user_state.save()
#     print("Context data updated:", user_state.context_data)




# async def set_next_question_and_save_upd(user_state, next_question_id, callback_query):
#     next_question = await Question.get_or_none(id=next_question_id)

#     if next_question is None:
#         # Следующий вопрос не найден
#         await callback_query.answer("Следующий вопрос не найден.")
#         return

#     # Обновляем текущий вопрос пользователя в состоянии
#     user_state.current_question = next_question
#     await user_state.save()
    
#     answer_type = next_question.answer_type

#     if answer_type.name == "TEXT":
#         await callback_query.answer(next_question.question)

#     elif answer_type.name == "CHOICE":
#         # Обработка ответа типа "выбор"
#         answer_options = next_question.answer_options
#         answer_kb = ReplyKeyboardMarkup(
#             resize_keyboard=True,
#             one_time_keyboard=True,
#             keyboard=[
#                 [KeyboardButton(text=answer)] for answer in answer_options.keys()
#             ]
#         )
#         # Отправляем следующий вопрос с клавиатурой
#         await callback_query.answer(next_question.question, reply_markup=answer_kb)

#     elif answer_type.name == "FILE":
#         # Обработка ответа типа "файл"
#         ...

#     elif answer_type.name == "COMBO":
#          # Получение данных
#         answer_options = next_question.answer_options
        

#         if answer_options is not None:
#             answer_options = next_question.answer_options
#             answer_kb = ReplyKeyboardMarkup(
#                 resize_keyboard=True,
#                 one_time_keyboard=True,
#                 keyboard=[
#                     [KeyboardButton(text=answer)] for answer in answer_options.keys()
#                 ]
#             )
#         # Отправляем следующий вопрос с клавиатурой
#             await callback_query.answer(next_question.question, reply_markup=answer_kb)
#         else:
#             await callback_query.answer(next_question.question)

#     else:
#         await callback_query.answer(f"Неизвестный тип ответа: {answer_type}")
#         return




# async def handle_request_projects(callback_query, user_state):
#     """
#     Функция для проверки и обработки проектов.

#     Args:
#         context_data (dict): Словарь context_data пользователя.

#     Returns:
#         None: 
#     """

#     project_keys = [key for key in user_state.context_data if "project" in key]
#     for project_key in project_keys:
#         if user_state.context_data[project_key] is False:
#             # Запрос загрузки файла проекта
#             await callback_query.answer("Пожалуйста, загрузите файл проекта.")
#             # ... (обработка полученного файла проекта)
#             # ... (обновление context_data[project_key] = True)

#     # Проверка, все ли значения True
#     all_projects_true = all(user_state.context_data[project_key] for project_key in project_keys)

#     if all_projects_true:
#         # Переход к следующему вопросу
#         next_question_id = current_question.next_question_id
#         if next_question_id is not None:
#             await set_next_question_and_save_upd(user_state, next_question_id, callback_query)



# async def hi_message(callback_query: types.CallbackQuery):
#     # Получаем ID пользователя из запроса
#     telegram_user_id = callback_query.from_user.id
#     # Проверяем, есть ли пользователь в базе данных
#     # user = await get_user_info(telegram_user_id)
#     user = await User.get_or_none(telegram_user_id=telegram_user_id)
#     if user is not None:
#         # Проверяем, есть ли у пользователя открытые Brief'ы в базе данных
#         brief = await Brief.filter(user=user).first()
#         # Если брифа ещё нет, то создаём его
#         if not brief:
#             brief = await Brief.create(user=user, created_at=datetime.datetime.now())
#         # Проверяем текущее состояние пользователя в базе данных
#         user_state = await UserState.get_or_none(user=user)
#         # Если состояние пользователя существует и есть текущий вопрос
#         if user_state and user_state.current_question is not None:
#             # Получаем текущий вопрос пользователя
#             current_question = await user_state.current_question.first()
#             # Получаем текущий вопрос пользователя                                                
#             current_question = await Question.get(id=current_question.id)
#             # Сохраняем ответ пользователя в переменную
#             user_answer = callback_query.text  
#             if current_question.id == 1:  # Если это специфический вопрос, где нужно обновить имя
#                 result_message = await update_user_name(callback_query.from_user.id, user_answer)
#                 print(result_message)  # Выведет сообщение о статусе обновления

#             # Пробуем создать запись с ответом пользователя        
#             try:
#                 await Answer.create(user=user, brief=brief, question=current_question, answer=user_answer)                 
#             # Проверка на возможные ошибки которые приведут к тому что запись не произойдёт в базе данных
#             except Exception as e:
#                 await callback_query.answer(f"Ошибка: {e}")
#             else:
#                 print(f"Ответ успешно сохранен.")
#                 # Получение ID следующего вопроса из текущего вопроса

#                 if user_answer == "Нужна консультация":
#                     await handle_question_consultation(callback_query, current_question, user_answer)
#                 if current_question.id == 5:
#                     await handle_special_question_5(user_state, user_answer)
#                 if current_question.id == 1002:
#                     await handle_special_question_1002(user_state, user_answer)
#                 if current_question.id == 1100:
#                     await handle_special_question_1100(user_state, user_answer)
#                 if current_question.id == 1101:
#                     await handle_special_question_1101(user_state, user_answer)
#                 if current_question.id == 1116:
#                     next_question_id = await process_unconfigured_bathrooms_in_node_count(user_state, current_question)
#                     if next_question_id is not None:
#                     # Получение следующего вопроса по ID
#                         await set_next_question_and_save_upd(user_state, next_question_id, callback_query)
#                 if current_question.id == 1127:
#                     await handle_special_question_1127(user_state, user_answer)
#                 if current_question.id == 2100:
#                     await handle_special_question_2100(user_state, user_answer)
#                 if current_question.id == 2102:
#                     await handle_special_question_2102(user_state, user_answer)
#                 if current_question.id == 2104:
#                     await handle_special_question_2104(user_state, user_answer)
#                 # if current_question.id == 2112:
#                 #     next_question_id = handle_question_2121(user_state)
#                 if current_question.id == 1165:
#                     next_question_id = await process_unconfigured_nodes_count(user_state, current_question)
#                     if next_question_id is not None:
#                     # Получение следующего вопроса по ID
#                         await set_next_question_and_save_upd(user_state, next_question_id, callback_query)

#                 else:

#                     answer_type = current_question.answer_type
#                     if answer_type.name == "TEXT":
#                         next_question_id = current_question.next_question_id
#                         if next_question_id is not None:
#                             await set_next_question_and_save_upd(user_state, next_question_id, callback_query)
#                     elif answer_type.name == "CHOICE":
#                         # Обработка ответа типа "выбор"
#                         next_question_id = current_question.answer_options[user_answer]
#                         if next_question_id is not None:
#                             await set_next_question_and_save_upd(user_state, next_question_id, callback_query)

#                     elif answer_type.name == "FILE":
#                         # Обработка ответа типа "файл"
#                         ...

#                     elif answer_type.name == "COMBO":
#                         if user_answer in current_question.answer_options:
#                             next_question_id = current_question.answer_options[user_answer]
#                         else:
#                             next_question_id = current_question.next_question_id
#                         if next_question_id is not None:
#                             await set_next_question_and_save_upd(user_state, next_question_id, callback_query)



#                     else:
#                         await callback_query.answer(f"Неизвестный тип ответа: {answer_type}")
                       
                                         

#             # Если состояние пользователя ещё не существует то:
#         else:
#             # Извлекаем первый вопрос из базы данных
#             first_question = await Question.filter(id=1).first()
#             # Если первый вопрос в базе данных существует то задаём его пользователю и создаём новую запись о состоянии пользователя в базе данных
#             if first_question is not None:
#                 print('CheCK6')
#                 await callback_query.answer(first_question.question)
#                 user_state = await UserState.create(user=user, current_question=first_question, context_data=())

#     else:
#         callback_query.answer("Вы не зарегистрированы, чтобы зарегистрироваться воспользуйтесь командой /start")
