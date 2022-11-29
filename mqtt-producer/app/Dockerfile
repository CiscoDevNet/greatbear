FROM python:3.9.13-slim

RUN pip install paho-mqtt

COPY producer.py ./

CMD [ "python", "-u", "producer.py" ]