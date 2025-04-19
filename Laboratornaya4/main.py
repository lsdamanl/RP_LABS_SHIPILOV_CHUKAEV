import os
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

bot_token = os.getenv('API_TOKEN')
bot = Bot(token=bot_token)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Словарь для валют
currencies = {}

class CurrencyStates(StatesGroup):
    waiting_name = State()
    waiting_rate = State()

@dp.message(Command("start"))
async def start(message: Message):
    logger.info(f"Пользователь {message.from_user.id} начал работу")
    await message.answer("Привет! Для работы с валютами введи /save_currency")

@dp.message(Command("save_currency"))
async def save_start(message: Message, state: FSMContext):
    logger.info(f"Пользователь {message.from_user.id} начал сохранение валюты")
    await message.answer("Введите название валюты (например: EUR, USD, CNY или др.):")
    await state.set_state(CurrencyStates.waiting_name)

@dp.message(CurrencyStates.waiting_name)
async def get_name(message: Message, state: FSMContext):
    logger.info(f"Пользователь ввёл название: {message.text}")
    await state.update_data(name=message.text.upper())
    data = await state.get_data()
    name = data['name']
    await message.answer(f"Теперь введите курс валюты {name} к рублю:")
    await state.set_state(CurrencyStates.waiting_rate)

@dp.message(CurrencyStates.waiting_rate)
async def get_rate(message: Message, state: FSMContext):
    try:
        rate = float(message.text.replace(',', '.'))
        data = await state.get_data()
        currencies[data['name']] = rate
        logger.info(f"Сохранена валюта: {data['name']} = {rate}")
        await message.answer(f"Сохранено: {data['name']} = {rate}")
        await state.clear()
    except ValueError:
        logger.warning("Некорректный курс")
        await message.answer("Ошибка! Введи число:")

async def main():
    logger.info("Запуск бота...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())