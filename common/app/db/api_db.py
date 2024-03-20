from psycopg import Cursor
from psycopg.rows import dict_row
from common.app.db.db_pool import get_pool_cur
from typing import List
from datetime import datetime


@get_pool_cur
async def save_message(cur: Cursor, message: str):
    cur.row_factory = dict_row
    await cur.execute("""
        INSERT INTO messages (message) VALUES (%s)
        RETURNING id, message, created_at;
    """, (message,))
    return await cur.fetchone()


@get_pool_cur
async def get_all_messages(cur: Cursor) -> List[dict]:
    cur.row_factory = dict_row
    await cur.execute("""
        SELECT message, created_at FROM messages ORDER BY created_at DESC;
    """)
    return await cur.fetchall()


@get_pool_cur
async def clear_db(cur: Cursor):
    # Удаление всех записей из таблиц, начиная с таблицы, не имеющей внешних ключей
    await cur.execute("DELETE FROM messages;")
    await cur.execute("COMMIT;")
