# Template for backend course
[source rutube](https://rutube.ru/plst/799817/)  
[source youtube](https://youtube.com/playlist?list=PLrHK_KyUvYLNYjsUYbZ0n0VzT5djU3vfK&si=2BZ8h0AeL-45AQ6s)  
[gitlab link](https://gitlab.com/frukun1/doubletapp-django)
### install dependencies

```sh
poetry install --no-root
```

### create .env
```sh
cp env.example .env
```

### edit environment
```sh
ENVIRONMENT= # can be prod, test, local
```
### start docker
```sh
make up
```
### migrate
```sh
make init-migrate
```
### tests
```sh
make test
```
### create super user

```sh
make createsuperuser
```

### start web

```sh
make dev
```

### start bot

```sh
make bot
```

### down docker

```sh
make down
```

### logs docker

```sh
make logs
```

### start yandex unified agent

```sh
docker run -it -p 16241:16241 --detach -v `pwd`/config.yml:/etc/yandex/unified_agent/conf.d/config.yml -e FOLDER_ID=$FOLDER_ID cr.yandex/yc/unified-agent
```
