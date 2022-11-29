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

from flask import Flask
from syncer import SyncClient
import json
import os
import uuid

HTTP_PORT: int = int(os.getenv('HTTP_PORT') or '11777')
BASE_URL: str = os.getenv('BASE_URL') or '/'
DEFAULT_ECHO_TEXT: str = os.getenv('ECHO_TEXT') or 'Hello World'
ECHO_TEXT: str = DEFAULT_ECHO_TEXT

SYNC_SERVER_HOST: str = os.getenv('SYNC_SERVER_HOST')
SYNC_SERVER_PORT: str = os.getenv('SYNC_SERVER_PORT')
GB_NODE_ID: str = os.getenv('GB_NODE_ID') or ''
GB_NODE_IDS: str = os.getenv('GB_NODE_IDS') or '{}'
APP_NAME: str = os.getenv('APP_NAME') or 'bear-echo-runtime'

class EchoSyncer(SyncClient):
    """extends the SyncClient and overrides the "onNewData" and onRemoveContent listeners"""
    def onNewData(self, data):
        global ECHO_TEXT
        print(f'ECHO_TEXT updated from {ECHO_TEXT} to {data}')
        ECHO_TEXT = data

    def onRemoveContent(self):
        global ECHO_TEXT
        print(f'ECHO_TEXT updated from {ECHO_TEXT} to {DEFAULT_ECHO_TEXT}')
        ECHO_TEXT = DEFAULT_ECHO_TEXT

app = Flask(__name__)

@app.route(BASE_URL, methods=['GET'])
def echo():
    return(f'<hr><center><h1>{ECHO_TEXT}</h1><center><hr>')

def main():
    print('ECHO_TEXT: ' + ECHO_TEXT)
    print(f'Started on 0.0.0.0:{HTTP_PORT}{BASE_URL}')
    nodeIDMap = json.loads(GB_NODE_IDS)
    nodeID = nodeIDMap[GB_NODE_ID] if GB_NODE_ID in nodeIDMap else str(uuid.uuid4())
    sync = EchoSyncer(
        syncServerHost='http://%s:%s' % (SYNC_SERVER_HOST, SYNC_SERVER_PORT),
        gbNodeID=nodeID,
        appName=APP_NAME,
        deployID='demo',
    )
    sync.start()
    app.run(host='0.0.0.0', port=HTTP_PORT) # blocking
    sync.stop()

if __name__ == '__main__':
    main()
