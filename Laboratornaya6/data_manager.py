from fastapi import FastAPI, HTTPException
import asyncpg
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


# Модель запроса для конвертации
class ConvertRequest(BaseModel):
    currency_name: str
    amount: float



@app.get("/convert")
async def convert_currency(currency_name: str, amount: float):
    conn = await get_db_connection()
    try:
        # Получение курса валюты
        currency = await conn.fetchrow(
            "SELECT rate FROM currencies WHERE currency_name = $1",
            currency_name.upper()
        )
        if not currency:
            raise HTTPException(status_code=404, detail="Валюта не найдена")

        converted_amount = amount * float(currency["rate"])
        return {"converted_amount": round(converted_amount, 2)}
    finally:
        await conn.close()



@app.get("/currencies")
async def get_currencies():
    conn = await get_db_connection()
    try:
        currencies = await conn.fetch("SELECT currency_name, rate FROM currencies")
        return {"currencies": currencies}
    finally:
        await conn.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5002)