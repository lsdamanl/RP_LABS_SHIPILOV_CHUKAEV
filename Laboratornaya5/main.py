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
        await message.answer(f"Сохранено: 1 {data['name']} = {rate} ₽")
        await state.clear()
        await message.answer("Для конвертации валюты введи /convert")
    except ValueError:
        logger.warning("Некорректный курс")
        await message.answer("Ошибка! Введи число:")


# Задание 2
class ConvertStates(StatesGroup):
    waiting_currency_name = State()
    waiting_amount = State()


@dp.message(Command("convert"))
async def convert_start(message: Message, state: FSMContext):
    logger.info(f"Пользователь {message.from_user.id} начал конвертацию")
    if not currencies:
        await message.answer("Нет сохраненных валют. Сначала добавьте валюту через /save_currency")
        return


    currencies_list = "\n".join([f"• {name}: {rate} ₽" for name, rate in currencies.items()])
    await message.answer(f"Введите название валюты для конвертации \n\n Список доступных валют:\n{currencies_list}")
    await state.set_state(ConvertStates.waiting_currency_name)


@dp.message(ConvertStates.waiting_currency_name)
async def get_currency_for_conversion(message: Message, state: FSMContext):
    currency_name = message.text.upper()
    if currency_name not in currencies:
        await message.answer(f"Валюта {currency_name} не найдена. Введите одно из: {', '.join(currencies.keys())}")
        return

    logger.info(f"Пользователь выбрал валюту: {currency_name}")
    await state.update_data(currency_name=currency_name)
    await message.answer(f"Введите сумму в {currency_name} для конвертации в рубли:")
    await state.set_state(ConvertStates.waiting_amount)


@dp.message(ConvertStates.waiting_amount)
async def convert_currency(message: Message, state: FSMContext):
    try:
        amount = float(message.text.replace(',', '.'))
        data = await state.get_data()
        currency_name = data['currency_name']
        rate = currencies[currency_name]

        result = amount * rate
        logger.info(f"Конвертация: {amount} {currency_name} = {result} ₽")
        await message.answer(f"{amount} {currency_name} = {result:.2f} ₽ по курсу {rate} ₽")
        await state.clear()
    except ValueError:
        logger.warning("Некорректная сумма для конвертации")
        await message.answer("Ошибка! Введите число:")


async def main():
    logger.info("Запуск бота...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())