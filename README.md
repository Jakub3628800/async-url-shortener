
# Async URL Shortener

[![CI](https://github.com/Jakub3628800/async-url-shortener/actions/workflows/master.yml/badge.svg?branch=master)](https://github.com/Jakub3628800/async-url-shortener/actions/workflows/python-app.yml)
![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Jakub3628800/async-url-shortener/master.svg)

A high-performance URL shortener service built with Python's Starlette framework, designed for asynchronous operations.

## Features
- Fast URL shortening using async operations
- RESTful API endpoints
- Docker container support
- PostgreSQL database integration
- Comprehensive test coverage

## Run Locally

### Using Docker (Recommended)

1. Start PostgreSQL container:
```bash
docker run -d --name postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:alpine
```

2. Pull and run the application container:
```bash
docker run -d \
  --name url-shortener \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://postgres:postgres@host.docker.internal:5432/postgres \
  ghcr.io/jakub3628800/shortener:latest
```

### Development Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install pip-tools
make install
```

3. Set up environment variables:
```bash
cp env.example .env
```

4. Run the application:
```bash
make run
```

## API Documentation

The API documentation will be available at `http://localhost:8000/docs` when the application is running.

## Testing

Run the test suite:
```bash
make test
```

## Deployment

The application is containerized and can be deployed using Docker. The latest image is available at:
`ghcr.io/jakub3628800/shortener:latest`

## Contributing

Contributions are welcome! Please follow the standard GitHub workflow:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request
