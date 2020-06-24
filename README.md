# Local's Hit

Project of Lecture DBE14 Distributed Systems

## Team Members

- Markus Drespling
- Frederick Dehner
- David Lüttmann

## Install & run (without docker)
Install:
```
pip install -e .
```
Run backend:
```
localshit
```

Run client (same for proxy):
```
client
```


## Build and run backend

Build Docker image for backends (after every change)

```
docker build -f Dockerfile.backend -t localshit .
```

Run docker

```
docker run --rm localshit
```

## Build and run client

Build Docker image for backends (after every change)

```
docker build -f Dockerfile.client -t localshit-client .
```

Run docker

```
docker run --rm localshit-client
```

## Build and run client

Build Docker image for backends (after every change)

```
docker build -f Dockerfile.proxy -t localshit-proxy .
```

Run docker

```
docker run --rm localshit-proxy
```

## Run tests
```
pytest tests -s
```

## Examples
To run the examles within a docker container use

```
docker run -it --rm  -v "$PWD/examples":"/usr/src/widget_app" python:3 python /usr/src/widget_app/dynamicdiscover.py
```