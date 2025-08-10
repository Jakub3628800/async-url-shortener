all: test

test:
	uv run pytest

upgrade-deps:
	uv lock --upgrade

run:
	docker compose up postgres -d
	sleep 3
	uv run python -m shortener.app
	docker compose down

run-docker:
	docker compose up
