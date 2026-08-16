# AGENTS.md

## Project overview

This repository contains a small async URL-shortening API. It uses:

- Python 3.14
- Starlette for ASGI routing and HTTP primitives
- psycopg 3 and `psycopg-pool` for async PostgreSQL access
- Raw, parameterized SQL instead of an ORM
- `uv` for dependency and lockfile management
- pre-commit for verification

Keep the implementation small and explicit. Every new dependency requires user approval and must be vetted for necessity, maintenance, security, and licensing. Do not introduce a larger framework, ORM, or validation library unless the user explicitly requests it.

## Important files

- `shortener/app.py`: application construction, route ordering, lifespan, schema initialization, and exception handlers
- `shortener/views.py`: HTTP handlers and request validation
- `shortener/actions.py`: database operations and application-level exceptions
- `shortener/database.py`: async connection-pool wrapper and global database accessor
- `shortener/settings.py`: `.env` loading and dataclass-based settings
- `shortener/models.py`: schema SQL executed at application startup
- `shortener/migration.sql`: equivalent schema for manual execution
- `tests/conftest.py`: mocked HTTP-test client and PostgreSQL Testcontainers fixtures
- `compose.yaml`: local PostgreSQL and full application stack
- `pyproject.toml`: Python version, dependencies, scripts, and pytest settings
- `.pre-commit-config.yaml`: formatting, linting, typing, lockfile, Docker, and workflow checks

## Setup and common commands

Install development dependencies with `uv sync --extra dev`.

Main Makefile targets:

| Command | Purpose |
| --- | --- |
| `make test` | Run the complete pytest suite |
| `make run` | Start PostgreSQL as a Compose sidecar, run the app locally, then stop the sidecar |
| `make deps` | Upgrade dependencies and regenerate `uv.lock` |
| `make migrate` | Start the PostgreSQL sidecar and apply `shortener/migration.sql` with `psql` |
| `make un-migrate` | Start the PostgreSQL sidecar and drop the application table with `psql` |

Run a specific test file or test:

```bash
uv run --extra dev pytest tests/unit/test_views.py
uv run --extra dev pytest tests/unit/test_views.py::test_create_url_requires_a_json_object
```

Run all repository checks with `pre-commit run --all-files`. Run the complete container stack with `docker compose up --build`.

## Architecture and behavior

The normal request flow is:

1. `shortener/app.py` matches a Starlette route.
2. `shortener/views.py` parses and validates request input.
3. `shortener/actions.py` performs an operation through `Database`.
4. `shortener/database.py` acquires an async pooled connection and executes parameterized SQL.
5. The view returns a Starlette response, or the app's exception handlers render an error as JSON.

The lifespan opens the pool, creates the table and index if needed, checks database connectivity, and closes the pool on shutdown.

Expected API behavior:

- Short keys match `[A-Za-z0-9_-]+` and have a maximum length of 50.
- Targets use `http` or `https`, include a host, contain no URL credentials, and have a maximum length of 2,048.
- Redirects use HTTP 307.
- Expected failures use `HTTPException` and preserve status codes.
- Database failures exposed by the action layer become HTTP 503 responses.
- Unexpected exceptions return a generic HTTP 500 body; do not expose internal details.

## Coding conventions

- Use async functions for request handlers and database I/O.
- Keep HTTP concerns in `views.py`, SQL operations in `actions.py`, and pool mechanics in `database.py`.
- Use psycopg parameters (`%s`) for every value derived from input. Never interpolate values into SQL strings.
- Catch narrow exception types. Log operational context without credentials, target URLs, or other sensitive values.
- Preserve the existing JSON error shape: `{"error": "...", "detail": "..."}`.
- Use Starlette response and exception types; do not add framework-specific abstractions without a clear need.
- Python 3.14 syntax is allowed because the project pins Python to `==3.14.*`.
- Ruff uses a 120-character line length.
- Keep patches focused and avoid unrelated refactors.

## Database changes

There is no migration framework. The schema is duplicated intentionally for two startup modes:

- `shortener/models.py` is used automatically by the application.
- `shortener/migration.sql` is available for manual schema setup.

When changing the schema, update both files and add or adjust tests. Keep all queries compatible with PostgreSQL and preserve parameterization.

`get_database()` stores a module-level singleton. Tests that replace or exercise it must avoid leaking state between test cases.

## Tests

- Tests under `tests/integration/` currently exercise HTTP behavior through a `TestClient` configured with a mocked `Database`.
- Unit tests cover validation, settings, and lower-level behavior.
- `tests/conftest.py` also provides PostgreSQL Testcontainers fixtures for tests that require a real database. Such tests require a working Docker daemon.
- Add regression tests for bug fixes and test both success and expected failure paths for API changes.
- Prefer asserting response status and meaningful response content, not only that a request completed.
- Avoid relying on test order or persistent database state.

Before considering a change complete, run the narrowest relevant tests, then the full suite when practical. Run pre-commit for changes that affect Python, configuration, Docker, workflows, dependencies, or formatting.

## Dependencies and generated files

- Declare dependencies in `pyproject.toml`.
- Regenerate `uv.lock` with `uv lock` or `make deps`; do not edit it manually.
- Do not add or change dependencies without explicit user approval and documented vetting.
- Do not edit or commit caches, virtual environments, coverage data, bytecode, or other generated artifacts.
- Never commit `.env`, passwords, tokens, or connection strings containing secrets.

## Documentation

Update `README.md` when commands, configuration, endpoints, response behavior, prerequisites, or architecture change. Keep examples executable and ensure documented defaults match the code and `.env.example`.
