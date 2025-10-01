# Async URL Shortener

[![CI](https://github.com/Jakub3628800/async-url-shortener/actions/workflows/master.yml/badge.svg?branch=master)](https://github.com/Jakub3628800/async-url-shortener/actions/workflows/python-app.yml)
![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Jakub3628800/async-url-shortener/master.svg)

A high-performance URL shortener service built with Python's Starlette framework, designed for asynchronous operations. This project serves as a practical experiment with async libraries, GitHub Actions, and modern Python development practices.

## Features
- **Fast URL Shortening**: Utilizes async operations to ensure non-blocking, efficient URL shortening.
- **RESTful API**: Provides a clean and simple RESTful API for creating and managing shortened URLs.
- **Docker Support**: Comes with a `Dockerfile` and `compose.yaml` for easy containerization and deployment.
- **PostgreSQL Integration**: Uses a robust PostgreSQL database for data persistence.
- **Comprehensive Test Coverage**: Includes a full suite of tests to ensure code quality and reliability.

## Technologies Used
- **Framework**: [Starlette](https://www.starlette.io/)
- **Database**: [PostgreSQL](https://www.postgresql.org/)
- **Async Support**: `asyncpg`, `uvloop`
- **Validation**: `pydantic`
- **Dependency Management**: `pip-tools`, `uv`
- **Testing**: `pytest`, `pytest-asyncio`, `testcontainers`

## Project Structure
```
.
├── alembic/              # Database migration scripts
├── shortener/            # Main application source code
│   ├── views/            # API view handlers
│   ├── __init__.py
│   ├── actions.py        # Core business logic
│   ├── app.py            # Starlette application setup
│   ├── database.py       # Database connection and session management
│   ├── models.py         # SQLAlchemy ORM models
│   └── settings.py       # Application settings management
├── tests/                # Test suite
├── Dockerfile            # Container build instructions
├── Makefile              # Development command shortcuts
├── README.md             # This file
├── alembic.ini           # Alembic configuration
├── compose.yaml          # Docker Compose setup
├── pyproject.toml        # Project metadata and dependencies
└── uv.lock               # Pinned dependencies
```

## Run Locally

### Using Docker (Recommended)
1.  Start the PostgreSQL container:
    ```bash
    docker run -d --name postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:alpine
    ```
2.  Pull and run the application container:
    ```bash
    docker run -d \
      --name url-shortener \
      -p 8000:8000 \
      -e DATABASE_URL=postgresql://postgres:postgres@host.docker.internal:5432/postgres \
      ghcr.io/jakub3628800/shortener:latest
    ```

### Development Setup
1.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
2.  Install dependencies:
    ```bash
    pip install pip-tools
    make install
    ```
3.  Set up environment variables by copying the example file:
    ```bash
    cp env.example .env
    ```
4.  Run the application:
    ```bash
    make run
    ```

## Configuration
The application is configured using environment variables. You can set them in a `.env` file in the project root.

| Variable          | Description                                | Default         |
| ----------------- | ------------------------------------------ | --------------- |
| `DATABASE_URL`    | The connection URL for the PostgreSQL database. | `postgresql://postgres:postgres@localhost:5432/postgres` |
| `APPLICATION_PORT`| The port on which the application will run.    | `8000`          |
| `DEBUG`           | Toggles debug mode.                        | `false`         |

## API Endpoints
The API documentation is available at `http://localhost:8000/docs` when the application is running.

- **`POST /urls`**: Create a new shortened URL.
  - **Request Body**: `{"url": "https://example.com"}`
  - **Response**: `{"url": "https://example.com", "short_url": "short_code"}`

- **`GET /{short_url}`**: Redirect to the original URL.

- **`GET /ping`**: A simple health check endpoint.
  - **Response**: `{"ping": "pong"}`

- **`GET /status`**: Provides the status of the application and its database connection.

## Testing
To run the test suite, use the following command:
```bash
make test
```

## Deployment
The application is containerized and can be deployed using Docker. The latest image is available at:
`ghcr.io/jakub3628800/shortener:latest`

## License
This project is not licensed.