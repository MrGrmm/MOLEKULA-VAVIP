# from aiogram import types
# from aiogram.fsm.state import State, StatesGroup
# from aiogram.fsm.context import FSMContext
# from aiogram import Router

# file_router = Router()



# class DocumentUploadState(StatesGroup):
#     waiting_for_document = State()


# @file_router.message(commands=['upload'])
# async def request_document(message: types.Message):
#     await DocumentUploadState.waiting_for_document.set()
#     await message.answer("Please upload a document.")


# async def file_handler(message: types.Message, state: FSMContext):
#     if not message.document:
#         await message.answer("Please send a valid document.")
#         return

#     document = message.document
#     file_path = await document.download(destination_file=f"./downloads/{document.file_name}")

#     # Создание нового объекта FileMetadata и сохранение в базу данных

#     await message.answer("Document has been successfully saved.")
#     await state.clear()

