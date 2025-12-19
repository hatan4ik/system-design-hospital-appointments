from .config import settings
import asyncpg

async def get_db_connection():
    return await asyncpg.connect(dsn=settings.DB_DSN)