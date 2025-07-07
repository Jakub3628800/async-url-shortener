
# Async URL Shortener

[![CI](https://github.com/Jakub3628800/async-url-shortener/actions/workflows/master.yml/badge.svg?branch=master)](https://github.com/Jakub3628800/async-url-shortener/actions/workflows/python-app.yml)
![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Jakub3628800/async-url-shortener/master.svg)

A high-performance URL shortener service built with Python's Starlette framework, designed for asynchronous operations.

## Features
- Fast URL shortening using async operations
- RESTful API endpoints
- Docker container support
- SQLite and PostgreSQL database support
- Comprehensive test coverage

## Quick Start

### One-Command Docker Run (SQLite)
```bash
make docker-build && make docker-run-sqlite
```

This builds and runs the application with SQLite database in a single command.

## Run Locally

### Using Docker (Recommended)

#### With SQLite (simplest setup):
```bash
make docker-build
make docker-run-sqlite
```

#### With PostgreSQL:
1. Start PostgreSQL container:
```bash
docker run -d --name postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:alpine
```

2. Build and run the application:
```bash
make docker-build
docker run -d \
  --name url-shortener \
  -p 8000:8000 \
  -e DB_TYPE=postgresql \
  -e DB_HOST=host.docker.internal \
  -e DB_USER=postgres \
  -e DB_PASSWORD=postgres \
  -e DB_DATABASE=postgres \
  async-url-shortener
```

### Development Setup

1. Install dependencies using uv:
```bash
make install
```

2. Set up environment variables:
```bash
cp env.example .env
```

3. Run the application:
```bash
# With SQLite (default)
make run-sqlite

# With PostgreSQL (requires Docker)
make run
```

## API Documentation

The API documentation will be available at `http://localhost:8000/docs` when the application is running.

## Testing

Run tests against both SQLite and PostgreSQL:
```bash
make test-all
```

Run tests with SQLite only:
```bash
make test-sqlite
```

Run tests with PostgreSQL only:
```bash
make test-postgres
```

## Deployment

The application is containerized and can be deployed using Docker. The latest image is available at:
`ghcr.io/jakub3628800/shortener:latest`
