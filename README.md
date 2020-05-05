# Local's Hit

Project of Lecture DBE14 Distributed Systems

## Team Members

- Markus Drespling
- Frederick Dehner
- David Lüttmann

## Build and run docker

Build Docker Image (after every change)

```
docker build -t localshit .
```

Run docker

```
docker run localshit
```

## Usage

Run application (without docker):

```
python src/localshit/run.py 
```

## Examples
To run the examles within a docker container use

```
docker run -it --rm  -v "$PWD/examples":"/usr/src/widget_app" python:3 python /usr/src/widget_app/dynamicdiscover.py
```
