from databases import Database
from pydantic import SecretStr
from typing import Optional
import asyncpg
import os
import asyncio
from contextlib import asynccontextmanager


def load_database_url() -> SecretStr:
    db_port = os.getenv("DB_PORT", 5432)
    db_host = os.getenv("DB_HOST", "localhost")

    db_hostname = f"{db_host}:{db_port}"
    db_name = os.getenv("DB_NAME","postgres")
    db_user = os.getenv("DB_USER","localuser")
    db_password = SecretStr(os.getenv("DB_PASS","password123"))

    db_url = f"postgresql://{db_user}:{db_password.get_secret_value()}@{db_hostname}/{db_name}"
    return SecretStr(db_url)


class DatabaseConnector:

    pool: Optional[asyncpg.Pool] = None

    async def init_pool(self):
       self.pool = await asyncpg.create_pool(dsn=load_database_url().get_secret_value(), min_size=5, max_size=25, loop=asyncio.get_running_loop())

    @asynccontextmanager
    async def connection(self):
        if self.pool is None:
            await self.init_pool()
        async with self.pool.acquire() as conn:
            yield conn

import asyncpg

async def create_db_pool():
    pool = asyncpg.create_pool(dsn=load_database_url().get_secret_value(), min_size=5, max_size=25)
    return pool



