FROM python:3.9.13-slim

RUN pip install paho-mqtt

COPY consumer.py ./

CMD [ "python", "-u", "consumer.py" ]