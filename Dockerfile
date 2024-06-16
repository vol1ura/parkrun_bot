FROM python:3.11.6-alpine

RUN apk add --no-cache \
  build-base postgresql-dev libffi-dev libxml2-dev libxslt-dev python3-dev gcc \
  tzdata git vim openssh \
  && python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel

# Russian locale settings
ENV LANG ru_RU.UTF-8

WORKDIR /usr/src
COPY ./requirements.txt ./requirements.txt
RUN pip3 install -r ./requirements.txt --no-cache-dir

COPY . .

EXPOSE 5000
CMD ["python3", "main.py"]
