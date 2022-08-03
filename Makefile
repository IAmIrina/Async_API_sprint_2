include ./.env
env = --env-file ./.env

help:
	@echo "usage: make <target>"
	@echo "Targets:"
	@echo "	build"
	@echo "	up"
	@echo "	up_detach"
	@echo "	start"
	@echo "	down"
	@echo "	destroy"
	@echo "	stop"
	@echo "	test"

build:
	docker-compose -f docker-compose.yml ${env} build
up_detach:
	docker-compose -f docker-compose.yml ${env} up -d
up:
	docker-compose -f docker-compose.yml ${env} up
start:
	docker-compose -f docker-compose.yml ${env} start
down:
	docker-compose -f docker-compose.yml ${env} down
destroy:
	docker-compose -f docker-compose.yml ${env} down -v
stop:
	docker-compose -f docker-compose.yml ${env} stop
test:
	docker-compose -f docker-compose.yml -f docker-compose.test.yml  up fastapi-movies test-elasticsearch test-cache functional-tests

