# pull official base image
FROM python:3.10.6-slim-bullseye
RUN apt update && apt install git -y
ADD requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -U -r /app/requirements.txt
