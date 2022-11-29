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

from sampleAppAgent import SampleAppAgent
from prometheus_client import start_http_server
import json
import os
import logging
import uuid

logging.basicConfig(level=logging.INFO)
PROMETHEUS_PORT = os.environ.get('PROMETHEUS_PORT', '9090')
MONITORING = os.environ.get('MONITORING', 'off')


def main(config):
  # starting a thread with socket io
  logging.info('Setting up Sample App Agent...')
  if MONITORING == 'on':
    logging.info('Start prometheus monitoring...')
    start_http_server(int(PROMETHEUS_PORT), '0.0.0.0')

  SampleAppAgent(config).start()


if __name__ == '__main__':

  config = {}

  # Great Bear specific ID's of each node
  nodeId = os.environ.get('GB_NODE_ID', '')
  idMap = json.loads(os.environ.get('GB_NODE_IDS', '{}'))
  config['gb_node_id'] = idMap[nodeId] if nodeId in idMap else str(uuid.uuid4())

  # Great Bear specific naming of each node
  nodeName = os.environ.get('GB_NODE_NAME', '')
  nameMap = json.loads(os.environ.get('GB_NODE_NAMES', '{}'))
  config['gb_node_name'] = nameMap[nodeName] if nodeName in nameMap else 'Sample App Node'

  # Great Bear specific sync server host url
  config['base_url'] = os.environ.get('BASE_URL', 'sync-server-sample-app')

  # Great Bear specific sync server host port
  config['port'] = os.environ.get('PORT', '8080')

  # Sync Server full URL
  config['sync_server_url'] = 'http://' + config['base_url'] + ':' + config['port']

  # App name
  config['app_name'] = os.environ.get('APP_NAME', 'SAMPLE-APP')

  # App ID
  config['app_id'] = config['gb_node_id'] + '-' + config['app_name']

  # Run agent
  logging.info('Running...')
  main(config)
