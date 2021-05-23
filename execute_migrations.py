from shortener.database import postgres_connection, set_up_postgres_connection, tear_down_postgres_connection
import asyncio


async def run_migrations():
    await set_up_postgres_connection()
    migration_files = ["create_short_url_table.sql"]
    for filename in migration_files:
        with open(f"database_migrations/{filename}") as sql_file:
            migration = "".join(sql_file.readlines())
            await postgres_connection.execute(query=migration)

    await tear_down_postgres_connection()


if __name__ == "__main__":
    asyncio.run(run_migrations())
