all: lint test

lint:
	pre-commit run --all-files

docker-compose:
	docker compose up postgres -d
	sleep 5 # wait for postgres to start

test: docker-compose
	pytest
	docker compose down

install:
	pip-sync

upgrade:
	pip-compile
	pip-sync

run: docker-compose
	python run_app.py
	docker compose down
