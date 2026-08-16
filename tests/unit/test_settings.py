from psycopg.conninfo import conninfo_to_dict

from shortener.settings import PostgresSettings


def test_postgres_dsn_escapes_connection_values(monkeypatch) -> None:
    monkeypatch.setenv("DB_HOST", "database.internal")
    monkeypatch.setenv("DB_PORT", "5433")
    monkeypatch.setenv("DB_DATABASE", "url database")
    monkeypatch.setenv("DB_USER", "service user")
    monkeypatch.setenv("DB_PASSWORD", "special ' password")
    monkeypatch.setenv("DB_SSL", "true")

    connection = conninfo_to_dict(PostgresSettings().postgres_dsn)

    assert connection == {
        "dbname": "url database",
        "host": "database.internal",
        "password": "special ' password",
        "port": "5433",
        "sslmode": "require",
        "user": "service user",
    }
