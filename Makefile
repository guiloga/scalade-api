SHELL=/bin/bash
PYTHON=python3
PYTEST=${PYTHON} -m pytest

.PHONY = load_fixtures setup docker_compose_dev \
		 test test_streams test_accounts test_common test_api

.DEFAULT_GOAL = setup

####################
# Install commands #
####################
install: # Development installation
	scripts/install.sh

load_fixtures: # Loads all models data from fixtures
	python manage.py loaddata fixtures/all.json

dump_fixtures: # Dumps all models data to fixtures
	scripts/dump_fixtures.sh

docker_compose_dev: # Up services with docker-compose on development
	docker-compose -f "docker-compose_dev.yml" up -d
	sleep 5

log_clean: # Cleans and recreates logs dir
	rm -rf logs | exit 0
	mkdir logs
	chomod -R 700 logs/

setup: # Initial Setup
	log_clean docker_compose_dev install load_fixtures

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