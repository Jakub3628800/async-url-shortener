"""Database schema definitions for raw SQL queries."""

# SQL schema for short_urls table
CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS short_urls (
        id SERIAL PRIMARY KEY,
        url_key VARCHAR(255) UNIQUE NOT NULL,
        target VARCHAR(2048) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
    )
"""

# Create index on url_key for faster lookups
CREATE_INDEX_SQL = """
    CREATE INDEX IF NOT EXISTS idx_short_urls_url_key ON short_urls(url_key)
"""

__all__ = ["CREATE_TABLE_SQL", "CREATE_INDEX_SQL"]
