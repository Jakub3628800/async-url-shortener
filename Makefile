all: test-unit

docker-compose:
	docker compose up postgres -d
	sleep 3
	@if command -v pg_isready > /dev/null; then \
		echo "Waiting for PostgreSQL to be ready..."; \
		while ! pg_isready -h localhost -p 5432; do sleep 1; done; \
	else \
		echo "pg_isready not found, install postgresql-client for better DB readiness check"; \
		sleep 3; \
	fi

test: test-integration docker-test

test-unit:
	uv run python -m pytest tests/unit/ -v

test-integration:
	DB_TYPE=sqlite uv run pytest tests/integration/ -v

test-postgres: docker-compose
	DB_TYPE=postgresql uv run pytest tests/integration/ -v
	docker compose down

docker-test: docker-build docker-test-sqlite docker-test-postgres

docker-test-sqlite:
	@echo "Testing Docker deployment with SQLite..."
	docker run --rm -d --name test-sqlite-app -p 8001:8000 -e DB_TYPE=sqlite async-url-shortener
	sleep 3
	curl -f http://localhost:8001/ping || (docker stop test-sqlite-app && exit 1)
	curl -f http://localhost:8001/status || (docker stop test-sqlite-app && exit 1)
	docker stop test-sqlite-app
	@echo "SQLite Docker test passed!"

docker-test-postgres: docker-compose
	@echo "Testing Docker deployment with PostgreSQL..."
	docker run --rm -d --name test-postgres-app -p 8002:8000 \
		-e DB_TYPE=postgresql \
		-e DB_HOST=host.docker.internal \
		-e DB_PORT=5432 \
		-e DB_DATABASE=urldatabase \
		-e DB_USER=localuser \
		-e DB_PASSWORD=password123 \
		--add-host=host.docker.internal:host-gateway \
		async-url-shortener
	sleep 5
	curl -f http://localhost:8002/ping || (docker stop test-postgres-app && docker compose down && exit 1)
	curl -f http://localhost:8002/status || (docker stop test-postgres-app && docker compose down && exit 1)
	docker stop test-postgres-app
	docker compose down
	@echo "PostgreSQL Docker test passed!"

test-all: test-unit test-integration test-postgres

lint:
	uv run ruff check .
	uv run mypy .

format:
	uv run ruff format .

install:
	uv sync

install-dev:
	uv sync --dev

upgrade:
	uv sync --upgrade

clean:
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyc" -delete
	find . -name "*.db" -delete

run: docker-compose
	uv run python run_app.py
	docker compose down

run-sqlite:
	DB_TYPE=sqlite uv run python run_app.py

run-dev:
	DB_TYPE=sqlite uv run uvicorn shortener.factory:app --reload --host 0.0.0.0 --port 8000

watch: docker-compose
	find . -type f -name "*.py" | entr -p uv run pytest

docker-build:
	docker build -t async-url-shortener .

docker-run-sqlite:
	docker run -d --name url-shortener-sqlite -p 8000:8000 -e DB_TYPE=sqlite async-url-shortener

docker-run-postgres:
	docker compose up -d

docker-stop:
	docker compose down
	docker stop url-shortener-sqlite 2>/dev/null || true
	docker rm url-shortener-sqlite 2>/dev/null || true

pre-commit:
	uv run pre-commit run --all-files

ci: test-unit lint
	@echo "All CI checks passed!"

.PHONY: all docker-compose test test-unit test-integration test-sqlite test-postgres test-all lint format install install-dev upgrade clean run run-sqlite run-dev watch docker-build docker-run-sqlite docker-run-postgres docker-stop pre-commit ci
