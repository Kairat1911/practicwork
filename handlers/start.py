from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher import State, StatesGroup
from aiogram.utils import markdown as md
from database.db import save_homework

# Определяем состояния
class HomeworkForm(StatesGroup):
    name = State()
    group_name = State()
    homework_number = State()
    github_link = State()

# Обработчик команды /start
async def cmd_start(message: types.Message):
    await message.answer("Привет! Отправь команду /homework для отправки домашнего задания.")

# Начинает диалог для отправки домашнего задания
async def process_homework(message: types.Message):
    await HomeworkForm.name.set()
    await message.answer("Введите ваше имя:")

# Обработчик имени
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await HomeworkForm.group_name.set()
    await message.answer("Выберите вашу группу:", reply_markup=group_keyboard())

# Обработчик группы
async def process_group_name(message: types.Message, state: FSMContext):
    await state.update_data(group_name=message.text)
    await HomeworkForm.homework_number.set()
    await message.answer("Введите номер домашнего задания (от 1 до 8):")

# Обработчик номера задания
async def process_homework_number(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or not (1 <= int(message.text) <= 8):
        await message.answer("Пожалуйста, введите корректный номер задания (от 1 до 8).")
        return
    await state.update_data(homework_number=int(message.text))
    await HomeworkForm.github_link.set()
    await message.answer("Введите ссылку на ваш GitHub репозиторий (должна начинаться с 'https://github.com'):")

# Обработчик ссылки
async def process_github_link(message: types.Message, state: FSMContext):
    if not message.text.startswith('https://github.com'):
        await message.answer("Ссылка должна начинаться с 'https://github.com'. Повторите ввод:")
        return
    data = await state.get_data()
    await save_homework(data['name'], data['group_name'], data['homework_number'], message.text)
    await message.answer("Ваше домашнее задание успешно сохранено!")
    await state.finish()

# Функция для создания кнопок для выбора группы
def group_keyboard():
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    groups = ['Python 46-01', 'Python 46-02', 'Python 46-03']
    buttons = [KeyboardButton(group) for group in groups]
    keyboard.add(*buttons)
    return keyboard