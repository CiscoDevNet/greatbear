FROM python:3.8-alpine

WORKDIR /echo

RUN pip install flask

COPY server.py ./

EXPOSE 11777

CMD [ "python", "server.py" ]