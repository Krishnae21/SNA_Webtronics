all: run

build:
	docker-compose build

run:
	docker-compose up

down:
	docker-compose down

uvicorn:
	uvicorn --port 8000 main:app --reload