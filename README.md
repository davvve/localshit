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

# Set up vagrant

1. Install VirtualBox
2. Install Vagrant
3. Add hashicorp/bionic64 box image: ``` vagrant box add hashicorp/bionic64```
4. (Init Vagrantfile: ```vagrant init hashicorp/bionic64```)
5. ```vagrant up```
6. ```sudo apt-get updates```
7. ```sudo apt-get -y install python3-pip```
8. Update setuptools: ```pip3 install setuptools```
9. Install localshit: pip3 install -e .
10. sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.6 1
11. pip install --upgrade pip
12. apt-get install python3-venv

## Run Vagrant
1. ```vagrant up```
2. ```vagrant ssh```
3. ```vagrant halt```