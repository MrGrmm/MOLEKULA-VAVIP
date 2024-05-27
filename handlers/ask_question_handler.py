from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile

import sqlite3
import datetime
from models import User, Brief, Question, UserState, Answer



class QuestionManager:
    class SpecialQuestions:
        def __init__(self, parent):
            self.parent = parent  # Ссылка на экземпляр QuestionManager для доступа к его атрибутам и методам



        async def handle_skip_question(self, message):
            if not self.parent.user_state.context_data:
                self.parent.user_state.context_data = {}
            # Обновление context_data в зависимости от ответа пользователя
            self.parent.user_state.context_data.update({self.parent.user_state.current_question_id: False})

        async def handle_question_consultation(self, message, current_question):
            if current_question.image_url:
                await message.answer_photo(photo=FSInputFile("img/shema_razvodki_radiatora.jpg"))
        # Предположим, что функция уже имеет доступ к current_question и user_answer
            if message.text == "Нужна консультация":
            # Отправляем URL для консультации пользователю, так как предполагается, что он существует            
                await message.answer(current_question.consultation_url)

                

        async def handle_question_1(self, message):
            try:
                # Обновляем имя пользователя в базе данных
                self.parent.user.name = message.text
                await self.parent.user.save()
                # Отправляем подтверждение пользователю
                # await message.answer("Ваше имя было успешно сохранено.")
            except Exception as e:
                # В случае ошибки, информируем пользователя
                await message.answer(f"Произошла ошибка при сохранении вашего имени: {e}")
                print(f"Error saving user name: {e}")

        async def handle_question_5(self, message):
            if not self.parent.user_state.context_data:
                self.parent.user_state.context_data = {}
            if message.text == "ДА":
                self.parent.user_state.context_data.update({"project_needed": ["Узел ввода", "Канализация", "Отопление", "Водоснабжение"]})

        async def handle_question_6(self, message):
            if not self.parent.user_state.context_data:
                self.parent.user_state.context_data = {}
            if message.text == "ДА":
                project_needed = self.parent.user_state.context_data.get("project_needed", [])
                if "Узел ввода" not in project_needed:
                    project_needed.append("Узел ввода")
                self.parent.user_state.context_data.update({"project_needed": project_needed})

        async def handle_question_7(self, message):
            if not self.parent.user_state.context_data:
                self.parent.user_state.context_data = {}
            if message.text == "ДА":
                project_needed = self.parent.user_state.context_data.get("project_needed", [])
                if "Канализация" not in project_needed:
                    project_needed.append("Канализация")
                self.parent.user_state.context_data.update({"project_needed": project_needed})

        async def handle_question_8(self, message):
            if not self.parent.user_state.context_data:
                self.parent.user_state.context_data = {}
            if message.text == "ДА":
                project_needed = self.parent.user_state.context_data.get("project_needed", [])
                if "Отопление" not in project_needed:
                    project_needed.append("Отопление")
                self.parent.user_state.context_data.update({"project_needed": project_needed})

        async def handle_question_9(self, message):
            if not self.parent.user_state.context_data:
                self.parent.user_state.context_data = {}
            if message.text == "ДА":
                project_needed = self.parent.user_state.context_data.get("project_needed", [])
                if "Водоснабжение" not in project_needed:
                    project_needed.append("Водоснабжение")
                self.parent.user_state.context_data.update({"project_needed": project_needed})

        async def handle_question_50_branch(self, question, message):
            selected_options = self.parent.user_state.context_data.get('project_needed', [])

            # Создание клавиатуры с кнопками

            keyboard = ReplyKeyboardMarkup(
                    resize_keyboard=True,
                    one_time_keyboard=True,
                    keyboard=[
                        [KeyboardButton(text=option)] for option in selected_options
                    ]
                )


            # Отправка сообщения с клавиатурой
            return keyboard
                    

        async def handle_question_1100(self, message):
            # Сначала проверяем, что в context_data уже есть данные, если нет, создаем новый словарь
            if not self.parent.user_state.context_data:
                self.parent.user_state.context_data = {}
            # Обновление context_data в зависимости от ответа пользователя
            if not message.text == "Нужна консультация":
                self.parent.user_state.context_data.update({"unconfigured_node_count": int(message.text)})
            # Сохранение обновленного состояния в базу данных
            await self.parent.user_state.save()
            print("Context data updated:", self.parent.user_state.context_data)

        async def handle_question_1105(self, message):
            node_count =  self.parent.user_state.context_data.unconfigured_node_count
            print(node_count)
            pass


        async def handle_question_1127(self, message):
            if not self.parent.user_state.context_data:
                self.parent.user_state.context_data = {}
            if message.text == "Проточный":
                self.parent.user_state.context_data.update({"waterhater_branch": "Проточный"})
            elif message.text == "Накопительный":
                self.parent.user_state.context_data.update({"waterhater_branch": "Накопительный"})

        

        async def handle_question_1132(self, question, message):
            waterhater_branch = self.parent.user_state.context_data.get('waterhater_branch')
            if waterhater_branch == "Проточный":
                next_question_id = self.parent.user_state.current_question_id = 1132
                next_question = await self.parent.update_user_state_with_next_question(next_question_id)
                keyboard = await self.parent.answer_keyboard_preparation(next_question)
                if next_question.image_url != "":
                        await message.answer_photo(photo=FSInputFile(path=f"{next_question.image_url}"))
                if keyboard is not None:
                    return await message.answer(next_question.question, reply_markup=keyboard)
                else:
                    return await message.answer(next_question.question)
            elif waterhater_branch == "Накопительный":
                next_question_id = self.parent.user_state.current_question_id = 1138
                next_question = await self.parent.update_user_state_with_next_question(next_question_id)
                keyboard = await self.parent.answer_keyboard_preparation(next_question)
                if next_question.image_url != "":
                        await message.answer_photo(photo=FSInputFile(path=f"{next_question.image_url}"))
                if keyboard is not None:
                    return await message.answer(next_question.question, reply_markup=keyboard)
                else:
                    return await message.answer(next_question.question)

        async def handle_question_1401(self, message):
            # Сначала проверяем, что в context_data уже есть данные, если нет, создаем новый словарь
            if not self.parent.user_state.context_data:
                self.parent.user_state.context_data = {}
            # Обновление context_data в зависимости от ответа пользователя
            if not message.text == "Нужна консультация":
                self.parent.user_state.context_data.update({"unconfigured_node_count": int(message.text)})
            # Сохранение обновленного состояния в базу данных
            await self.parent.user_state.save()
            print("Context data updated:", self.parent.user_state.context_data)

        async def handle_question_1429(self, message):
            if not self.parent.user_state.context_data:
                self.parent.user_state.context_data = {}
            if message.text == "Проточный":
                self.parent.user_state.context_data.update({"waterhater_branch": "Проточный"})
            elif message.text == "Накопительбный":
                self.parent.user_state.context_data.update({"waterhater_branch": "Накопительбный"})
            elif message.text == "У меня газовая колонка":
                self.parent.user_state.context_data.update({"waterhater_branch": "У меня газовая колонка"})
        

        async def handle_question_1434(self, question, message):
            waterhater_branch = self.parent.user_state.context_data.get('waterhater_branch')
            if waterhater_branch == "Проточный":
                next_question_id = self.parent.user_state.current_question_id = 1434
                next_question = await self.parent.update_user_state_with_next_question(next_question_id)
                keyboard = await self.parent.answer_keyboard_preparation(next_question)
                if next_question.image_url != "":
                        await message.answer_photo(photo=FSInputFile(path=f"{next_question.image_url}"))
                if keyboard is not None:
                    return await message.answer(next_question.question, reply_markup=keyboard)
                else:
                    return await message.answer(next_question.question)
            elif waterhater_branch == "Накопительный":
                next_question_id = self.parent.user_state.current_question_id = 1440
                next_question = await self.parent.update_user_state_with_next_question(next_question_id)
                keyboard = await self.parent.answer_keyboard_preparation(next_question)
                if next_question.image_url != "":
                        await message.answer_photo(photo=FSInputFile(path=f"{next_question.image_url}"))
                if keyboard is not None:
                    return await message.answer(next_question.question, reply_markup=keyboard)
                else:
                    return await message.answer(next_question.question)
            elif waterhater_branch == "У меня газовая колонка":
                next_question_id = self.parent.user_state.current_question_id = 1444
                next_question = await self.parent.update_user_state_with_next_question(next_question_id)
                keyboard = await self.parent.answer_keyboard_preparation(next_question)
                if next_question.image_url != "":
                        await message.answer_photo(photo=FSInputFile(path=f"{next_question.image_url}"))
                if keyboard is not None:
                    return await message.answer(next_question.question, reply_markup=keyboard)
                else:
                    return await message.answer(next_question.question)


        async def handle_special_question_2100(user_state, user_answer):
            # Сначала проверяем, что в context_data уже есть данные, если нет, создаем новый словарь
            if not user_state.context_data:
                user_state.context_data = {}
            # Обновление context_data в зависимости от ответа пользователя
            if user_answer == "ДА" or user_answer == "ПЛАНИРУЕТСЯ":
                user_state.context_data.update({"architectural_project": False})
                
            # Сохранение обновленного состояния в базу данных
            await user_state.save()
            print("Context data updated:", user_state.context_data)


        async def handle_special_question_2102(user_state, user_answer):
            # Сначала проверяем, что в context_data уже есть данные, если нет, создаем новый словарь
            if not user_state.context_data:
                user_state.context_data = {}
            # Обновление context_data в зависимости от ответа пользователя
            if user_answer == "ДА" or user_answer == "ПЛАНИРУЕТСЯ":
                user_state.context_data.update({"design_project": False})
                
            # Сохранение обновленного состояния в базу данных
            await user_state.save()
            print("Context data updated:", user_state.context_data)

        async def handle_question_2104(self, message):
            if not self.parent.user_state.context_data:
                self.parent.user_state.context_data = {}
            # Обновление context_data в зависимости от ответа пользователя
            self.parent.user_state.context_data.update({"house_floor_count": int(message.text)})
            # Сохранение обновленного состояния в базу данных
            await self.parent.user_state.save()
            print("Context data updated:", self.parent.user_state.context_data)



        async def handle_question_2112(self, question, message):
            selected_options = self.parent.user_state.context_data.get('selected_answers', [])
            if not message.text == "ЭТО ВСЁ":
                selected_options.append(message.text)
                self.parent.user_state.context_data['selected_answers'] = selected_options
                await self.parent.user_state.save()
                if message.text == "ЭЛЕКТРИЧЕСТВО":
                    return await self.parent.handle_choice_answer(question, message)
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
                return await message.answer(question.question, reply_markup=keyboard)
            
            else:
                # Логика завершения вопроса
                await self.parent.handle_choice_answer(question, message)

        async def handle_question_2113(self, question, message):
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
            return await message.answer(next_question.question, reply_markup=keyboard)

                # Дополнительные методы для других специальных вопросов

        async def handle_question_2121(self, question, message):
    # Получаем текущее количество повторений из context_data
            repeats_remaining = self.parent.user_state.context_data.get('house_floor_count', 1)

            if repeats_remaining > 1:
                # Уменьшаем количество оставшихся повторений
                self.parent.user_state.context_data['house_floor_count'] = repeats_remaining - 1
                await self.parent.user_state.save()

                # Подготовка клавиатуры, если необходимо
                keyboard = await self.parent.answer_keyboard_preparation(question)

                # Повторяем вопрос
                await message.answer(question.question, reply_markup=keyboard)
            else:
                # Переходим к следующему вопросу или завершаем, если повторения закончились
                self.parent.user_state.context_data.pop('house_floor_count', None)                
                await self.parent.user_state.save()
                await self.parent.handle_combo_answer(question, message)
                
        async def handle_question_2127(self, question, message):
            selected_options = self.parent.user_state.context_data.get('selected_answers', [])
            if not message.text == "ЭТО ВСЁ, ПРОДОЛЖИТЬ!":
                selected_options.append(message.text)
                self.parent.user_state.context_data['selected_answers'] = selected_options
                await self.parent.user_state.save()
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
                return await message.answer(question.question, reply_markup=keyboard)
            
            else:
                # Логика завершения вопроса
                self.parent.user_state.context_data.pop('selected_answers', None)                
                await self.parent.user_state.save()
                await self.parent.handle_choice_answer(question, message)
        

    def __init__(self, user, user_state):
        self.user = user
        self.user_state = user_state
        self.special_questions = self.SpecialQuestions(self)


    async def process_answer(self, brief, message):

        await self.save_user_answer(brief, message)

        current_question = await self.fetch_current_question()

        if not current_question:
            return "Вопрос не найден."
        if message.text == "Нужна консультация":
            return await self.special_questions.handle_question_consultation(message, current_question)
        elif message.text == "ПРОПУСТИТЬ":
            await self.special_questions.handle_skip_question(message)
        # Проверка, является ли вопрос специальным
        if current_question.id in [1, 5, 6, 7, 8, 9, 1100, 1105, 1127, 1429, 2100, 2102, 2104, 2112, 2113, 2121, 2127] :  # ID специальных вопросов
            method = getattr(self.special_questions, f'handle_question_{current_question.id}', None)
            if method:
                if current_question.id in [2112, 2113, 2121, 2127]:
                    return await method(current_question, message)
                else:
                    await method(message)

        # Обычная обработка ответов
        
        answer_type = current_question.answer_type.name
        method_name = f"handle_{answer_type.lower()}_answer"
        handler = getattr(self, method_name, self.handle_unknown_answer)
        return await handler(current_question, message)

    async def fetch_current_question(self):
        try:
            if self.user_state and self.user_state.current_question:
                return await Question.get(id=self.user_state.current_question_id)
        except Exception as e:
            print(f"Error fetching question: {e}")
        return None
    
    async def save_user_answer(self, brief, message):
        current_question = await Question.get_or_none(id=self.user_state.current_question_id)

        if current_question is None:
            return "Вопрос не найден."
        
        if message.text is None:
            return await Answer.create(user=self.user, brief=brief, question=current_question, answer='file')                 

        try:
            return await Answer.create(user=self.user, brief=brief, question=current_question, answer=message.text)                 
        # Проверка на возможные ошибки которые приведут к тому что запись не произойдёт в базе данных
        except Exception as e:
            return await message.answer(f"Ошибка: {e}")


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
        if next_question.id == 50:
            return await self.special_questions.handle_question_50_branch(next_question, self.user_state)
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

    async def handle_text_answer(self, current_question, message):
        next_question_id = current_question.next_question_id
        next_question = await self.update_user_state_with_next_question(next_question_id)
        keyboard = await self.answer_keyboard_preparation(next_question)
        if next_question.image_url:
                await message.answer_photo(photo=FSInputFile(path=f"{next_question.image_url}"))
        if keyboard is not None:
            return await message.answer(next_question.question, reply_markup=keyboard)
        else:
            return await message.answer(next_question.question)

    async def handle_choice_answer(self, question, message):
        next_question_id = question.answer_options[message.text]
        if next_question_id == 1132:
            return await self.special_questions.handle_question_1132(question, message)
        next_question = await self.update_user_state_with_next_question(next_question_id)
        keyboard = await self.answer_keyboard_preparation(next_question)
        if next_question.image_url != "":
                await message.answer_photo(photo=FSInputFile(path=f"{next_question.image_url}"))
        if keyboard is not None:
            return await message.answer(next_question.question, reply_markup=keyboard)
        else:
            return await message.answer(next_question.question)
        

    async def handle_combo_answer(self, question, message: types.Message):
        
        if message.text is not None:
            if message.text in question.answer_options:
                next_question_id = question.answer_options[message.text]
            else:
                next_question_id = question.next_question_id
            if next_question_id is not None:
                if next_question_id == 1132:
                    return await self.special_questions.handle_question_1132(question, message)
                next_question = await self.update_user_state_with_next_question(next_question_id)
                keyboard = await self.answer_keyboard_preparation(next_question)
            if next_question.image_url:

                await message.answer_photo(photo=FSInputFile(path=f"{next_question.image_url}"))
            if keyboard is not None:
                return await message.answer(next_question.question, reply_markup=keyboard)
            else:
                return await message.answer(next_question.question)
        else:
            await message.send_copy(chat_id=6977727803)

        #TODO Отправка данных о пользователе
            user_data = f"Name: {self.user.name}, Telegram ID: {self.user.telegram_user_id}"
            
            
            next_question_id = question.next_question_id
            if next_question_id is not None:
                if next_question_id == 1132:
                    return await self.special_questions.handle_question_1132(question, message)
                next_question = await self.update_user_state_with_next_question(next_question_id)
                keyboard = await self.answer_keyboard_preparation(next_question)
                if keyboard is not None:
                    return await message.answer(next_question.question, reply_markup=keyboard)
                else:
                    return await message.answer(next_question.question)


    async def handle_file_answer(self, question, message: types.Message):
        await message.send_copy(chat_id=6977727803)
        user_data = f"Name: {self.user.name}, Telegram ID: {self.user.telegram_user_id}"
        next_question_id = question.next_question_id
        if next_question_id is not None:
            next_question = await self.update_user_state_with_next_question(next_question_id)
            keyboard = await self.answer_keyboard_preparation(next_question)
        if next_question.image_url:
            await message.answer_photo(photo=FSInputFile(path=f"{next_question.image_url}"))
        if keyboard is not None:
            return await message.answer(next_question.question, reply_markup=keyboard)
        else:
            return await message.answer(next_question.question)


    async def handle_unknown_answer(self, message):
        await message.answer("Неизвестный тип ответа.")
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



async def hi_message(message: types.Message):   
    try:
        telegram_user_id = message.from_user.id
        user = await User.get_or_none(telegram_user_id=telegram_user_id)
        if not user:
            await message.answer("Вы не зарегистрированы, для регистрации используйте команду /start")
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
                await message.answer(first_question.question)
            return

        q_manager = QuestionManager(user, user_state)
        await q_manager.process_answer(brief, message)

    except Exception as e:
        print(f"Error in hi_message: {e}")
        await message.answer("Произошла ошибка, попробуйте позже.")