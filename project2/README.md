# README

To run project you must

## Run nameserver

```bash
# Shell 1
poetry run python -m Pyro5.nameserver
```

## Run server

```bash
# Shell 2
poetry run python -m project2 --proc-type server --n-resources 2
```

## Run clients

```bash
# Shell 3
poetry run python -m project2 --proc-type client --n-resources 2
```
