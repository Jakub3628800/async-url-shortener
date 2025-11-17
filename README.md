# Async URL Shortener

[![CI](https://github.com/Jakub3628800/async-url-shortener/actions/workflows/master.yml/badge.svg?branch=master)](https://github.com/Jakub3628800/async-url-shortener/actions/workflows/master.yml)
![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Jakub3628800/async-url-shortener/master.svg)

A lean, high-performance URL shortener service built with **Starlette** (pure ASGI) and **psycopg3** (async PostgreSQL). Zero unnecessary dependencies.

## Features

- 🚀 **Async-first** - Pure async/await throughout with psycopg3
- 🔧 **Minimal stack** - Only 3 production dependencies
- 📝 **Raw SQL** - Explicit SQL queries, no ORM overhead
- 🗄️ **PostgreSQL** - Async connection pooling with psycopg3
- 🧪 **Well tested** - 17 comprehensive tests
- 🐳 **Containerized** - Docker & Docker Compose support
- ✨ **Clean code** - ~1000 lines, organized structure

## Technology Stack

**Production:**
- `starlette` - Lightweight ASGI web framework
- `psycopg[binary]` - Async PostgreSQL driver
- `uvicorn[standard]` - ASGI server

**Development:**
- `pytest` - Testing framework
- `testcontainers[postgres]` - PostgreSQL test containers
- `httpx` - Async HTTP client for testing

## Quick Start

### Prerequisites
- Python 3.14+
- PostgreSQL 12+
- Docker (optional, for easier setup)

### Development Setup

1. **Clone and install:**
```bash
git clone https://github.com/Jakub3628800/async-url-shortener.git
cd async-url-shortener
```

2. **Configure environment (optional):**
```bash
# Create .env file with your settings (all have sensible defaults)
cat > .env << EOF
DB_HOST=localhost
DB_PORT=5432
DB_DATABASE=urldatabase
DB_USER=localuser
DB_PASSWORD=password123
DB_SSL=false
APPLICATION_HOST=0.0.0.0
APPLICATION_PORT=8000
EOF
```

3. **Run the application:**
```bash
# With Docker Compose (recommended)
make run

# Or manually with PostgreSQL running
uv run -m shortener.app
```

### Running Tests

```bash
# Run all tests
make test

# Tests use mocked database by default
# To run full integration tests with real PostgreSQL containers,
# testcontainers will automatically start a test database
```

### Database Migrations

```bash
# Run migrations (create schema)
make migrate

# Drop all tables
make un-migrate
```

## API Endpoints

### Basic
- `GET /ping` - Health check (returns `{"ping": "pong"}`)
- `GET /status` - Database health check (returns `{"db_up": "true"}`)

### URL Shortening (CRUD)
- `POST /urls/` - Create short URL
  ```json
  {"short_url": "abc", "target_url": "https://example.com"}
  ```
- `GET /urls/` - List all short URLs
- `GET /urls/{short_url}` - Get specific URL mapping
- `PUT /urls/{short_url}` - Update target URL
- `DELETE /urls/{short_url}` - Delete URL mapping

### Redirect
- `GET /{short_url}` - Redirect to target URL (HTTP 307)

## Configuration

All configuration uses environment variables with sensible defaults:

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | localhost | PostgreSQL host |
| `DB_PORT` | 5432 | PostgreSQL port |
| `DB_DATABASE` | urldatabase | Database name |
| `DB_USER` | localuser | Database user |
| `DB_PASSWORD` | password123 | Database password |
| `DB_SSL` | false | Enable SSL for DB connection |
| `DB_MIN_SIZE` | 5 | Connection pool minimum size |
| `DB_MAX_SIZE` | 25 | Connection pool maximum size |
| `APPLICATION_HOST` | 0.0.0.0 | Server bind address |
| `APPLICATION_PORT` | 8000 | Server port |

## Project Structure

```
shortener/
├── app.py           # Application setup, routing, lifespan
├── database.py      # PostgreSQL connection pool
├── actions.py       # Business logic & database operations
├── views.py         # All HTTP endpoint handlers
├── settings.py      # Configuration management
├── models.py        # SQL schema definitions
└── migration.sql    # Database schema
```

## Development

### Run tests with coverage
```bash
make test
```

### Format & lint code
```bash
# Pre-commit runs automatically on git commit
# Or manually:
pre-commit run --all-files
```

### Update dependencies
```bash
make deps
```

## Design Decisions

### No FastAPI/ORM
This project intentionally uses **raw Starlette** and **raw SQL**:
- Starlette provides just what we need: routing, middleware, ASGI
- Raw SQL is explicit, debuggable, and performant
- No magic, no hidden queries, no unnecessary abstractions

### Minimal Dependencies
Only 3 production dependencies (plus their transitive deps):
- `starlette` - routing, request/response handling
- `psycopg[binary]` - PostgreSQL driver with binary libpq
- `uvicorn[standard]` - ASGI server with C extensions

### Dataclasses Over Pydantic
Configuration uses Python's built-in `dataclasses` instead of Pydantic:
- No schema validation overhead
- Manual environment variable loading
- Clear, simple code

## Docker

### Build image
```bash
docker build -t url-shortener .
```

### Run with Docker Compose
```bash
docker compose up
```

### Environment variables in Docker
```bash
docker run -e DB_HOST=postgres -e DB_USER=localuser url-shortener
```

## Troubleshooting

### Port already in use
```bash
# Change port
APPLICATION_PORT=8001 make run
```

### Database connection failed
```bash
# Check PostgreSQL is running
psql -h localhost -U localuser -d urldatabase -c "SELECT 1"
```

### Tests failing
```bash
# Make sure no existing connections to test database
# testcontainers will auto-cleanup after tests
make test
```

## Performance

- **Async throughout** - All I/O operations are non-blocking
- **Connection pooling** - psycopg3 AsyncConnectionPool manages database connections
- **Pre-compiled regex** - URL validation uses pre-compiled patterns
- **No ORM overhead** - Raw parameterized queries

## License

MIT

## Contributing

Pull requests welcome! Please ensure:
- `make test` passes
- `pre-commit run --all-files` passes
- Code follows existing style
