from psycopg import Cursor
from common.app.db.db_pool import get_pool_cur


@get_pool_cur
async def init_db(cur: Cursor):
    # Создание необходимых расширений, если они еще не установлены
    await cur.execute("""
    CREATE EXTENSION IF NOT EXISTS pgcrypto;
    """)

    # Создание таблицы зашифрованных сообщений
    await cur.execute("""CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    message TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """)

    await cur.execute("COMMIT;")
