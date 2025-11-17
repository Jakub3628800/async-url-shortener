export UV_ISOLATED=1

all: test

test:
	uv run --extra dev pytest

deps:
	uv lock --upgrade

run:
	docker compose up postgres -d --wait
	uv run -m shortener.app
	docker compose down

migrate:
	docker compose up postgres -d --wait
	psql -h localhost -U localuser -d urldatabase -f shortener/migration.sql
	docker compose down

un-migrate:
	docker compose up postgres -d --wait
	psql -h localhost -U localuser -d urldatabase -c "DROP TABLE IF EXISTS short_urls CASCADE;"
	docker compose down
