include .env
all:
docker-file:=
ifeq (${ENVIRONMENT},prod)
	docker-file := -f docker-compose.yml
endif
ifeq (${ENVIRONMENT}, test)
	docker-file := -f docker-compose-test.yml
endif
ifeq (${ENVIRONMENT}, local)
	docker-file := -f docker-compose.yml -f docker-compose-local.yml
endif

migrate:
	python3 manage.py migrate $(if $m, api $m,)

makemigrations:
	python3 src/manage.py makemigrations
	sudo chown -R ${USER} src/app/migrations/

createsuperuser:
	python3 src/manage.py createsuperuser

collectstatic:
	python3 src/manage.py collectstatic --no-input

dev:
	python3 src/manage.py runserver localhost:8000

command:
	python3 src/manage.py ${c}

shell:
	python3 src/manage.py shell

debug:
	python3 src/manage.py debug

lint:
	isort .
	flake8 --config setup.cfg
	black --config pyproject.toml .

check_lint:
	isort --check --diff .
	flake8 --config setup.cfg
	black --check --config pyproject.toml .

test:
	pytest
bot:
	python3 src/manage.py run_bot

build:
	docker compose build

push:
	docker image push ${IMAGE_NGINX}
	docker image push ${IMAGE_APP}

pull:
	docker image pull ${IMAGE_APP}
	docker image pull ${IMAGE_NGINX}

up-build:
	docker compose ${docker-file} up -d --build

up:
	docker compose ${docker-file} up -d

down:
	docker compose ${docker-file} down

logs:
	docker compose ${docker-file} logs
