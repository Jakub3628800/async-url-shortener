-- Migration: Create short_urls table
-- This file contains all the SQL required to initialize the database schema

CREATE TABLE IF NOT EXISTS short_urls (
    id SERIAL PRIMARY KEY,
    url_key VARCHAR(255) UNIQUE NOT NULL,
    target VARCHAR(2048) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create index on url_key for faster lookups
CREATE INDEX IF NOT EXISTS idx_short_urls_url_key ON short_urls(url_key);
