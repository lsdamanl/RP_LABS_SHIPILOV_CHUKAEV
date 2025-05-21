import os
import logging
import psycopg2
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import requests
from datetime import datetime

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
        database="finance_bot",
        user="postgres",
        password="12345"
    )


# SQL для создания таблиц (для pgAdmin)
"""
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE operations (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    sum DECIMAL(10, 2) NOT NULL,
    chat_id BIGINT NOT NULL,
    type_operation VARCHAR(10) NOT NULL,
    CONSTRAINT fk_user FOREIGN KEY(chat_id) REFERENCES users(chat_id)
);
"""


# Состояния
class RegistrationStates(StatesGroup):
    waiting_name = State()


class AddOperationStates(StatesGroup):
    waiting_type = State()
    waiting_amount = State()
    waiting_date = State()


class OperationsStates(StatesGroup):
    waiting_currency = State()


# Проверка зарегистрирован ли пользователь
def is_registered(chat_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM users WHERE chat_id = %s", (str(chat_id),))
            return cur.fetchone() is not None


# Получение курса валют
def get_exchange_rate(currency):
    try:
        response = requests.get(f'http://localhost:5000/rate?currency={currency}')
        if response.status_code == 200:
            return response.json()['rate']
        elif response.status_code == 400:
            logger.error(f"Unknown currency requested: {currency}")
        else:
            logger.error(f"Currency server error: {response.status_code}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error connecting to currency server: {e}")
        return None


@dp.message(Command("start"))
async def cmd_start(message: Message):
    commands = ["start", "reg", "add_operation", "operations"]
    await message.answer(
        "Добро пожаловать в финансовый бот! Доступные команды:\n" +
        "\n".join(f"/{cmd}" for cmd in commands)
    )


@dp.message(Command("reg"))
async def cmd_reg(message: Message, state: FSMContext):
    if is_registered(message.chat.id):
        await message.answer("Вы уже зарегистрированы.")
        return

    await message.answer("Введите ваше имя:")
    await state.set_state(RegistrationStates.waiting_name)


@dp.message(RegistrationStates.waiting_name)
async def process_name(message: Message, state: FSMContext):
    name = message.text
    chat_id = message.chat.id

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (chat_id, name) VALUES (%s, %s)",
                    (chat_id, name)
                )
                conn.commit()
        await message.answer(f"Регистрация успешно завершена, {name}!")
    except Exception as e:
        logger.error(f"Registration error: {e}")
        await message.answer("Произошла ошибка при регистрации. Попробуйте позже.")

    await state.clear()


@dp.message(Command("add_operation"))
async def cmd_add_operation(message: Message, state: FSMContext):
    if not is_registered(message.chat.id):
        await message.answer("Вы не зарегистрированы. Используйте команду /reg.")
        return

    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="РАСХОД"))
    builder.add(KeyboardButton(text="ДОХОД"))
    keyboard = builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

    await message.answer("Выберите тип операции:", reply_markup=keyboard)
    await state.set_state(AddOperationStates.waiting_type)


@dp.message(AddOperationStates.waiting_type)
async def process_operation_type(message: Message, state: FSMContext):
    op_type = message.text
    if op_type not in ["РАСХОД", "ДОХОД"]:
        await message.answer("Пожалуйста, выберите тип операции с помощью кнопок.")
        return

    await state.update_data(type_operation=op_type)
    await message.answer("Введите сумму операции в рублях:")
    await state.set_state(AddOperationStates.waiting_amount)


@dp.message(AddOperationStates.waiting_amount)
async def process_operation_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", "."))
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Пожалуйста, введите корректную сумму (положительное число).")
        return

    await state.update_data(sum=amount)
    await message.answer("Введите дату операции в формате ДД.ММ.ГГГГ (или нажмите кнопку для сегодняшней даты):",
                         reply_markup=ReplyKeyboardMarkup(
                             keyboard=[[KeyboardButton(text="Сегодня")]],
                             resize_keyboard=True,
                             one_time_keyboard=True
                         ))
    await state.set_state(AddOperationStates.waiting_date)


@dp.message(AddOperationStates.waiting_date)
async def process_operation_date(message: Message, state: FSMContext):
    date_str = message.text
    if date_str == "Сегодня":
        op_date = datetime.now().date()
    else:
        try:
            op_date = datetime.strptime(date_str, "%d.%m.%Y").date()
        except ValueError:
            await message.answer("Неверный формат даты. Используйте ДД.ММ.ГГГГ или нажмите кнопку 'Сегодня'.")
            return

    data = await state.get_data()
    chat_id = message.chat.id

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO operations (date, sum, chat_id, type_operation) VALUES (%s, %s, %s, %s)",
                    (op_date, data['sum'], chat_id, data['type_operation'])
                )
                conn.commit()
        await message.answer("Операция успешно добавлена!")
    except Exception as e:
        logger.error(f"Error adding operation: {e}")
        await message.answer("Произошла ошибка при добавлении операции. Попробуйте позже.")

    await state.clear()


@dp.message(Command("operations"))
async def cmd_operations(message: Message, state: FSMContext):
    if not is_registered(message.chat.id):
        await message.answer("Вы не зарегистрированы. Используйте команду /reg.")
        return

    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="RUB"))
    builder.add(KeyboardButton(text="EUR"))
    builder.add(KeyboardButton(text="USD"))
    keyboard = builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

    await message.answer("Выберите валюту для отображения операций:", reply_markup=keyboard)
    await state.set_state(OperationsStates.waiting_currency)


@dp.message(OperationsStates.waiting_currency)
async def process_operations_currency(message: Message, state: FSMContext):
    currency = message.text.upper()
    if currency not in ["RUB", "EUR", "USD"]:
        await message.answer("Пожалуйста, выберите валюту с помощью кнопок.")
        return

    chat_id = message.chat.id
    exchange_rate = 1.0

    if currency != "RUB":
        exchange_rate = get_exchange_rate(currency)
        if not exchange_rate:
            await message.answer("Не удалось получить курс валют. Попробуйте позже.")
            await state.clear()
            return

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT date, sum, type_operation FROM operations WHERE chat_id = %s ORDER BY date DESC",
                    (chat_id,)
                )
                operations = cur.fetchall()

        if not operations:
            await message.answer("У вас пока нет операций.")
            await state.clear()
            return

        response = [f"Ваши операции в {currency}:"]
        for op in operations:
            date, amount, op_type = op
            converted_amount = amount / exchange_rate if currency != "RUB" else amount
            response.append(
                f"{date.strftime('%d.%m.%Y')} - {converted_amount:.2f} {currency} - {op_type}"
            )

        await message.answer("\n".join(response))
    except Exception as e:
        logger.error(f"Error getting operations: {e}")
        await message.answer("Произошла ошибка при получении операций. Попробуйте позже.")

    await state.clear()


async def main():
    logger.info("Запуск бота...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())