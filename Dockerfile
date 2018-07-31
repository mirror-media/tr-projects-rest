FROM python:3.5-alpine

RUN addgroup user && adduser -h /home/user -D user -G user -s /bin/sh

COPY . /usr/src/app/tr-projects-rest

WORKDIR /usr/src/app/tr-projects-rest

RUN apk update \
    && apk add gcc libc-dev linux-headers \
    && pip install --upgrade pip \
    && pip install -r requirements.txt

EXPOSE 8080
CMD ["/usr/local/bin/uwsgi", "--ini", "server.ini"]
