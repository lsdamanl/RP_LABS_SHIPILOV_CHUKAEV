from fastapi import FastAPI, HTTPException
import asyncpg
import os
from pydantic import BaseModel

app = FastAPI()


async def get_db_connection():
    return await asyncpg.connect(
        user='postgres',
        password='12345',
        database='RP_LAB_5',
        host='localhost',
        port=5432
    )


# Модели запросов
class CurrencyLoadRequest(BaseModel):
    currency_name: str
    rate: float


class CurrencyUpdateRequest(BaseModel):
    currency_name: str
    new_rate: float


class CurrencyDeleteRequest(BaseModel):
    currency_name: str


# Эндпоинт для добавления валюты
@app.post("/load")
async def load_currency(request: CurrencyLoadRequest):
    conn = await get_db_connection()
    try:
        # ПРоверка, есть ли валюта
        existing = await conn.fetchrow(
            "SELECT * FROM currencies WHERE currency_name = $1",
            request.currency_name.upper()
        )
        if existing:
            raise HTTPException(status_code=400, detail="Валюта уже существует")

        # Добавление валюты
        await conn.execute(
            "INSERT INTO currencies (currency_name, rate) VALUES ($1, $2)",
            request.currency_name.upper(), request.rate
        )
        return {"status": "OK"}
    finally:
        await conn.close()



@app.post("/update_currency")
async def update_currency(request: CurrencyUpdateRequest):
    conn = await get_db_connection()
    try:
        # Проверка, есть ли валюта
        existing = await conn.fetchrow(
            "SELECT * FROM currencies WHERE currency_name = $1",
            request.currency_name.upper()
        )
        if not existing:
            raise HTTPException(status_code=404, detail="Валюта не найдена")

        # Обновление курса
        await conn.execute(
            "UPDATE currencies SET rate = $1 WHERE currency_name = $2",
            request.new_rate, request.currency_name.upper()
        )
        return {"status": "OK"}
    finally:
        await conn.close()



@app.post("/delete")
async def delete_currency(request: CurrencyDeleteRequest):
    conn = await get_db_connection()
    try:
        # Проверка, есть ли валюта
        existing = await conn.fetchrow(
            "SELECT * FROM currencies WHERE currency_name = $1",
            request.currency_name.upper()
        )
        if not existing:
            raise HTTPException(status_code=404, detail="Валюта не найдена")

        # Удаление валюты
        await conn.execute(
            "DELETE FROM currencies WHERE currency_name = $1",
            request.currency_name.upper()
        )
        return {"status": "OK"}
    finally:
        await conn.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5001)