import asyncio
import asyncpg
from shortener.database import load_database_url


async def run_migrations():
    connection = await asyncpg.connect(load_database_url().get_secret_value())
    migration_files = ["create_short_url_table.sql"]
    for filename in migration_files:
        with open(f"database_migrations/{filename}") as sql_file:
            migration = "".join(sql_file.readlines())
            await connection.execute(query=migration)

    await connection.close()


if __name__ == "__main__":
    asyncio.run(run_migrations())
