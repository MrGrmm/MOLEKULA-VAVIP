from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import json
import sqlite3
import datetime
from models import User, Brief, Question, UserState, Answer
from config import API_TOKEN
import aiohttp


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
                # await callback_query.answer("Ваше имя было успешно сохранено.")
            except Exception as e:
                # В случае ошибки, информируем пользователя
                await callback_query.answer(f"Произошла ошибка при сохранении вашего имени: {e}")
                print(f"Error saving user name: {e}")


        async def handle_question_2104(self, answer, question, callback_query):
            if not self.parent.user_state.context_data:
                self.parent.user_state.context_data = {}
            # Обновление context_data в зависимости от ответа пользователя
            self.parent.user_state.context_data.update({"house_floor_count": int(answer)})
            # Сохранение обновленного состояния в базу данных
            await self.parent.user_state.save()
            print("Context data updated:", self.parent.user_state.context_data)



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

        async def handle_question_2121(self, answer, question, callback_query):
    # Получаем текущее количество повторений из context_data
            repeats_remaining = self.parent.user_state.context_data.get('house_floor_count', 1)

            if repeats_remaining > 1:
                # Уменьшаем количество оставшихся повторений
                self.parent.user_state.context_data['house_floor_count'] = repeats_remaining - 1
                await self.parent.user_state.save()

                # Подготовка клавиатуры, если необходимо
                keyboard = await self.parent.answer_keyboard_preparation(question)

                # Повторяем вопрос
                await callback_query.answer(question.question, reply_markup=keyboard)
            else:
                # Переходим к следующему вопросу или завершаем, если повторения закончились
                self.parent.user_state.context_data.pop('house_floor_count', None)                
                await self.parent.user_state.save()
                await self.parent.handle_combo_answer(answer, question, callback_query)
                
        async def handle_question_2127(self, answer, question, callback_query):
            selected_options = self.parent.user_state.context_data.get('selected_answers', [])
            if not answer == "ЭТО ВСЁ, ПРОДОЛЖИТЬ!":
                selected_options.append(answer)
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
                return await callback_query.answer(question.question, reply_markup=keyboard)
            
            else:
                # Логика завершения вопроса
                self.parent.user_state.context_data.pop('selected_answers', None)                
                await self.parent.user_state.save()
                await self.parent.handle_choice_answer(answer, question, callback_query)
        

    def __init__(self, user, user_state):
        self.user = user
        self.user_state = user_state
        self.special_questions = self.SpecialQuestions(self)

    async def process_answer(self, answer, callback_query):
        current_question = await self.fetch_current_question()

        if not current_question:
            return "Вопрос не найден."

        # Проверка, является ли вопрос специальным
        if current_question.id in [1, 2104, 2112, 2113, 2121, 2127]:  # ID специальных вопросов
            method = getattr(self.special_questions, f'handle_question_{current_question.id}', None)
            if method:
                if current_question.id in [2112, 2113, 2121, 2127]:
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


    async def handle_file_answer(self, message, state: FSMContext):
        pass

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

