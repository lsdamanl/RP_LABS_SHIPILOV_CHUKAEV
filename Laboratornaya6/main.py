import os
import logging
import httpx
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

bot_token = os.getenv("API_TOKEN")
bot = Bot(token=bot_token)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URL микросервисов
CURRENCY_MANAGER_URL = "http://localhost:5001"
DATA_MANAGER_URL = "http://localhost:5002"
ROLE_MANAGER_URL = "http://localhost:5003"


# Состояния
class ManageCurrencyStates(StatesGroup):
    waiting_action = State()
    waiting_currency_name = State()
    waiting_new_rate = State()


class ConvertStates(StatesGroup):
    waiting_currency_name = State()
    waiting_amount = State()


async def is_admin(chat_id: int) -> bool:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{ROLE_MANAGER_URL}/check_admin",
                json={"chat_id": str(chat_id)}
            )
            return response.status_code == 200 and response.json().get("is_admin", False)
    except Exception as e:
        logger.error(f"Ошибка при обращении к role-manager: {e}")
        return False


@dp.message(Command("start"))
async def cmd_start(message: Message):
    commands = ["start", "get_currencies", "convert"]
    if await is_admin(message.chat.id):
        commands.insert(1, "manage_currency")
    await message.answer("Добро пожаловать! Доступные команды:\n" + "\n".join(f"/{cmd}" for cmd in commands))


@dp.message(Command("get_currencies"))
async def cmd_get_currencies(message: Message):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DATA_MANAGER_URL}/currencies")
            if response.status_code != 200:
                await message.answer("Ошибка при получении списка валют.")
                return

            currencies = response.json().get("currencies", [])
            if not currencies:
                await message.answer("Нет сохранённых валют.")
            else:
                text = "\n".join([f"{row['currency_name']}: {row['rate']} ₽" for row in currencies])
                await message.answer("Список валют:\n" + text)
    except Exception as e:
        logger.error(f"Ошибка в /get_currencies: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")


@dp.message(Command("convert"))
async def cmd_convert(message: Message, state: FSMContext):
    await message.answer("Введите название валюты:")
    await state.set_state(ConvertStates.waiting_currency_name)


@dp.message(ConvertStates.waiting_currency_name)
async def process_currency_name(message: Message, state: FSMContext):
    currency = message.text.upper()
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{DATA_MANAGER_URL}/convert",
                params={"currency_name": currency, "amount": 1.0}
            )
            if response.status_code != 200:
                await message.answer("Валюта не найдена. Попробуйте ещё раз.")
                return

            rate = response.json().get("converted_amount")
            await state.update_data(currency_name=currency, rate=rate)
            await message.answer(f"Введите сумму в {currency}:")
            await state.set_state(ConvertStates.waiting_amount)
    except Exception as e:
        logger.error(f"Ошибка в process_currency_name: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")


@dp.message(ConvertStates.waiting_amount)
async def process_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Введите корректное число.")
        return

    data = await state.get_data()
    rubles = amount * float(data["rate"])
    await message.answer(f"{amount} {data['currency_name']} = {rubles:.2f} ₽")
    await state.clear()


@dp.message(Command("manage_currency"))
async def cmd_manage_currency(message: Message, state: FSMContext):
    if not await is_admin(message.chat.id):
        await message.answer("Нет доступа к команде.")
        return

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Добавить валюту")],
            [KeyboardButton(text="Удалить валюту")],
            [KeyboardButton(text="Изменить курс валюты")]
        ],
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

    try:
        if action == "Добавить валюту":
            await state.update_data(currency_name=name)
            await message.answer("Введите курс к рублю:")
            await state.set_state(ManageCurrencyStates.waiting_new_rate)

        elif action == "Удалить валюту":
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{CURRENCY_MANAGER_URL}/delete",
                    json={"currency_name": name}
                )
                if response.status_code == 200:
                    await message.answer(f"Валюта {name} удалена.")
                else:
                    await message.answer("Валюта не найдена или произошла ошибка.")
            await state.clear()

        elif action == "Изменить курс валюты":
            await state.update_data(currency_name=name)
            await message.answer("Введите новый курс:")
            await state.set_state(ManageCurrencyStates.waiting_new_rate)

    except Exception as e:
        logger.error(f"Ошибка в process_currency_name_admin: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")
        await state.clear()


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

    try:
        async with httpx.AsyncClient() as client:
            if action == "Добавить валюту":
                response = await client.post(
                    f"{CURRENCY_MANAGER_URL}/load",
                    json={"currency_name": name, "rate": rate}
                )
                if response.status_code == 200:
                    await message.answer(f"Валюта {name} успешно добавлена.")
                else:
                    await message.answer("Ошибка: валюта уже существует.")

            elif action == "Изменить курс валюты":
                response = await client.post(
                    f"{CURRENCY_MANAGER_URL}/update_currency",
                    json={"currency_name": name, "new_rate": rate}
                )
                if response.status_code == 200:
                    await message.answer(f"Курс валюты {name} обновлён.")
                else:
                    await message.answer("Ошибка: валюта не найдена.")

        await state.clear()
    except Exception as e:
        logger.error(f"Ошибка в process_new_rate: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")
        await state.clear()


async def main():
    logger.info("Запуск бота...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
