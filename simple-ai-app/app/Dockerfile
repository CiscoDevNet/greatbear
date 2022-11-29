FROM python:3.9

WORKDIR /usr/src/app

RUN apt-get update && \
    apt-get install ffmpeg libsm6 libxext6 -y

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir onnxruntime rtsp numpy paho-mqtt requests

COPY *.py .

CMD python -u minimal_ai_app.py $RTSP_STREAM $MQTT_BROKER $MQTT_TOPIC
