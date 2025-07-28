import pytest
import os
from unittest.mock import patch
from shortener.settings import PostgresSettings, AppSettings


class TestPostgresSettings:
    def test_default_postgresql_settings(self):
        """Test default PostgreSQL database settings."""
        settings = PostgresSettings()
        assert settings.host == "localhost"
        assert settings.port == 5432
        assert settings.database == "urldatabase"
        assert settings.user == "localuser"
        assert settings.password == "password123"
        assert not settings.ssl
        assert settings.min_size == 5
        assert settings.max_size == 25
        assert settings.timeout == 60.0

    def test_postgres_dsn_property(self):
        """Test postgres_dsn property."""
        settings = PostgresSettings(
            user="testuser",
            password="testpass",
            host="testhost",
            port=5433,
            database="testdb"
        )
        expected_dsn = "postgresql+asyncpg://testuser:testpass@testhost:5433/testdb"
        assert settings.postgres_dsn == expected_dsn

    def test_custom_postgresql_settings(self):
        """Test PostgreSQL settings with custom values."""
        settings = PostgresSettings(
            host="custom_host",
            port=9999,
            database="custom_db",
            user="custom_user",
            password="custom_pass",
            ssl=True,
            min_size=10,
            max_size=50,
            timeout=120.5
        )
        assert settings.host == "custom_host"
        assert settings.port == 9999
        assert settings.database == "custom_db"
        assert settings.user == "custom_user"
        assert settings.password == "custom_pass"
        assert settings.ssl is True
        assert settings.min_size == 10
        assert settings.max_size == 50
        assert settings.timeout == 120.5


class TestAppSettings:
    def test_default_app_settings(self):
        """Test default application settings."""
        settings = AppSettings()
        assert settings.debug is False
        assert settings.title == "URL Shortener API"
        assert settings.description == "API for creating and managing shortened URLs"
        assert settings.version == "1.0.0"
        assert settings.max_url_length == 2048
        assert settings.max_key_length == 50
        assert settings.rate_limit_enabled is False
        assert settings.rate_limit_per_minute == 60

    def test_custom_app_settings(self):
        """Test app settings with custom values."""
        settings = AppSettings(
            debug=True,
            title="Custom API",
            description="Custom Description",
            version="2.0.0",
            max_url_length=4096,
            max_key_length=100,
            rate_limit_enabled=True,
            rate_limit_per_minute=120
        )
        assert settings.debug is True
        assert settings.title == "Custom API"
        assert settings.description == "Custom Description"
        assert settings.version == "2.0.0"
        assert settings.max_url_length == 4096
        assert settings.max_key_length == 100
        assert settings.rate_limit_enabled is True
        assert settings.rate_limit_per_minute == 120

    @patch.dict(os.environ, {"ENV": "production"})
    def test_environment_property_production(self):
        """Test environment property returns production."""
        settings = AppSettings()
        assert settings.environment == "production"

    @patch.dict(os.environ, {"ENV": "DEVELOPMENT"})
    def test_environment_property_case_insensitive(self):
        """Test environment property is case insensitive."""
        settings = AppSettings()
        assert settings.environment == "development"

    def test_environment_property_default(self):
        """Test environment property default value."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove ENV if it exists
            if "ENV" in os.environ:
                del os.environ["ENV"]
            settings = AppSettings()
            assert settings.environment == "development"

    @patch.dict(os.environ, {"ENV": "testing"})
    def test_environment_property_custom(self):
        """Test environment property with custom value."""
        settings = AppSettings()
        assert settings.environment == "testing"

    def test_boolean_field_values(self):
        """Test that boolean fields accept various boolean values."""
        # Test direct boolean values
        settings_true = AppSettings(debug=True, rate_limit_enabled=True)
        assert settings_true.debug is True
        assert settings_true.rate_limit_enabled is True

        settings_false = AppSettings(debug=False, rate_limit_enabled=False)
        assert settings_false.debug is False
        assert settings_false.rate_limit_enabled is False