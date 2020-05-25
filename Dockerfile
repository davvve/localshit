FROM python:3

ADD src/localshit /

CMD [ "python", "./run.py" ]