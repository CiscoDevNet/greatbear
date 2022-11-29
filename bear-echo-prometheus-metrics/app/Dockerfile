FROM python:3.8-alpine

WORKDIR /echo

COPY requirements.txt .

RUN set -e; \
    apk add --no-cache --virtual .build-deps \
    gcc \
    libc-dev \
    linux-headers \
    ; \
    pip install --no-cache-dir -r requirements.txt; \
    apk del .build-deps;

COPY server.py ./

EXPOSE 11777

CMD uwsgi --http 0.0.0.0:11777 --wsgi-file server.py --callable app
