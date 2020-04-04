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
	npm run gulp

install:
	pip install -e .

install-dev:
	pip install -r requirements-dev.txt

init: install
	python -c 'import nltk; nltk.download("wordnet")'

sync:
	pipenv sync --dev

lint:
	flake8 app.py goto_publication --max-line-length=120 --ignore=N802

run:
	export FLASK_APP=app.py; export FLASK_DEBUG=1; flask run -h 127.0.0.1 -p 5000

tests:
	python -m unittest discover -s goto_publication.tests

