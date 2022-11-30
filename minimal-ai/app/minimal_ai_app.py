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

import sys
import rtsp
import onnxruntime as ort
import numpy as np
import paho.mqtt.client as mqtt
import requests
from preprocess import preprocess

if __name__ == '__main__':

    """
    python3 minimal_ai_app.py <url of RTSP stream> <url of MQTT Broker> <MQTT topic>
    """

    if len(sys.argv) != 4:
        raise ValueError("This demo app expects 3 arguments and has %d" % (len(sys.argv) - 1))

    # Load in the command line arguments
    rtsp_stream, mqtt_broker, mqtt_topic = sys.argv[1], sys.argv[2], sys.argv[3]

    # Download the model
    model = requests.get('https://github.com/onnx/models/raw/main/vision/classification/inception_and_googlenet/googlenet/model/googlenet-12.onnx')
    open("model.onnx" , 'wb').write(model.content)
    
    sess_options = ort.SessionOptions()
    sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    sess_options.optimized_model_filepath = "optimized_model.onnx"

    session = ort.InferenceSession("model.onnx", sess_options)
    inname = [input.name for input in session.get_inputs()]

    # Download the class names
    labels = requests.get('https://raw.githubusercontent.com/onnx/models/main/vision/classification/synset.txt')
    open("synset.txt" , 'wb').write(labels.content)
    with open("synset.txt", 'r') as f:
        labels = [l.rstrip() for l in f]

    # Connect to the MQTT Broker
    mqtt_client = mqtt.Client()
    mqtt_client.connect(mqtt_broker)
    mqtt_client.loop_start()

    # Connect to the RTSP Stream
    rtsp_client = rtsp.Client(rtsp_server_uri = rtsp_stream)
    while rtsp_client.isOpened():
        img = rtsp_client.read()
        if img != None:

            img = preprocess(img)
            preds = session.run(None, {inname[0]: img})
            pred = np.squeeze(preds)
            a = np.argsort(pred)[::-1]
            print(labels[a[0]])
            mqtt_client.publish(mqtt_topic, labels[a[0]])

    rtsp_client.close()
    mqtt_client.disconnect()
