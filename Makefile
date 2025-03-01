all: test

docker-compose:
        docker compose up postgres -d
        while ! pg_isready -h localhost -p 5432; do sleep 1; done

test: docker-compose
        pytest
        docker compose down

install:
        pip-sync

upgrade:
        pip-compile --upgrade
        pip-sync

run: docker-compose
        python run_app.py
        docker compose down

watch: docker-compose
        find . -type f -name "*.py" | entr -p pytest
