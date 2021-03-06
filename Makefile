SHELL=/bin/bash
PYTHON=python3
PYTEST=${PYTHON} -m pytest

.PHONY = install load_fixtures dump_fixtures docker_compose_dev log_clean setup \
		 test test_streams test_accounts test_common test_api

.DEFAULT_GOAL = setup

####################
# Install commands #
####################
install: # Development installation
	scripts/install.sh

load_fixtures: # Loads all models data from fixtures
	python manage.py loaddata fixtures/dev/accounts/*
	python manage.py loaddata fixtures/dev/streams/*
	python manage.py loaddata fixtures/common/permissions.json
	python manage.py loaddata fixtures/common/groups.json

dump_fixtures: # Dumps all models data to fixtures
	scripts/dump_fixtures.sh

docker_compose_dev: # Up services with docker-compose on development
	docker-compose -f "./docker/docker-compose_dev.yml" up -d
	sleep 15

log_clean: # Cleans and recreates logs dir
	rm -rf ./logs | exit 0
	mkdir logs
	chmod -R 700 logs/

setup: log_clean docker_compose_dev install load_fixtures

##################
# Tests commands #
##################
test: # Run tests
	${PYTEST}

test_streams: # Run streams tests
	${PYTEST} tests/test_streams.py

test_accounts: # Run accounts tests
	${PYTEST} tests/test_accounts.py

test_common: # Run common tests
	${PYTEST} tests/test_common.py

test_api: # Run api tests
	${PYTEST} tests/test_api.py