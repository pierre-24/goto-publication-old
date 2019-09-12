all: help

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  init                        to install python dependencies through pipenv"
	@echo "  sync                        update dependencies of pipenv"
	@echo "  lint                        to lint backend code (flake8)"
	@echo "  front                       install NPM packages and build front (JS+CSS)"
	@echo "  help                        to get this help"

front:
	npm i
	gulp

init:
	pipenv install --dev --ignore-pipfile

sync:
	pipenv sync --dev

lint:
	pipenv run flake8 app.py goto_publi --max-line-length=120 --ignore=N802
