FROM python:2-onbuild
# FROM pypi/eve

RUN groupadd user && useradd --create-home --home-dir /home/user -g user user

COPY . /usr/src/app/tr-projects-rest 

RUN set -x \
    && apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && apt-get install -y git

RUN buildDeps=' \
    gcc \
    make \
    python \
    ' \
    && set -x \
    && apt-get update && apt-get install -y $buildDeps --no-install-recommends && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip \
    # && pip install -r requirements.txt
    && pip install flask \
    && pip install Eve \
    && pip install uwsgi 

EXPOSE 8080
# CMD ["python", "/tr-projects-rest/server.py"]
CMD ["/usr/local/bin/uwsgi", "--ini", "/usr/src/app/tr-projects-rest/server.ini"]
