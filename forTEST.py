if current_question and current_question.answer_options is not None:
                    next_question_id = current_question.answer_options.get(user_answer)
                else:
                    next_question_id = None
                # Переменная для хранения клавиатуры ответа, если она потребуется
                answer_kb = None

                # Переменная для хранения следующего вопроса
                next_question = None

                # Проверяем, есть ли следующий вопрос
                if next_question_id is not None:
                    next_question = await Question.get_or_none(id=next_question_id)

                # Проверяем, нужно ли создать клавиатуру для следующего вопроса
                if next_question and next_question.answer_options:
                    answer_kb = ReplyKeyboardMarkup(
                        resize_keyboard=True,
                        one_time_keyboard=True,
                        keyboard=[
                            [KeyboardButton(text=answer)] for answer in next_question.answer_options.keys()
                        ]
                    )

                # Обновляем состояние пользователя и отправляем сообщение
                if next_question:
                    # Обновляем состояние пользователя с id следующего вопроса
                    user_state.current_question = next_question
                    user_state.context_data = {}  # Обновите, если необходимо
                    await user_state.save()
                    
                    # Отправляем следующий вопрос с клавиатурой или без
                    await callback_query.answer(next_question.question, reply_markup=answer_kb)
                else:
                    # Если следующего вопроса нет, отправляем соответствующее сообщение
                    if not next_question_id:
                        await callback_query.answer("Это был последний вопрос. Спасибо за ваше время!")
                    else:
                        await callback_query.answer("Следующий вопрос не найден.")