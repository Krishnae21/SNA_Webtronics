all: run

build:
	docker-compose build

run:
	docker-compose up

uvicorn:
	uvicorn --port 8000 main:app --reload