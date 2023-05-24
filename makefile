PORT ?= 8000
start:
		poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

build:
	poetry build

dev:
		poetry run flask --app page_analyzer:app run

install:
		poetry install

lint:
		poetry run flake8 page_analyzer