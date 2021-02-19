FROM python:3-slim


COPY requirements.txt requirements.txt
COPY sense.py sense.py

RUN pip3 install -r requirements.txt

CMD ["python3", "sense.py"]
