all: test

docker-compose:
	docker-compose up postgres -d
	sleep 3
	@if command -v pg_isready > /dev/null; then \
		echo "Waiting for PostgreSQL to be ready..."; \
		while ! pg_isready -h localhost -p 5432; do sleep 1; done; \
	else \
		echo "pg_isready not found, install postgresql-client for better DB readiness check"; \
		sleep 3; \
	fi

test: docker-compose
	.venv/bin/pytest
	docker-compose down

install:
	uv pip sync requirements.txt

upgrade:
	uv pip compile requirements.in --upgrade -o requirements.txt
	uv pip sync requirements.txt

run: docker-compose
	python run_app.py
	docker-compose down

watch: docker-compose
	find . -type f -name "*.py" | entr -p pytest
