all: test

test:
	uv run pytest

install:
	uv sync --all-extras

upgrade:
	uv lock --upgrade
	uv sync --all-extras

run:
	docker compose up postgres -d
	sleep 3
	uv run python -m shortener.app
	docker compose down

watch:
	find . -type f -name "*.py" | entr -p uv run pytest
