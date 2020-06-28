# Local's Hit

Project of Lecture DBE14 Distributed Systems

## Team Members

- Markus Drespling
- Frederick Dehner
- David Lüttmann

## Install & run
Install:

1. Update pip: ```pip install --upgrade pip```
2. Update setuptools: ```pip install --upgrade setuptools```
3. Install localshit: ```pip install -e .```


Run frontend server:
```
frontend
```

Run backend server(s) with custom frontend server IP:
```
localshit -p "172.17.0.2"
```

Open client:
```
http://[frontend-ip]:8081/index.html
```

Run tests:
```
pytest tests -s
```

# Docker

You can use docker to run multiple servers on one host. If you use multiple servers distributed on more than one host, use Vagrant because DOcker doesn't support bridged networks to the local area network.

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
docker build -f Dockerfile.frontend -t localshit-frontend .
```

Run docker

```
docker run --rm localshit-frontend
```

# Vagrant

Because Docker doesn't support bridged networking, we choose Vagrant containers with VirtualBox.

## Setup

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
11. Update pip: ```pip install --upgrade pip```
12. Update setuptools: ```pip install --upgrade setuptools```
13. Install localshit: ```pip install -e .```

## Run Vagrant


1. Start vagrant VM: ```vagrant up```
2. Connect to VM via ssh: ```vagrant ssh```
3. Navigate to ```/home/vagrant/code``` and start the server with ```localshit -p "[frontend_ip]"```
4. To stop the VM, use ```vagrant halt```

# Examples
To run the examles within a docker container use

```
docker run -it --rm  -v "$PWD/examples":"/usr/src/widget_app" python:3 python /usr/src/widget_app/dynamicdiscover.py
```