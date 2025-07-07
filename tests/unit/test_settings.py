import os
from unittest.mock import patch

from shortener.settings import DatabaseSettings, AppSettings


class TestDatabaseSettings:
    def test_default_settings(self):
        settings = DatabaseSettings()
        assert settings.type == "sqlite"
        assert settings.sqlite_path == "shortener.db"
        assert settings.host == "localhost"
        assert settings.port == 5432
        assert settings.database == "urldatabase"
        assert settings.user == "localuser"
        assert settings.password == "password123"
        assert settings.ssl is False

    def test_sqlite_database_url(self):
        settings = DatabaseSettings(type="sqlite", sqlite_path="test.db")
        assert settings.database_url == "sqlite+aiosqlite:///test.db"

    def test_postgresql_database_url(self):
        settings = DatabaseSettings(
            type="postgresql",
            host="db.example.com",
            port=5433,
            database="testdb",
            user="testuser",
            password="testpass"
        )
        expected = "postgresql+asyncpg://testuser:testpass@db.example.com:5433/testdb"
        assert settings.database_url == expected

    def test_postgres_dsn_property(self):
        settings = DatabaseSettings(
            host="db.example.com",
            port=5433,
            database="testdb",
            user="testuser",
            password="testpass"
        )
        expected = "postgresql+asyncpg://testuser:testpass@db.example.com:5433/testdb"
        assert settings.postgres_dsn == expected

    @patch.dict(os.environ, {
        'DB_TYPE': 'postgresql',
        'DB_HOST': 'prod.db.com',
        'DB_PORT': '5432',
        'DB_DATABASE': 'proddb',
        'DB_USER': 'produser',
        'DB_PASSWORD': 'prodpass',
        'DB_SSL': 'true'
    })
    def test_environment_variable_loading(self):
        settings = DatabaseSettings()
        assert settings.type == "postgresql"
        assert settings.host == "prod.db.com"
        assert settings.port == 5432
        assert settings.database == "proddb"
        assert settings.user == "produser"
        assert settings.password == "prodpass"
        assert settings.ssl is True

    def test_case_insensitive_type_handling(self):
        settings_upper = DatabaseSettings(type="SQLITE")
        settings_lower = DatabaseSettings(type="sqlite")
        settings_mixed = DatabaseSettings(type="SQLite")

        assert settings_upper.database_url.startswith("sqlite+aiosqlite:")
        assert settings_lower.database_url.startswith("sqlite+aiosqlite:")
        assert settings_mixed.database_url.startswith("sqlite+aiosqlite:")

    def test_connection_pool_settings(self):
        settings = DatabaseSettings(min_size=10, max_size=50, timeout=120.0)
        assert settings.min_size == 10
        assert settings.max_size == 50
        assert settings.timeout == 120.0

    def test_custom_sqlite_path(self):
        custom_path = "/tmp/custom.db"
        settings = DatabaseSettings(type="sqlite", sqlite_path=custom_path)
        assert settings.database_url == f"sqlite+aiosqlite:///{custom_path}"


class TestAppSettings:
    def test_default_settings(self):
        settings = AppSettings()
        assert settings.debug is False
        assert settings.title == "URL Shortener API"
        assert settings.description == "API for creating and managing shortened URLs"
        assert settings.version == "1.0.0"
        assert settings.max_url_length == 2048
        assert settings.max_key_length == 50
        assert settings.rate_limit_enabled is False
        assert settings.rate_limit_per_minute == 60

    @patch.dict(os.environ, {
        'APP_DEBUG': 'true',
        'APP_TITLE': 'Custom API',
        'APP_DESCRIPTION': 'Custom Description',
        'APP_VERSION': '2.0.0',
        'APP_MAX_URL_LENGTH': '4096',
        'APP_MAX_KEY_LENGTH': '100',
        'APP_RATE_LIMIT_ENABLED': 'true',
        'APP_RATE_LIMIT_PER_MINUTE': '120'
    })
    def test_environment_variable_loading(self):
        settings = AppSettings()
        assert settings.debug is True
        assert settings.title == "Custom API"
        assert settings.description == "Custom Description"
        assert settings.version == "2.0.0"
        assert settings.max_url_length == 4096
        assert settings.max_key_length == 100
        assert settings.rate_limit_enabled is True
        assert settings.rate_limit_per_minute == 120

    @patch.dict(os.environ, {'ENV': 'production'})
    def test_environment_property_production(self):
        settings = AppSettings()
        assert settings.environment == "production"

    @patch.dict(os.environ, {'ENV': 'DEVELOPMENT'})
    def test_environment_property_case_insensitive(self):
        settings = AppSettings()
        assert settings.environment == "development"

    @patch.dict(os.environ, {}, clear=True)
    def test_environment_property_default(self):
        # Clear ENV variable to test default
        if 'ENV' in os.environ:
            del os.environ['ENV']
        settings = AppSettings()
        assert settings.environment == "development"

    def test_custom_url_limits(self):
        settings = AppSettings(max_url_length=1024, max_key_length=25)
        assert settings.max_url_length == 1024
        assert settings.max_key_length == 25

    def test_rate_limiting_configuration(self):
        settings = AppSettings(
            rate_limit_enabled=True,
            rate_limit_per_minute=30
        )
        assert settings.rate_limit_enabled is True
        assert settings.rate_limit_per_minute == 30

    @patch.dict(os.environ, {
        'APP_DEBUG': 'false',
        'APP_RATE_LIMIT_ENABLED': 'false'
    })
    def test_boolean_environment_variables(self):
        settings = AppSettings()
        assert settings.debug is False
        assert settings.rate_limit_enabled is False

    @patch.dict(os.environ, {
        'APP_DEBUG': '1',
        'APP_RATE_LIMIT_ENABLED': 'yes'
    })
    def test_boolean_environment_variables_alternative_values(self):
        settings = AppSettings()
        # Note: pydantic-settings handles these conversions
        assert settings.debug is True
        assert settings.rate_limit_enabled is True
