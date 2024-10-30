import logging
from aiogram import Bot, Dispatcher, types
from aiogram.fsm import FSMContext, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.utils import executor

# Установим уровень логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
API_TOKEN = 'YOUR_BOT_API_TOKEN'
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Определяем состояния
class Form(StatesGroup):
    name = State()  # Состояние для имени
    group = State()  # Состояние для группы
    homework_number = State()  # Состояние для номера домашнего задания
    github_link = State()  # Состояние для ссылки на GitHub

@dp.message_handler(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Привет! Ты можешь отправить свое домашнее задание. Напиши свое имя:")
    await Form.name.set()

@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Отлично, теперь выбери свою группу:", reply_markup=group_keyboard())
    await Form.group.set()

def group_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    groups = ['Python 46-01', 'Python 46-02', 'Python 46-03']
    keyboard.add(*groups)
    return keyboard

@dp.message_handler(state=Form.group)
async def process_group(message: types.Message, state: FSMContext):
    if message.text not in ['Python 46-01', 'Python 46-02', 'Python 46-03']:
        await message.answer("Пожалуйста, выбери корректную группу.")
        return
    await state.update_data(group=message.text)
    await message.answer("Теперь введи номер домашнего задания (от 1 до 8):")
    await Form.homework_number.set()

@dp.message_handler(lambda message: not message.text.isdigit() or not (1 <= int(message.text) <= 8), state=Form.homework_number)
async def process_homework_number_invalid(message: types.Message):
    await message.answer("Номер домашнего задания должен быть числом от 1 до 8. Попробуй еще раз.")

@dp.message_handler(lambda message: message.text.isdigit() and 1 <= int(message.text) <= 8, state=Form.homework_number)
async def process_homework_number(message: types.Message, state: FSMContext):
    await state.update_data(homework_number=message.text)
    await message.answer("Отлично! Теперь вставь ссылку на свой репозиторий GitHub (должна начинаться с 'https://github.com'):")
    await Form.github_link.set()

@dp.message_handler(lambda message: not message.text.startswith('https://github.com'), state=Form.github_link)
async def process_github_link_invalid(message: types.Message):
    await message.answer("Ссылка должна начинаться с 'https://github.com'. Попробуй еще раз.")

@dp.message_handler(lambda message: message.text.startswith('https://github.com'), state=Form.github_link)
async def process_github_link(message: types.Message, state: FSMContext):
    await state.update_data(github_link=message.text)
    user_data = await state.get_data()
    await message.answer(f"Спасибо, {user_data['name']}! Вот твои данные:n"
                         f"Группа: {user_data['group']}n"
                         f"Номер домашнего задания: {user_data['homework_number']}n"
                         f"Ссылка на GitHub: {user_data['github_link']}")
    await state.clear()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
