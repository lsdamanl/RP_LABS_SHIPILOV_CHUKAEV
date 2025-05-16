from fastapi import FastAPI, HTTPException
import asyncpg
from pydantic import BaseModel

app = FastAPI()


# Подключение к БД
async def get_db_connection():
    return await asyncpg.connect(
        user='postgres',
        password='12345',
        database='RP_LAB_5',
        host='localhost',
        port=5432
    )


# Модель для запроса
class RoleRequest(BaseModel):
    chat_id: str


# Проверка роли
@app.post("/check_admin")
async def check_admin(request: RoleRequest):
    conn = await get_db_connection()
    try:
        result = await conn.fetchrow(
            "SELECT 1 FROM admins WHERE chat_id = $1", request.chat_id
        )
        return {"is_admin": result is not None}
    finally:
        await conn.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5003)
