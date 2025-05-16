import os
import logging
import psycopg2
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

bot_token = os.getenv("API_TOKEN")
bot = Bot(token=bot_token)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Подключение к БД
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="RP_LAB_5",
        user="postgres",
        password="12345"
    )


# Состояния
class ManageCurrencyStates(StatesGroup):
    waiting_action = State()
    waiting_currency_name = State()
    waiting_new_rate = State()


class ConvertStates(StatesGroup):
    waiting_currency_name = State()
    waiting_amount = State()


# Проверка администратора
def is_admin(chat_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM admins WHERE chat_id = %s", (str(chat_id),))
            return cur.fetchone() is not None



@dp.message(Command("start"))
async def cmd_start(message: Message):
    commands = ["start", "get_currencies", "convert"]
    if is_admin(message.chat.id):
        commands.insert(1, "manage_currency")
    await message.answer("Добро пожаловать! Доступные команды:\n" + "\n".join(f"/{cmd}" for cmd in commands))



@dp.message(Command("get_currencies"))
async def cmd_get_currencies(message: Message):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT currency_name, rate FROM currencies")
            rows = cur.fetchall()

    if not rows:
        await message.answer("Нет сохранённых валют.")
    else:
        text = "\n".join([f"{name}: {rate} ₽" for name, rate in rows])
        await message.answer("Список валют:\n" + text)



@dp.message(Command("convert"))
async def cmd_convert(message: Message, state: FSMContext):
    await message.answer("Введите название валюты:")
    await state.set_state(ConvertStates.waiting_currency_name)


@dp.message(ConvertStates.waiting_currency_name)
async def process_currency_name(message: Message, state: FSMContext):
    currency = message.text.upper()
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT rate FROM currencies WHERE currency_name = %s", (currency,))
            result = cur.fetchone()

    if not result:
        await message.answer("Валюта не найдена. Попробуйте ещё раз.")
        return
    await state.update_data(currency_name=currency, rate=float(result[0]))
    await message.answer(f"Введите сумму в {currency}:")
    await state.set_state(ConvertStates.waiting_amount)


@dp.message(ConvertStates.waiting_amount)
async def process_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Введите корректное число.")
        return
    data = await state.get_data()
    rubles = amount * data["rate"]
    await message.answer(f"{amount} {data['currency_name']} = {rubles:.2f} ₽")
    await state.clear()


# Команда /manage_currency
@dp.message(Command("manage_currency"))
async def cmd_manage_currency(message: Message, state: FSMContext):
    if not is_admin(message.chat.id):
        await message.answer("Нет доступа к команде.")
        return

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Добавить валюту"), KeyboardButton(text="Удалить валюту"),
                   KeyboardButton(text="Изменить курс валюты")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Выберите действие:", reply_markup=keyboard)
    await state.set_state(ManageCurrencyStates.waiting_action)


@dp.message(ManageCurrencyStates.waiting_action)
async def process_action(message: Message, state: FSMContext):
    action = message.text
    if action not in ["Добавить валюту", "Удалить валюту", "Изменить курс валюты"]:
        await message.answer("Неверный выбор. Повторите.")
        return

    await state.update_data(action=action)
    await message.answer("Введите название валюты:")
    await state.set_state(ManageCurrencyStates.waiting_currency_name)


@dp.message(ManageCurrencyStates.waiting_currency_name)
async def process_currency_name_admin(message: Message, state: FSMContext):
    name = message.text.upper()
    data = await state.get_data()
    action = data["action"]

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT rate FROM currencies WHERE currency_name = %s", (name,))
            result = cur.fetchone()

    if action == "Добавить валюту":
        if result:
            await message.answer("Данная валюта уже существует.")
            await state.clear()
        else:
            await state.update_data(currency_name=name)
            await message.answer("Введите курс к рублю:")
            await state.set_state(ManageCurrencyStates.waiting_new_rate)

    elif action == "Удалить валюту":
        if not result:
            await message.answer("Валюта не найдена.")
        else:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM currencies WHERE currency_name = %s", (name,))
                    conn.commit()
            await message.answer(f"Валюта {name} удалена.")
        await state.clear()

    elif action == "Изменить курс валюты":
        if not result:
            await message.answer("Валюта не найдена.")
            await state.clear()
        else:
            await state.update_data(currency_name=name)
            await message.answer("Введите новый курс:")
            await state.set_state(ManageCurrencyStates.waiting_new_rate)


@dp.message(ManageCurrencyStates.waiting_new_rate)
async def process_new_rate(message: Message, state: FSMContext):
    try:
        rate = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Введите корректное число.")
        return

    data = await state.get_data()
    name = data["currency_name"]
    action = data["action"]

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            if action == "Добавить валюту":
                cur.execute("INSERT INTO currencies (currency_name, rate) VALUES (%s, %s)", (name, rate))
                await message.answer(f"Валюта {name} успешно добавлена.")
            elif action == "Изменить курс валюты":
                cur.execute("UPDATE currencies SET rate = %s WHERE currency_name = %s", (rate, name))
                await message.answer(f"Курс валюты {name} обновлён.")
            conn.commit()
    await state.clear()



async def main():
    logger.info("Запуск бота...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
