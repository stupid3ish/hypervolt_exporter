# syntax=docker/dockerfile:1

FROM python:3-slim-buster
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY ./requirements.txt /code/
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "exporter.py"]