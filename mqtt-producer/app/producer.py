"""
Copyright (c) 2022 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

import os
import paho.mqtt.client as mqtt 
import time
import datetime

_MQTT_SERVICE_NAME: str = (os.getenv('MQTT_SERVICE_NAME') or 'broker.hivemq.com').strip()
_MQTT_TOPIC: str = (os.getenv('MQTT_TOPIC') or 'test_topic').strip()
_MESSAGE_TEXT: str = (os.getenv('MESSAGE_TEXT') or 'Hello World').strip()

print("MQTT_SERVICE_NAME:", _MQTT_SERVICE_NAME)
print("MQTT_TOPIC:", _MQTT_TOPIC)
print("MESSAGE_TEXT:", _MESSAGE_TEXT)

client = mqtt.Client()
client.connect(_MQTT_SERVICE_NAME) 
print("Connected to broker", _MQTT_SERVICE_NAME)

while True:
    client.publish(_MQTT_TOPIC, _MESSAGE_TEXT)
    datetime_object = datetime.datetime.now()
    print(datetime_object, "Published to topic", _MQTT_TOPIC, "message:", _MESSAGE_TEXT)
    time.sleep(5)