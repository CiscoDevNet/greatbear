FROM python:3.9

WORKDIR /usr/src/app

COPY requirements.txt .

RUN apt-get update && \
    apt-get install libsm6 libxext6 -y && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY *.py .

EXPOSE 9090

CMD ["python", "-u", "main.py"]
