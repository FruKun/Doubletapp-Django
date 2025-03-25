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

bot:
	python3 src/manage.py run_bot

build:
	docker build -t $$IMAGE_NGINX ./nginx
	docker build -t $$IMAGE_APP .
local-up:
	docker compose -f docker-compose.yml -f docker-compose-local.yml up -d
local-down:
	docker compose -f docker-compose.yml -f docker-compose-local.yml down
dev-up:
	docker compose -f docker-compose.yml -f docker-compose-dev.yml up -d --build
dev-down:
	docker compose -f docker-compose.yml -f docker-compose-dev.yml down
dev-logs:
	docker compose -f docker-compose.yml -f docker-compose-dev.yml logs
up:
	docker compose up -d
down:
	docker compose down
logs:
	docker compose logs
pull:
	docker image pull $$IMAGE_APP
push:
	docker image push $$IMAGE_NGINX
	docker image push $$IMAGE_APP
