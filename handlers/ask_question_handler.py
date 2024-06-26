import asyncio
import logging
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile
import sqlite3
import json
import re
import datetime
from models import User, Brief, Question, UserState, Answer

# Настройка логгирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import asyncio
import logging
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile
import sqlite3
import json
import re
import datetime
from models import User, Brief, Question, UserState, Answer

# Настройка логгирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuestionManager:
    class SpecialQuestions:
        def __init__(self, parent):
            self.parent = parent  # Ссылка на экземпляр QuestionManager для доступа к его атрибутам и методам

        def create_unconfigured_nodes(self, node_count):
            for i in range(1, node_count + 1):
                self.parent.user_state.context_data.update({f'unconfigured_node_{i}': None}) # Или любое другое значение по умолчанию

        async def handle_skip_question(self, message):
            if not self.parent.user_state.context_data:
                self.parent.user_state.context_data = {}
            self.parent.user_state.context_data.update({self.parent.user_state.current_question_id: False})
            await self.parent.user_state.save()

        async def handle_question_consultation(self, message, current_question):
            if current_question.image_url:
                await message.answer_photo(photo=FSInputFile("img/logo.jpg"))
            if message.text == "Нужна консультация":
                await message.answer(current_question.consultation_url)
        

        async def handle_question_1(self, message):
            try:
                self.parent.user.name = message.text
                await self.parent.user.save()
            except Exception as e:
                await message.answer(f"Произошла ошибка при сохранении вашего имени: {e}")
                logger.error(f"Error saving user name: {e}")

        async def handle_question_5(self, message):
            if not self.parent.user_state.context_data:
                self.parent.user_state.context_data = {}
            if message.text == "ДА":
                self.parent.user_state.context_data.update({"project_needed": ["Узел ввода", "Канализация", "Отопление", "Водоснабжение"]})
            await self.parent.user_state.save()

        async def handle_question_6(self, message):
            if not self.parent.user_state.context_data:
                self.parent.user_state.context_data = {}
            if message.text == "ДА":
                project_needed = self.parent.user_state.context_data.get("project_needed", [])
                if "Узел ввода" not in project_needed:
                    project_needed.append("Узел ввода")
                self.parent.user_state.context_data.update({"project_needed": project_needed})
            await self.parent.user_state.save()

        async def handle_question_7(self, message):
            if not self.parent.user_state.context_data:
                self.parent.user_state.context_data = {}
            if message.text == "ДА":
                project_needed = self.parent.user_state.context_data.get("project_needed", [])
                if "Канализация" not in project_needed:
                    project_needed.append("Канализация")
                self.parent.user_state.context_data.update({"project_needed": project_needed})
            await self.parent.user_state.save()

        async def handle_question_8(self, message):
            if not self.parent.user_state.context_data:
                self.parent.user_state.context_data = {}
            if message.text == "ДА":
                project_needed = self.parent.user_state.context_data.get("project_needed", [])
                if "Отопление" not in project_needed:
                    project_needed.append("Отопление")
                self.parent.user_state.context_data.update({"project_needed": project_needed})
            await self.parent.user_state.save()

        async def handle_question_9(self, message):
            if not self.parent.user_state.context_data:
                self.parent.user_state.context_data = {}
            if message.text == "ДА":
                project_needed = self.parent.user_state.context_data.get("project_needed", [])
                if "Водоснабжение" not in project_needed:
                    project_needed.append("Водоснабжение")
                self.parent.user_state.context_data.update({"project_needed": project_needed})
            await self.parent.user_state.save()

        async def handle_question_50_branch(self, question, message):
            selected_options = self.parent.user_state.context_data.get('project_needed', [])
            keyboard = ReplyKeyboardMarkup(
                resize_keyboard=True,
                one_time_keyboard=True,
                keyboard=[
                    [KeyboardButton(text=option)] for option in selected_options
                ]
            )
            return keyboard

        async def handle_question_1011(self, message):
            if not self.parent.user_state.context_data:
                self.parent.user_state.context_data = {}
            if not message.text == "Нужна консультация":
                if message.text == "НЕТ":
                    self.parent.user_state.context_data.update({"unconfigured_node_count": int(0)})
                else:
                    self.parent.user_state.context_data.update({"unconfigured_node_count": int(message.text)})
                self.create_unconfigured_nodes(int(message.text))
            await self.parent.user_state.save()
            logger.info("Context data updated: %s", self.parent.user_state.context_data)

        async def handle_question_1100(self, message):
            if not self.parent.user_state.context_data:
                self.parent.user_state.context_data = {}
            if message.text.isdigit():
                self.parent.user_state.context_data["total_bathrooms"] = int(message.text)
                self.parent.user_state.context_data["unconfigured_bathroom_count"] = int(message.text)
                await self.parent.user_state.save()
            logger.info("Context data updated: %s", self.parent.user_state.context_data)

        async def handle_question_1101(self, message):
            if not self.parent.user_state.context_data:
                self.parent.user_state.context_data = {}
            if not message.text == "Нужна консультация":
                self.parent.user_state.context_data.update({"total_kitchens": int(message.text)})
                self.parent.user_state.context_data.update({"unconfigured_kitchen_count": int(message.text)})
            await self.parent.user_state.save()
            logger.info("Context data updated: %s", self.parent.user_state.context_data)

        async def handle_question_1102(self, message):
            if not self.parent.user_state.context_data:
                self.parent.user_state.context_data = {}
            if not message.text == "Нужна консультация":
                self.parent.user_state.context_data.update({"total_laundries": int(message.text)})
                self.parent.user_state.context_data.update({"unconfigured_laundries_count": int(message.text)})
            await self.parent.user_state.save()
            logger.info("Context data updated: %s", self.parent.user_state.context_data)

        async def handle_question_1103(self, message):
            if not self.parent.user_state.context_data:
                self.parent.user_state.context_data = {}
            if message.text.isdigit():
                self.parent.user_state.context_data.update({"total_wetrooms": int(message.text)})
                self.parent.user_state.context_data.update({"unconfigured_wetroom_count": int(message.text)})
            else:
                self.parent.user_state.context_data.update({"total_wetrooms": 0})
                self.parent.user_state.context_data.update({"unconfigured_wetroom_count": 0})
            logger.info("Context data updated: %s", self.parent.user_state.context_data)

        async def replace_placeholder_bathrooms(self, question):
            """
            Заменяет все вхождения '*' в тексте вопроса на значение unconfigured_bathroom_count из context_data.
            """
            unconfigured_bathroom_count = self.parent.user_state.context_data.get('unconfigured_bathroom_count', 0)
            question_text = question.question
            if '*' in question_text:
                question_text = question_text.replace('*', str(unconfigured_bathroom_count))
                question.question = question_text
            return question

        async def handle_question_1104(self, question, message):
            # Получаем данные unconfigured_bathroom_count из context_data
            unconfigured_bathrooms_count = self.parent.user_state.context_data.get("unconfigured_bathroom_count", 0)

            if unconfigured_bathrooms_count > 0:
                # Получаем текстовые данные из сообщения пользователя
                if message.text and message.text.isdigit():
                    bathrooms_to_subtract = int(message.text)
                    
                    # Минусуем ответ пользователя из unconfigured_bathrooms_count и сохраняем изменения
                    unconfigured_bathrooms_count -= bathrooms_to_subtract
                    self.parent.user_state.context_data["unconfigured_bathroom_count"] = unconfigured_bathrooms_count
                    await self.parent.user_state.save()
                    
                    await message.answer(f"Осталось неконфигурированных ванных комнат: {unconfigured_bathrooms_count}")
                    await self.parent.handle_choice_answer(question, message)
                else:
                    await message.answer("Пожалуйста, введите корректное количество ванных комнат.")
            else:
                # Оповещаем пользователя, что все ванные комнаты уже подключены к другому узлу
                await message.answer("Все ванные комнаты уже подключены.")
                # Приступаем к следующему вопросу
                await self.parent.handle_choice_answer(question, message)

        async def replace_placeholder_kitchen(self, question):
            """
            Заменяет все вхождения '*' в тексте вопроса на значение total_bathrooms из context_data.
            """
            unconfigured_kitchen_count = self.parent.user_state.context_data.get('unconfigured_kitchen_count', 0)
            question_text = question.question
            if '*' in question_text:
                question_text = question_text.replace('*', str(unconfigured_kitchen_count))
                question.question = question_text
            return question

        async def handle_question_1105(self, question, message):
            # Получаем данные unconfigured_bathroom_count из context_data
            unconfigured_kitchen_count = self.parent.user_state.context_data.get("unconfigured_kitchen_count", 0)

            if unconfigured_kitchen_count > 0:
                # Получаем текстовые данные из сообщения пользователя
                if message.text and message.text.isdigit():
                    kitchen_to_subtract = int(message.text)
                    
                    # Минусуем ответ пользователя из unconfigured_bathrooms_count и сохраняем изменения
                    unconfigured_kitchen_count -= kitchen_to_subtract
                    self.parent.user_state.context_data["unconfigured_kitchen_count"] = unconfigured_kitchen_count
                    await self.parent.user_state.save()
                    
                    await message.answer(f"Осталось неконфигурированных кухонь: {unconfigured_kitchen_count}")
                    await self.parent.handle_choice_answer(question, message)
                else:
                    await message.answer("Пожалуйста, введите корректное количество кухонь.")
            else:
                # Оповещаем пользователя, что все ванные комнаты уже подключены к другому узлу
                await message.answer("Все ванные комнаты уже подключены.")
                # Приступаем к следующему вопросу
                await self.parent.handle_choice_answer(question, message)

        async def replace_placeholder_laundries(self, question):
            """
            Заменяет все вхождения '*' в тексте вопроса на значение total_bathrooms из context_data.
            """
            unconfigured_laundries_count = self.parent.user_state.context_data.get('unconfigured_laundries_count', 0)
            question_text = question.question
            if '*' in question_text:
                question_text = question_text.replace('*', str(unconfigured_laundries_count))
                question.question = question_text
            return question

        async def handle_question_1106(self, question, message):
            # Получаем данные unconfigured_bathroom_count из context_data
            unconfigured_laundries_count = self.parent.user_state.context_data.get("unconfigured_laundries_count", 0)

            if unconfigured_laundries_count > 0:
                # Получаем текстовые данные из сообщения пользователя
                if message.text and message.text.isdigit():
                    laundries_to_subtract = int(message.text)
                    
                    # Минусуем ответ пользователя из unconfigured_bathrooms_count и сохраняем изменения
                    unconfigured_laundries_count -= laundries_to_subtract
                    self.parent.user_state.context_data["unconfigured_laundries_count"] = unconfigured_laundries_count
                    await self.parent.user_state.save()
                    
                    await message.answer(f"Осталось неконфигурированных прачечных: {unconfigured_laundries_count}")
                    await self.parent.handle_choice_answer(question, message)
                else:
                    await message.answer("Пожалуйста, введите корректное количество прачечных.")
            else:
                # Оповещаем пользователя, что все ванные комнаты уже подключены к другому узлу
                await message.answer("Все ванные комнаты уже подключены.")
                # Приступаем к следующему вопросу
                await self.parent.handle_choice_answer(question, message)

        async def handle_question_1107(self, message):
            kitchen_count = self.parent.user_state.context_data.get("unconfigured_wetroom_count", 0) 
            if kitchen_count > 0:
                pass
            else:
                await self.parent.skip_to_next_question(message)
            # TODO

        async def replace_placeholder_wc(self, question):
            """
            Заменяет все вхождения '*' в тексте вопроса на значение total_bathrooms из context_data.
            """
            current_bathr_iteration = self.parent.user_state.context_data.get('current_bathr_iteration', 1)
            question_text = question.question
            if '*' in question_text:
                question_text = question_text.replace('*', str(current_bathr_iteration))
                question.question = question_text
            return question

        async def handle_question_1108(self,question, message):
            # Получаем общее количество ванных комнат
            total_bathrooms = self.parent.user_state.context_data.get("total_bathrooms", 0)
            
            # Проверяем, существует ли итерация в context_data, если нет - создаем
            if "current_bathr_iteration" not in self.parent.user_state.context_data:
                self.parent.user_state.context_data["current_bathr_iteration"] = 1
            else:
                self.parent.user_state.context_data["current_bathr_iteration"] += 1
            
            current_iteration = self.parent.user_state.context_data["current_bathr_iteration"]

            # Если итерация превышает общее количество ванных комнат, переходим к следующему вопросу
            if current_iteration > total_bathrooms:
                self.parent.user_state.context_data.pop("current_bathr_iteration", None)
                return await self.parent.skip_to_next_question(message)

            
            # Получаем вопрос 1108
            question = await Question.get_or_none(id=1108)
            if question:
                # Заменяем * на текущую итерацию
                keyboard = await self.parent.answer_keyboard_preparation(question)
                question = await self.replace_placeholder_wc(question)
                if question.image_url:
                    await message.answer_photo(photo=FSInputFile(path=f"{question.image_url}"))
                if keyboard:
                    await message.answer(question.question, reply_markup=keyboard)
                else:
                    await message.answer(question.question)
                
            await self.parent.user_state.save()

        async def handle_question_1109(self, question, message):
            # Получаем общее количество ванных комнат
            total_bathrooms = self.parent.user_state.context_data.get("total_bathrooms", 0)
            
            # Проверяем, существует ли итерация в context_data, если нет - создаем
            if "current_bathr_iteration" not in self.parent.user_state.context_data:
                self.parent.user_state.context_data["current_bathr_iteration"] = 1
            else:
                self.parent.user_state.context_data["current_bathr_iteration"] += 1
            
            current_iteration = self.parent.user_state.context_data["current_bathr_iteration"]

            # Если итерация превышает общее количество ванных комнат, переходим к следующему вопросу
            if current_iteration > total_bathrooms:
                self.parent.user_state.context_data.pop("current_bathr_iteration", None)
                await self.parent.skip_to_next_question(message)
                return await self.parent.user_state.save()
            
            # Получаем вопрос 1109
            question = await Question.get_or_none(id=1109)
            if question:
                # Заменяем * на текущую итерацию
                keyboard = await self.parent.answer_keyboard_preparation(question)
                question = await self.replace_placeholder_wc(question)
                if question.image_url:
                    await message.answer_photo(photo=FSInputFile(path=f"{question.image_url}"))
                if keyboard:
                    await message.answer(question.question, reply_markup=keyboard)
                else:
                    await message.answer(question.question)
                
            await self.parent.user_state.save()

        async def handle_question_1110(self, question, message):
            # Получаем общее количество ванных комнат
            total_bathrooms = self.parent.user_state.context_data.get("total_bathrooms", 0)
            
            # Проверяем, существует ли итерация в context_data, если нет - создаем
            if "current_bathr_iteration" not in self.parent.user_state.context_data:
                self.parent.user_state.context_data["current_bathr_iteration"] = 1
            else:
                self.parent.user_state.context_data["current_bathr_iteration"] += 1
            
            current_iteration = self.parent.user_state.context_data["current_bathr_iteration"]

            # Если итерация превышает общее количество ванных комнат, переходим к следующему вопросу
            if current_iteration > total_bathrooms:
                self.parent.user_state.context_data.pop("current_bathr_iteration", None)
                await self.parent.skip_to_next_question(message)
                return await self.parent.user_state.save()
            
            # Получаем вопрос 1109
            question = await Question.get_or_none(id=1110)
            if question:
                # Заменяем * на текущую итерацию
                keyboard = await self.parent.answer_keyboard_preparation(question)
                question = await self.replace_placeholder_wc(question)
                if question.image_url:
                    await message.answer_photo(photo=FSInputFile(path=f"{question.image_url}"))
                if keyboard:
                    await message.answer(question.question, reply_markup=keyboard)
                else:
                    await message.answer(question.question)
                
            await self.parent.user_state.save()

        async def handle_question_1111(self, question, message):
            # Получаем общее количество ванных комнат
            total_bathrooms = self.parent.user_state.context_data.get("total_bathrooms", 0)
            
            # Проверяем, существует ли итерация в context_data, если нет - создаем
            if "current_bathr_iteration" not in self.parent.user_state.context_data:
                self.parent.user_state.context_data["current_bathr_iteration"] = 1
            else:
                self.parent.user_state.context_data["current_bathr_iteration"] += 1
            
            current_iteration = self.parent.user_state.context_data["current_bathr_iteration"]

            # Если итерация превышает общее количество ванных комнат, переходим к следующему вопросу
            if current_iteration > total_bathrooms:
                self.parent.user_state.context_data.pop("current_bathr_iteration", None)
                await self.parent.skip_to_next_question(message)
                return await self.parent.user_state.save()
            
            # Получаем вопрос 1109
            question = await Question.get_or_none(id=1111)
            if question:
                # Заменяем * на текущую итерацию
                keyboard = await self.parent.answer_keyboard_preparation(question)
                question = await self.replace_placeholder_wc(question)
                if question.image_url:
                    await message.answer_photo(photo=FSInputFile(path=f"{question.image_url}"))
                if keyboard:
                    await message.answer(question.question, reply_markup=keyboard)
                else:
                    await message.answer(question.question)
                
            await self.parent.user_state.save()

        async def handle_question_1112(self, question, message):
            # Получаем общее количество ванных комнат
            total_bathrooms = self.parent.user_state.context_data.get("total_bathrooms", 0)
            
            # Проверяем, существует ли итерация в context_data, если нет - создаем
            if "current_bathr_iteration" not in self.parent.user_state.context_data:
                self.parent.user_state.context_data["current_bathr_iteration"] = 1
            else:
                self.parent.user_state.context_data["current_bathr_iteration"] += 1
            
            current_iteration = self.parent.user_state.context_data["current_bathr_iteration"]

            # Если итерация превышает общее количество ванных комнат, переходим к следующему вопросу
            if current_iteration > total_bathrooms:
                self.parent.user_state.context_data.pop("current_bathr_iteration", None)
                await self.parent.skip_to_next_question(message)
                return await self.parent.user_state.save()
            
            # Получаем вопрос 1109
            question = await Question.get_or_none(id=1112)
            if question:
                # Заменяем * на текущую итерацию
                keyboard = await self.parent.answer_keyboard_preparation(question)
                question = await self.replace_placeholder_wc(question)
                if question.image_url:
                    await message.answer_photo(photo=FSInputFile(path=f"{question.image_url}"))
                if keyboard:
                    await message.answer(question.question, reply_markup=keyboard)
                else:
                    await message.answer(question.question)
                
            await self.parent.user_state.save()

        async def handle_question_1113(self, question, message):
            # Получаем общее количество ванных комнат
            total_bathrooms = self.parent.user_state.context_data.get("total_bathrooms", 0)
            
            # Проверяем, существует ли итерация в context_data, если нет - создаем
            if "current_bathr_iteration" not in self.parent.user_state.context_data:
                self.parent.user_state.context_data["current_bathr_iteration"] = 1
            else:
                self.parent.user_state.context_data["current_bathr_iteration"] += 1
            
            current_iteration = self.parent.user_state.context_data["current_bathr_iteration"]

            # Если итерация превышает общее количество ванных комнат, переходим к следующему вопросу
            if current_iteration > total_bathrooms:
                self.parent.user_state.context_data.pop("current_bathr_iteration", None)
                await self.parent.skip_to_next_question(message)
                return await self.parent.user_state.save()
            
            # Получаем вопрос 1109
            question = await Question.get_or_none(id=1113)
            if question:
                # Заменяем * на текущую итерацию
                keyboard = await self.parent.answer_keyboard_preparation(question)
                question = await self.replace_placeholder_wc(question)
                if question.image_url:
                    await message.answer_photo(photo=FSInputFile(path=f"{question.image_url}"))
                if keyboard:
                    await message.answer(question.question, reply_markup=keyboard)
                else:
                    await message.answer(question.question)
                
            await self.parent.user_state.save()

        async def handle_question_1114(self, question, message):
            # Получаем общее количество ванных комнат
            total_bathrooms = self.parent.user_state.context_data.get("total_bathrooms", 0)
            
            # Проверяем, существует ли итерация в context_data, если нет - создаем
            if "current_bathr_iteration" not in self.parent.user_state.context_data:
                self.parent.user_state.context_data["current_bathr_iteration"] = 1
            else:
                self.parent.user_state.context_data["current_bathr_iteration"] += 1
            
            current_iteration = self.parent.user_state.context_data["current_bathr_iteration"]

            # Если итерация превышает общее количество ванных комнат, переходим к следующему вопросу
            if current_iteration > total_bathrooms:
                self.parent.user_state.context_data.pop("current_bathr_iteration", None)
                await self.parent.skip_to_next_question(message)
                return await self.parent.user_state.save()
            
            # Получаем вопрос 1109
            question = await Question.get_or_none(id=1114)
            if question:
                # Заменяем * на текущую итерацию
                keyboard = await self.parent.answer_keyboard_preparation(question)
                question = await self.replace_placeholder_wc(question)
                if question.image_url:
                    await message.answer_photo(photo=FSInputFile(path=f"{question.image_url}"))
                if keyboard:
                    await message.answer(question.question, reply_markup=keyboard)
                else:
                    await message.answer(question.question)
                
            await self.parent.user_state.save()

        async def replace_placeholder_ktch(self, question):
            """
            Заменяет все вхождения '*' в тексте вопроса на значение total_bathrooms из context_data.
            """
            current_ktch_iteration = self.parent.user_state.context_data.get('current_ktch_iteration', 1)
            question_text = question.question
            if '*' in question_text:
                question_text = question_text.replace('*', str(current_ktch_iteration))
                question.question = question_text
            return question

        async def handle_question_1115(self, question, message):
            # Получаем общее количество ванных комнат
            total_bathrooms = self.parent.user_state.context_data.get("total_kitchens", 0)
            
            # Проверяем, существует ли итерация в context_data, если нет - создаем
            if "current_ktch_iteration" not in self.parent.user_state.context_data:
                self.parent.user_state.context_data["current_ktch_iteration"] = 1
            else:
                self.parent.user_state.context_data["current_ktch_iteration"] += 1
            
            current_iteration = self.parent.user_state.context_data["current_ktch_iteration"]

            # Если итерация превышает общее количество ванных комнат, переходим к следующему вопросу
            if current_iteration > total_bathrooms:
                self.parent.user_state.context_data.pop("current_ktch_iteration", None)
                await self.parent.skip_to_next_question(message)
                return await self.parent.user_state.save()
            
            # Получаем вопрос 1109
            question = await Question.get_or_none(id=1115)
            if question:
                # Заменяем * на текущую итерацию
                keyboard = await self.parent.answer_keyboard_preparation(question)
                question = await self.replace_placeholder_ktch(question)
                if question.image_url:
                    await message.answer_photo(photo=FSInputFile(path=f"{question.image_url}"))
                if keyboard:
                    await message.answer(question.question, reply_markup=keyboard)
                else:
                    await message.answer(question.question)
                
            await self.parent.user_state.save()


        async def handle_question_1116(self, question, message):
            # Получаем общее количество ванных комнат
            total_bathrooms = self.parent.user_state.context_data.get("total_kitchens", 0)
            
            # Проверяем, существует ли итерация в context_data, если нет - создаем
            if "current_ktch_iteration" not in self.parent.user_state.context_data:
                self.parent.user_state.context_data["current_ktch_iteration"] = 1
            else:
                self.parent.user_state.context_data["current_ktch_iteration"] += 1
            
            current_iteration = self.parent.user_state.context_data["current_ktch_iteration"]

            # Если итерация превышает общее количество ванных комнат, переходим к следующему вопросу
            if current_iteration > total_bathrooms:
                self.parent.user_state.context_data.pop("current_ktch_iteration", None)
                await self.parent.skip_to_next_question(message)
                return await self.parent.user_state.save()
            
            # Получаем вопрос 1109
            question = await Question.get_or_none(id=1116)
            if question:
                # Заменяем * на текущую итерацию
                keyboard = await self.parent.answer_keyboard_preparation(question)
                question = await self.replace_placeholder_ktch(question)
                if question.image_url:
                    await message.answer_photo(photo=FSInputFile(path=f"{question.image_url}"))
                if keyboard:
                    await message.answer(question.question, reply_markup=keyboard)
                else:
                    await message.answer(question.question)
                
            await self.parent.user_state.save()


        async def handle_question_1117(self, question, message):
            # Получаем общее количество ванных комнат
            total_bathrooms = self.parent.user_state.context_data.get("total_kitchens", 0)
            
            # Проверяем, существует ли итерация в context_data, если нет - создаем
            if "current_ktch_iteration" not in self.parent.user_state.context_data:
                self.parent.user_state.context_data["current_ktch_iteration"] = 1
            else:
                self.parent.user_state.context_data["current_ktch_iteration"] += 1
            
            current_iteration = self.parent.user_state.context_data["current_ktch_iteration"]

            # Если итерация превышает общее количество ванных комнат, переходим к следующему вопросу
            if current_iteration > total_bathrooms:
                self.parent.user_state.context_data.pop("current_ktch_iteration", None)
                await self.parent.skip_to_next_question(message)
                return await self.parent.user_state.save()
            
            # Получаем вопрос 1109
            question = await Question.get_or_none(id=1117)
            if question:
                # Заменяем * на текущую итерацию
                keyboard = await self.parent.answer_keyboard_preparation(question)
                question = await self.replace_placeholder_ktch(question)
                if question.image_url:
                    await message.answer_photo(photo=FSInputFile(path=f"{question.image_url}"))
                if keyboard:
                    await message.answer(question.question, reply_markup=keyboard)
                else:
                    await message.answer(question.question)
                
            await self.parent.user_state.save()

        async def handle_question_1118(self, question, message):
           # Получаем общее количество ванных комнат
            total_bathrooms = self.parent.user_state.context_data.get("total_kitchens", 0)
            
            # Проверяем, существует ли итерация в context_data, если нет - создаем
            if "current_ktch_iteration" not in self.parent.user_state.context_data:
                self.parent.user_state.context_data["current_ktch_iteration"] = 1
            else:
                self.parent.user_state.context_data["current_ktch_iteration"] += 1
            
            current_iteration = self.parent.user_state.context_data["current_ktch_iteration"]

            # Если итерация превышает общее количество ванных комнат, переходим к следующему вопросу
            if current_iteration > total_bathrooms:
                self.parent.user_state.context_data.pop("current_ktch_iteration", None)
                await self.parent.skip_to_next_question(message)
                return await self.parent.user_state.save()
            
            # Получаем вопрос 1109
            question = await Question.get_or_none(id=1118)
            if question:
                # Заменяем * на текущую итерацию
                keyboard = await self.parent.answer_keyboard_preparation(question)
                question = await self.replace_placeholder_ktch(question)
                if question.image_url:
                    await message.answer_photo(photo=FSInputFile(path=f"{question.image_url}"))
                if keyboard:
                    await message.answer(question.question, reply_markup=keyboard)
                else:
                    await message.answer(question.question)
                
            await self.parent.user_state.save()

        async def handle_question_1119(self, question, message):
           # Получаем общее количество ванных комнат
            total_bathrooms = self.parent.user_state.context_data.get("total_kitchens", 0)
            
            # Проверяем, существует ли итерация в context_data, если нет - создаем
            if "current_ktch_iteration" not in self.parent.user_state.context_data:
                self.parent.user_state.context_data["current_ktch_iteration"] = 1
            else:
                self.parent.user_state.context_data["current_ktch_iteration"] += 1
            
            current_iteration = self.parent.user_state.context_data["current_ktch_iteration"]

            # Если итерация превышает общее количество ванных комнат, переходим к следующему вопросу
            if current_iteration > total_bathrooms:
                self.parent.user_state.context_data.pop("current_ktch_iteration", None)
                await self.parent.skip_to_next_question(message)
                return await self.parent.user_state.save()
            
            # Получаем вопрос 1109
            question = await Question.get_or_none(id=1119)
            if question:
                # Заменяем * на текущую итерацию
                keyboard = await self.parent.answer_keyboard_preparation(question)
                question = await self.replace_placeholder_ktch(question)
                if question.image_url:
                    await message.answer_photo(photo=FSInputFile(path=f"{question.image_url}"))
                if keyboard:
                    await message.answer(question.question, reply_markup=keyboard)
                else:
                    await message.answer(question.question)
                
            await self.parent.user_state.save()
            
        async def handle_question_1120(self, question, message):
            # Получаем общее количество ванных комнат
            total_bathrooms = self.parent.user_state.context_data.get("total_kitchens", 0)
            
            # Проверяем, существует ли итерация в context_data, если нет - создаем
            if "current_ktch_iteration" not in self.parent.user_state.context_data:
                self.parent.user_state.context_data["current_ktch_iteration"] = 1
            else:
                self.parent.user_state.context_data["current_ktch_iteration"] += 1
            
            current_iteration = self.parent.user_state.context_data["current_ktch_iteration"]

            # Если итерация превышает общее количество ванных комнат, переходим к следующему вопросу
            if current_iteration > total_bathrooms:
                self.parent.user_state.context_data.pop("current_ktch_iteration", None)
                await self.parent.skip_to_next_question(message)
                return await self.parent.user_state.save()
            
            # Получаем вопрос 1109
            question = await Question.get_or_none(id=1120)
            if question:
                # Заменяем * на текущую итерацию
                keyboard = await self.parent.answer_keyboard_preparation(question)
                question = await self.replace_placeholder_ktch(question)
                if question.image_url:
                    await message.answer_photo(photo=FSInputFile(path=f"{question.image_url}"))
                if keyboard:
                    await message.answer(question.question, reply_markup=keyboard)
                else:
                    await message.answer(question.question)
                
            await self.parent.user_state.save()

        async def handle_question_1124(self, message):
            if not self.parent.user_state.context_data:
                self.parent.user_state.context_data = {}
            if message.text != "Нужна консультация":
                number_match = re.search(r'\d+', message.text)
                if number_match:
                    number_of_residence = int(number_match.group())
                    self.parent.user_state.context_data.update({"number_of_residence": number_of_residence})
                await self.parent.user_state.save()
            else:
                await message.answer("Консультация нужна. Что вас интересует?")

        async def replace_placeholder_lnd(self, question):
            """
            Заменяет все вхождения '*' в тексте вопроса на значение total_bathrooms из context_data.
            """
            current_lnd_iteration = self.parent.user_state.context_data.get('current_lnd_iteration', 1)
            question_text = question.question
            if '*' in question_text:
                question_text = question_text.replace('*', str(current_lnd_iteration))
                question.question = question_text
            return question

        async def handle_question_1121(self, question, message):
            # Получаем общее количество ванных комнат
            total_laundries = self.parent.user_state.context_data.get("total_laundries", 0)
            
            # Проверяем, существует ли итерация в context_data, если нет - создаем
            if "current_lnd_iteration" not in self.parent.user_state.context_data:
                self.parent.user_state.context_data["current_lnd_iteration"] = 1
            else:
                self.parent.user_state.context_data["current_lnd_iteration"] += 1
            
            current_iteration = self.parent.user_state.context_data["current_lnd_iteration"]

            # Если итерация превышает общее количество ванных комнат, переходим к следующему вопросу
            if current_iteration > total_laundries:
                self.parent.user_state.context_data.pop("current_lnd_iteration", None)
                await self.parent.skip_to_next_question(message)
                return await self.parent.user_state.save()
            
            # Получаем вопрос 1109
            question = await Question.get_or_none(id=1121)
            if question:
                # Заменяем * на текущую итерацию
                keyboard = await self.parent.answer_keyboard_preparation(question)
                question = await self.replace_placeholder_laundries(question)
                if question.image_url:
                    await message.answer_photo(photo=FSInputFile(path=f"{question.image_url}"))
                if keyboard:
                    await message.answer(question.question, reply_markup=keyboard)
                else:
                    await message.answer(question.question)
                
            await self.parent.user_state.save()

        async def handle_question_1122(self, question, message):
            # Получаем общее количество ванных комнат
            total_laundries = self.parent.user_state.context_data.get("total_laundries", 0)
            
            # Проверяем, существует ли итерация в context_data, если нет - создаем
            if "current_lnd_iteration" not in self.parent.user_state.context_data:
                self.parent.user_state.context_data["current_lnd_iteration"] = 1
            else:
                self.parent.user_state.context_data["current_lnd_iteration"] += 1
            
            current_iteration = self.parent.user_state.context_data["current_lnd_iteration"]

            # Если итерация превышает общее количество ванных комнат, переходим к следующему вопросу
            if current_iteration > total_laundries:
                self.parent.user_state.context_data.pop("current_lnd_iteration", None)
                await self.parent.skip_to_next_question(message)
                return await self.parent.user_state.save()
            
            # Получаем вопрос 1109
            question = await Question.get_or_none(id=1122)
            if question:
                # Заменяем * на текущую итерацию
                keyboard = await self.parent.answer_keyboard_preparation(question)
                question = await self.replace_placeholder_laundries(question)
                if question.image_url:
                    await message.answer_photo(photo=FSInputFile(path=f"{question.image_url}"))
                if keyboard:
                    await message.answer(question.question, reply_markup=keyboard)
                else:
                    await message.answer(question.question)
                
            await self.parent.user_state.save()

        async def handle_question_1127(self, message):
            if not self.parent.user_state.context_data:
                self.parent.user_state.context_data = {}
            if message.text == "Проточный":
                self.parent.user_state.context_data.update({"waterhater_branch": "Проточный"})
            elif message.text == "Накопительный":
                self.parent.user_state.context_data.update({"waterhater_branch": "Накопительный"})

        async def handle_question_1132(self, question, message):
            waterhater_branch = self.parent.user_state.context_data.get('waterhater_branch')
            next_question_id = 1132 if waterhater_branch == "Проточный" else 1138
            next_question = await self.parent.update_user_state_with_next_question(next_question_id)
            keyboard = await self.parent.answer_keyboard_preparation(next_question)
            if next_question.image_url:
                await message.answer_photo(photo=FSInputFile(path=f"{next_question.image_url}"))
            if keyboard:
                await message.answer(next_question.question, reply_markup=keyboard)
            else:
                await message.answer(next_question.question)

        async def handle_question_1143(self, message):
            if not self.parent.user_state.context_data:
                self.parent.user_state.context_data = {}
            if message.text != "ДА":
                self.parent.user_state.context_data.update({"retzirkuliatzia_goreacei_vodi": "NEPTUN Кран 12B Profi"})
            await self.parent.user_state.save()
            logger.info("Context data updated: %s", self.parent.user_state.context_data)

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
            next_question_id = 1434 if waterhater_branch == "Проточный" else 1440
            next_question = await self.parent.update_user_state_with_next_question(next_question_id)
            keyboard = await self.parent.answer_keyboard_preparation(next_question)
            if next_question.image_url:
                await message.answer_photo(photo=FSInputFile(path=f"{next_question.image_url}"))
            if keyboard:
                await message.answer(next_question.question, reply_markup=keyboard)
            else:
                await message.answer(next_question.question)

        async def handle_question_2100(self, message):
            if not self.parent.user_state.context_data:
                self.parent.user_state.context_data = {}
            if message.text in ["ДА", "ПЛАНИРУЕТСЯ"]:
                self.parent.user_state.context_data.update({"architectural_project": False})
            await self.parent.user_state.save()
            logger.info("Context data updated: %s", self.parent.user_state.context_data)

        async def handle_question_2102(self, message):
            if not self.parent.user_state.context_data:
                self.parent.user_state.context_data = {}
            if message.text in ["ДА", "ПЛАНИРУЕТСЯ"]:
                self.parent.user_state.context_data.update({"design_project": False})
            await self.parent.user_state.save()
            logger.info("Context data updated: %s", self.parent.user_state.context_data)

        async def handle_question_2104(self, message):
            if not self.parent.user_state.context_data:
                self.parent.user_state.context_data = {}
            self.parent.user_state.context_data.update({"house_floor_count": int(message.text)})
            await self.parent.user_state.save()
            logger.info("Context data updated: %s", self.parent.user_state.context_data)

        async def handle_question_2112(self, question, message):
            selected_options = self.parent.user_state.context_data.get('selected_answers', [])
            if message.text != "ЭТО ВСЁ":
                selected_options.append(message.text)
                self.parent.user_state.context_data['selected_answers'] = selected_options
                await self.parent.user_state.save()
                if message.text == "ЭЛЕКТРИЧЕСТВО":
                    return await self.parent.handle_choice_answer(question, message)
                remaining_options = {k: v for k, v in question.answer_options.items() if k not in selected_options or k == "Это всё"}
                keyboard = ReplyKeyboardMarkup(
                    resize_keyboard=True,
                    one_time_keyboard=True,
                    keyboard=[
                        [KeyboardButton(text=option)] for option in remaining_options
                    ]
                )
                return await message.answer(question.question, reply_markup=keyboard)
            else:
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
            return await message.answer(next_question.question, reply_markup=keyboard)

        async def handle_question_2121(self, question, message):
            repeats_remaining = self.parent.user_state.context_data.get('house_floor_count', 1)
            if repeats_remaining > 1:
                self.parent.user_state.context_data['house_floor_count'] = repeats_remaining - 1
                await self.parent.user_state.save()
                keyboard = await self.parent.answer_keyboard_preparation(question)
                await message.answer(question.question, reply_markup=keyboard)
            else:
                self.parent.user_state.context_data.pop('house_floor_count', None)
                await self.parent.user_state.save()
                await self.parent.handle_combo_answer(question, message)

        async def handle_question_2127(self, question, message):
            selected_options = self.parent.user_state.context_data.get('selected_answers', [])
            if message.text != "ЭТО ВСЁ, ПРОДОЛЖИТЬ!":
                selected_options.append(message.text)
                self.parent.user_state.context_data['selected_answers'] = selected_options
                await self.parent.user_state.save()
                remaining_options = {k: v for k, v in question.answer_options.items() if k not in selected_options or k == "Это всё"}
                keyboard = ReplyKeyboardMarkup(
                    resize_keyboard=True,
                    one_time_keyboard=True,
                    keyboard=[
                        [KeyboardButton(text=option)] for option in remaining_options
                    ]
                )
                return await message.answer(question.question, reply_markup=keyboard)
            else:
                self.parent.user_state.context_data.pop('selected_answers', None)
                await self.parent.user_state.save()
                await self.parent.handle_choice_answer(question, message)

    def __init__(self, user, user_state):
        self.user = user
        self.user_state = user_state
        self.special_questions = self.SpecialQuestions(self)

    async def skip_to_next_question(self, message):
        """
        Пропускает текущий вопрос и задает следующий вопрос пользователю.
        """
        current_question = await self.fetch_current_question()
        if not current_question:
            return await message.answer("Вопрос не найден.")
        
        next_question_id = current_question.answer_options.get('1')
        if not next_question_id:
            next_question_id = current_question.answer_options.get('ДА')
            if not next_question_id:
                next_question_id = current_question.answer_options.get('НЕТ')
                if not next_question_id:
                    return await message.answer("Следующий вопрос не найден.")
        
        next_question = await self.update_user_state_with_next_question(next_question_id)
        if not next_question:
            return await message.answer("Следующий вопрос не найден.")

        keyboard = await self.answer_keyboard_preparation(next_question)
        if next_question_id == 1104:
            next_question = await self.special_questions.replace_placeholder_bathrooms(next_question)
        if next_question_id == 1105:
            next_question = await self.special_questions.replace_placeholder_kitchen(next_question)         
        if next_question_id == 1106:
            next_question = await self.special_questions.replace_placeholder_laundries(next_question)
        if next_question_id in [1108, 1109, 1110, 1111, 1112, 1113, 1114]:
            if "current_bathr_iteration" not in self.user_state.context_data:
                self.user_state.context_data["current_bathr_iteration"] = 1
            else:
                self.user_state.context_data["current_bathr_iteration"] += 1
            await self.user_state.save()
            next_question == await self.special_questions.replace_placeholder_wc(next_question)
        elif next_question_id in [1115, 1116, 1117, 1118, 1119, 1120]:
            if "current_ktch_iteration" not in self.user_state.context_data:
                self.user_state.context_data["current_ktch_iteration"] = 1
            else:
                self.user_state.context_data["current_ktch_iteration"] += 1
            await self.user_state.save()
            next_question == await self.special_questions.replace_placeholder_ktch(next_question)
        elif next_question_id in [ 1121, 1122]:
            if "current_lnd_iteration" not in self.user_state.context_data:
                self.user_state.context_data["current_lnd_iteration"] = 1
            else:
                self.user_state.context_data["current_lnd_iteration"] += 1
            await self.user_state.save()
            next_question == await self.special_questions.replace_placeholder_ktch(next_question)
        if next_question.image_url:
            await message.answer_photo(photo=FSInputFile(path=f"{next_question.image_url}"))
        
        if keyboard:
            await message.answer(next_question.question, reply_markup=keyboard)
        else:
            await message.answer(next_question.question)

    async def process_answer(self, brief, message):
        await self.save_user_answer(brief, message)
        current_question = await self.fetch_current_question()
        if not current_question:
            return "Вопрос не найден."
        if message.text == "Нужна консультация":
            return await self.special_questions.handle_question_consultation(message, current_question)
        elif message.text == "ПРОПУСТИТЬ":
            await self.special_questions.handle_skip_question(message)
        if current_question.id in [1, 5, 6, 7, 8, 9, 1011, 1100, 1101, 1102, 1103, 1104, 1105, 1106, 1107, 1108, 1109, 1110, 1111, 1112, 1113, 1114, 1115, 1116, 1117, 1118, 1119, 1120, 1121, 1122, 1124, 1127, 1143, 1429, 2100, 2102, 2104, 2112, 2113, 2121, 2127]:
            method = getattr(self.special_questions, f'handle_question_{current_question.id}', None)
            if method:
                if current_question.id in [1104, 1105, 1106, 1108, 1109, 1110, 1111, 1112, 1113, 1114, 1115, 1116, 1117, 1118, 1119, 1120, 1121, 1122, 2112, 2113, 2121, 2127]:
                    return await method(current_question, message)
                else:
                    await method(message)
        answer_type = current_question.answer_type.name
        method_name = f"handle_{answer_type.lower()}_answer"
        handler = getattr(self, method_name, self.handle_unknown_answer)
        return await handler(current_question, message)

    async def fetch_current_question(self):
        try:
            if self.user_state and self.user_state.current_question:
                return await Question.get(id=self.user_state.current_question_id)
        except Exception as e:
            logger.error(f"Error fetching question: {e}")
        return None
    
    async def save_user_answer(self, brief, message):
        current_question = await Question.get_or_none(id=self.user_state.current_question_id)
        if not current_question:
            return "Вопрос не найден."
        try:
            answer_text = 'file' if message.text is None else message.text
            return await Answer.create(user=self.user, brief=brief, question=current_question, answer=answer_text)
        except Exception as e:
            logger.error(f"Error saving user answer: {e}")
            await message.answer(f"Ошибка: {e}")

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
        unconfig_nodes = self.user_state.context_data.get('unconfigured_node_count', 0)
        unconfig_weetrooms = self.user_state.context_data.get('unconfigured_wetroom_count', 0)
        next_question_id = current_question.next_question_id
        next_question = await self.update_user_state_with_next_question(next_question_id)
        if next_question_id == 9900 and unconfig_nodes > 0:
            await message.answer("Приступим к конфигурации следующего узла ввода")
            next_question = await self.update_user_state_with_next_question(1104)
            unconfig_nodes -= 1
            self.user_state.context_data["unconfigured_node_count"] = unconfig_nodes
            await self.user_state.save()
        elif next_question_id == 1166 and unconfig_weetrooms > 0:
            await message.answer("Приступим к конфигурации следующего узла ввода")
            next_question = await self.update_user_state_with_next_question(1108)
            unconfig_weetrooms -= 1
            self.user_state.context_data["unconfigured_wetroom_count"] = unconfig_weetrooms
            await self.user_state.save()
        keyboard = await self.answer_keyboard_preparation(next_question)
        if next_question.image_url:
            await message.answer_photo(photo=FSInputFile(path=f"{next_question.image_url}"))
        if keyboard:
            await message.answer(next_question.question, reply_markup=keyboard)
        else:
            await message.answer(next_question.question)

    async def handle_choice_answer(self, question, message):
        next_question_id = question.answer_options.get(message.text)
        unconfig_weetrooms = self.user_state.context_data.get('unconfigured_wetroom_count', 0)
        if next_question_id == 1132:
            return await self.special_questions.handle_question_1132(question, message)
        next_question = await self.update_user_state_with_next_question(next_question_id)
        if next_question_id == 1106 and unconfig_weetrooms > 0:
            next_question = await self.update_user_state_with_next_question(1108)
            unconfig_weetrooms -= 1
            self.user_state.context_data["unconfigured_wetroom_count"] = unconfig_weetrooms
            await self.user_state.save()    
        keyboard = await self.answer_keyboard_preparation(next_question)
        if next_question_id == 1104:
            unconfigured_bathroom_count = self.user_state.context_data.get('unconfigured_wetroom_count', 0)
            if unconfigured_bathroom_count > 0:
                next_question = await self.special_questions.replace_placeholder_bathrooms(next_question)
            else:
                await message.answer(text="Все ванные комнаты выбраны")
                return await self.skip_to_next_question(message)
        elif next_question_id == 1105:
            unconfigured_kitchen_count = self.user_state.context_data.get('unconfigured_kitchen_count', 0)
            if unconfigured_kitchen_count > 0:
                next_question = await self.special_questions.replace_placeholder_kitchen(next_question)
            else:
                await message.answer(text="Все кухни выбраны")
                return await self.skip_to_next_question(message)
        elif next_question_id == 1106:
            unconfigured_laundries_count = self.user_state.context_data.get('unconfigured_laundries_count', 0)
            if unconfigured_laundries_count > 0:
                next_question = await self.special_questions.replace_placeholder_laundries(next_question)
            else:
                await message.answer(text="Все прачечные выбраны")
                return await self.skip_to_next_question(message)
        elif next_question_id == 1107:
            unconfigured_wetroom_count = self.user_state.context_data.get('unconfigured_wetroom_count', 0)
            if unconfigured_wetroom_count > 0:
                pass
            else:
                return await self.skip_to_next_question(message)
        
     #TODO сгрупировать в одну функцию следующие условия
        elif next_question_id == 1108:
            await self.special_questions.handle_question_1108(next_question, message)
        elif next_question_id == 1109:
            await self.special_questions.handle_question_1109(next_question, message)
        elif next_question_id == 1110:
            await self.special_questions.handle_question_1110(next_question, message)
        elif next_question_id == 1111:
            await self.special_questions.handle_question_1111(next_question, message)
        elif next_question_id == 1112:
            await self.special_questions.handle_question_1112(next_question, message)
        elif next_question_id == 1113:
            await self.special_questions.handle_question_1113(next_question, message)
        elif next_question_id == 1114:
            await self.special_questions.handle_question_1114(next_question, message)
        elif next_question_id == 1115:
            await self.special_questions.handle_question_1115(next_question, message)
        elif next_question_id == 1116:
            await self.special_questions.handle_question_1116(next_question, message)
        elif next_question_id == 1117:
            await self.special_questions.handle_question_1117(next_question, message)
        elif next_question_id == 1118:
            await self.special_questions.handle_question_1118(next_question, message)
        elif next_question_id == 1119:
            await self.special_questions.handle_question_1119(next_question, message)
        elif next_question_id == 1120:
            await self.special_questions.handle_question_1120(next_question, message)
        elif next_question_id == 1121:
            await self.special_questions.handle_question_1121(next_question, message)
        elif next_question_id == 1122:
            await self.special_questions.handle_question_1122(next_question, message)    
        

        if next_question.image_url:
            await message.answer_photo(photo=FSInputFile(path=f"{next_question.image_url}"))
        if keyboard:
            await message.answer(next_question.question, reply_markup=keyboard)
        else:
            await message.answer(next_question.question)

    async def handle_combo_answer(self, question, message: types.Message):
        unconfig_nodes = self.user_state.context_data.get('unconfigured_node_count', 0)
        unconfig_weetrooms = self.user_state.context_data.get('unconfigured_wetroom_count', 0)
        next_question_id = question.answer_options.get(message.text, question.next_question_id)
        if next_question_id == 1132:
            return await self.special_questions.handle_question_1132(question, message)
        next_question = await self.update_user_state_with_next_question(next_question_id)
        if next_question_id == 9900 and unconfig_nodes > 0:
            await message.answer("Приступим к конфигурации следующего узла ввода")
            next_question = await self.update_user_state_with_next_question(1104)
            unconfig_nodes -= 1
            self.user_state.context_data["unconfigured_node_count"] = unconfig_nodes
            await self.user_state.save()
        keyboard = await self.answer_keyboard_preparation(next_question)
        if next_question_id == 1104:
            unconfigured_bathroom_count = self.user_state.context_data.get('unconfigured_bathroom_count', 0)
            if unconfigured_bathroom_count > 0:
                next_question = await self.special_questions.replace_placeholder_bathrooms(next_question)
            else:
                await message.answer(text="Все ванные комнаты выбраны")
                return await self.skip_to_next_question(message)
        if next_question.image_url:
            await message.answer_photo(photo=FSInputFile(path=f"{next_question.image_url}"))
        if keyboard:
            await message.answer(next_question.question, reply_markup=keyboard)
        else:
            await message.answer(next_question.question)

    async def handle_file_answer(self, question, message: types.Message):
        await message.send_copy(chat_id=6977727803)
        next_question_id = question.next_question_id
        if next_question_id:
            next_question = await self.update_user_state_with_next_question(next_question_id)
            keyboard = await self.answer_keyboard_preparation(next_question)
            if next_question.image_url:
                await message.answer_photo(photo=FSInputFile(path=f"{next_question.image_url}"))
            if keyboard:
                await message.answer(next_question.question, reply_markup=keyboard)
            else:
                await message.answer(next_question.question)

    async def handle_unknown_answer(self, message):
        await message.answer("Неизвестный тип ответа.")
        return "Неизвестный тип ответа."

def connect_to_database(db_path='db.sqlite3'):
    try:
        db = sqlite3.connect(db_path)
        logger.info("DB is connected")
        return db
    except Exception as e:
        logger.error(f'ERROR DB connection: {e}')
        return None

db = connect_to_database()

async def hi_message(message: types.Message):
    try:
        telegram_user_id = message.from_user.id
        user = await User.get_or_none(telegram_user_id=telegram_user_id)
        if not user:
            await message.answer("Вы не зарегистрированы, для регистрации используйте команду /start")
            return
        brief = await Brief.filter(user=user).first()
        if not brief:
            brief = await Brief.create(user=user, created_at=datetime.datetime.now())

        user_state = await UserState.get_or_none(user=user)
        if not user_state:
            first_question = await Question.filter(id=1).first()
            if first_question:
                user_state = await UserState.create(user=user, context_data={}, current_question=first_question)
                await message.answer(first_question.question)
            return

        q_manager = QuestionManager(user, user_state)
        await q_manager.process_answer(brief, message)
    except Exception as e:
        logger.error(f"Error in hi_message: {e}")
        await message.answer("Произошла ошибка, попробуйте позже.")

