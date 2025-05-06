# Template for backend course

### install dependencies

```sh
poetry install --no-root
```

### create .env

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

### start docker

```sh
make up
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
