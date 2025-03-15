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

piplock:
	pipenv install
	sudo chown -R ${USER} Pipfile.lock

lint:
	isort .
	flake8 --config setup.cfg
	black --config pyproject.toml .

check_lint:
	isort --check --diff .
	flake8 --config setup.cfg
	black --check --config pyproject.toml .

bot:
	python3 src/manage.py run_bot

build:
	docker build -t $$CI_REGISTRY/frukun1/doubletapp-django/telegram-bot:$$CI_ENVIRONMENT_SLUG-$$CI_COMMIT_SHA .
up:
	docker compose -f docker-compose-prod.yml up -d
down:
	docker compose -f docker-compose-prod.yml down
logs:
	docker compose -f docker-compose-prod.yml logs
pull:
	docker image pull django:latest
push:
	docker image push $$CI_REGISTRY/frukun1/doubletapp-django/telegram-bot:$$CI_ENVIRONMENT_SLUG-$$CI_COMMIT_SHA
