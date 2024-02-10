
# async-url-shortener

Simple async url shortener written using Starlette framework. Mostly a toy project made to experiment with different
things such as GitHub actions or python async libraries.

[![Master workflow](https://github.com/Jakub3628800/async-url-shortener/actions/workflows/master.yml/badge.svg?branch=master)](https://github.com/Jakub3628800/async-url-shortener/actions/workflows/python-app.yml)
![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Jakub3628800/async-url-shortener/master.svg)
![coverage](https://gist.githubusercontent.com/Jakub3628800/5163dbd0fdea4409fd7a3ae6383c6b66/raw/gistfile1.svg)

It works: https://async-url-shortener.herokuapp.com/shipit

## Running
1. Activate a virtual environment
2. Install pip-tools: `pip install pip-tools` (pip-tols is used to manage dependencies, you only need to install it once when bootstraping the virtualenv)
3. Install dependencies: `make install`

### Running the tests
`make test`

### Running the app
`make run`

### Upgrading dependencies
`make upgrade`

## Environments
The app is currently deployed in heroku.

https://async-url-shortener.herokuapp.com/

## Artifacts
docker: `ghcr.io/jakub3628800/shortener:latest`
