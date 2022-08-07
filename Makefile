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
	@echo "	up_dev"
	@echo "	test"


build:
	docker-compose -f docker-compose.yml  build
up_detach:
	docker-compose -f docker-compose.yml  up -d
up:
	docker-compose -f docker-compose.yml  up
start:
	docker-compose -f docker-compose.yml  start
down:
	docker-compose -f docker-compose.yml  down
destroy:
	docker-compose -f docker-compose.yml  down -v
stop:
	docker-compose -f docker-compose.yml  stop
dev:
	docker-compose -f docker-compose.yml -f docker-compose-dev.yml up --build
test:
	docker-compose -f docker-compose.yml -f docker-compose-test.yml up --build fastapi-movies test-elasticsearch test-cache functional-tests

