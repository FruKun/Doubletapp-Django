migrate:
	python src/manage.py migrate $(if $m, api $m,)

makemigrations:
	python src/manage.py makemigrations
	sudo chown -R ${USER} src/app/migrations/

createsuperuser:
	python src/manage.py createsuperuser

collectstatic:
	python src/manage.py collectstatic --no-input

dev:
	python src/manage.py runserver localhost:8000

command:
	python src/manage.py ${c}

shell:
	python src/manage.py shell

debug:
	python src/manage.py debug

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
	python src/manage.py run_bot

build:
	docker build -t $$CI_REGISTRY/frukun1/doubletapp-django/django:$$CI_ENVIRONMENT_SLUG-$$CI_COMMIT_SHA .
up:
	docker compose -f docker-compose-prod.yml up -d
down:
	docker compose down
logs:
	docker compose logs
pull:
	docker image pull registry.gitlab.com/frukun1/doubletapp-django/django:latest
push:
	docker image push $$CI_REGISTRY/frukun1/doubletapp-django/django:$$CI_ENVIRONMENT_SLUG-$$CI_COMMIT_SHA
