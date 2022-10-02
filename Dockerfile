FROM python:3.8.10-alpine

RUN apk add --update \
  build-base postgresql-dev libffi-dev libxml2-dev libxslt-dev python3-dev gcc \
  tzdata git vim openssh \
  && python3 -m pip install --upgrade pip setuptools wheel \
  && rm -rf /var/cache/apk/*

# Russian locale settings
ENV LANG ru_RU.UTF-8

WORKDIR /usr/src
COPY ./requirements.txt ./requirements.txt
RUN pip3 install -r ./requirements.txt

COPY . .

EXPOSE 5000
CMD ["python3", "main.py"]
