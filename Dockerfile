FROM python:3-alpine


COPY requirements.txt requirements.txt
COPY sense.py sense.py

RUN apk update
RUN apk add make automake gcc g++ subversion python3-dev

RUN pip3 install -r requirements.txt

CMD ["python3", "sense.py"]