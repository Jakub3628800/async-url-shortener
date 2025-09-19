export UV_ISOLATED=1

all: test

test:
	uv run --extra dev pytest

deps:
	uv lock --upgrade

run:
	docker compose up postgres -d
	sleep 3
	uv run -m shortener.app
	docker compose down
