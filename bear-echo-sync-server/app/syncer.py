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

from datetime import datetime
from enum import Enum
from threading import Thread
import socketio
import logging
import time

logging.basicConfig(level=logging.DEBUG)


class AppStatus(Enum):
    NULL = 0
    ONLINE = 1
    ERROR = 2
    OFFLINE = 3
    INITIALIZING = 4
    PAYLOAD_ERROR = 5


def nowTS():
    # now timestamp as nondelimited year-month-day-hour-minute-second string
    return datetime.now().strftime("%Y%m%d%H%M%S")


class SyncClient:
    """
    To be used directly, or subclassed with desired methods overridden.
    public methods to override:
        onConnect()
        onConnectError(errMsg)
        onDisconnect()
        onNewData(data)
        onRemoveContent()
        onCheckStatus()
        onCatchAll(data)

    Once the SyncClient is initialized, start listening with
        sync.start()

    Stop with:
        sync.stop()
    """
    def __init__(self, syncServerHost, gbNodeID, appName, deployID=nowTS()):
        self.syncServerHost = syncServerHost
        self.gbNodeID = gbNodeID
        self.appName = '%s-%s' % (appName, deployID)
        self.appID = '%s-%s-%s' % (gbNodeID, appName, deployID)
        self.fullSyncServerURL = '%s?nodeId=%s&appName=%s&appId=%s' % (
                self.syncServerHost,
                self.gbNodeID,
                self.appName,
                self.appID)

        logging.debug('initializing sync client...')
        logging.debug('    syncServerHost: <%s>', self.syncServerHost)
        logging.debug('    nodeID:         <%s>', self.gbNodeID)
        logging.debug('    appName:        <%s>', self.appName)
        logging.debug('    appID:          <%s>', self.appID)

        self.running = False
        self.connected = False
        self.connection = Thread(target=self.connect, daemon=False)

    # overide me
    def onConnect(self):
        logging.info('%s connected', self.appName)

    # overide me
    def onConnectError(self, err):
        logging.error('%s connection error: %s', self.appName, err)

    # overide me
    def onDisconnect(self):
        logging.info('%s disconnected', self.appName)

    # overide me
    def onNewData(self, data):
        logging.info('%s received new data: <%s>', self.appName, data)
        # supports an optional return to emit a response back to the server.
        # if an exception is raised, an error response will be emitted back to
        # the server.
        return None

    # overide me
    def onRemoveContent(self):
        logging.info('%s received remove content', self.appName)
        # supports an optional return
        return None

    # overide me
    def onCheckStatus(self, msg=None):
        logging.info('%s received on check status: %s', self.appName, msg)
        # supports an optional return
        return None

    # overide me
    def onCatchAll(self, data=None):
        logging.info('%s received an unexpeected event: <%s>', self.appName, data)

    # not blocking
    def start(self):
        logging.info('%s starting...', self.appName)
        self.running = True
        self.connection.start()

    # blocking
    def join(self):
        self.connection.join()

    def stop(self):
        self.running = False
        self.connected = False

    def connect(self):
        sio = socketio.Client(logger=False, engineio_logger=False, ssl_verify=False)
        logging.info('%s connecting to <%s>...', self.appName, self.fullSyncServerURL)

        @sio.event
        def connect():
            self.onConnect()

        @sio.event
        def connect_error(err):
            self.onConnectError(err)

        @sio.event
        def disconnect():
            self.onDisconnect()
            self.connected = False

        @sio.on('newData')
        def onNewData(data):
            try:
                resp = self.onNewData(data)
                if resp is not None:
                    logging.info('onNewData handler returned a response: <%s>', resp)
                    return resp
                return "ok"
            except Exception as e:
                logging.error('onNewData handler raised an exception: %s', e)
                return "error: %s" % e


        @sio.on('removeContent')
        def onRemoveContent():
            try:
                resp = self.onRemoveContent()
                if resp is not None:
                    logging.info('onRemoveContent handler returned a response: <%s>', resp)
                    return resp
                return "ok"
            except Exception as e:
                logging.error('onRemoveContent handler raised an exception: %s', e)
                return "error: %s" % e

        @sio.on('checkStatus')
        def onCheckStatus(msg=None):
            heartbeat = {'status': AppStatus.ONLINE.value, 'appId': self.appID}
            try:
                statusMsg = self.onCheckStatus(msg)
                if statusMsg is not None:
                    heartbeat['status_msg'] = statusMsg
            except Exception as e:
                heartbeat['status'] = AppStatus.PAYLOAD_ERROR.value
                heartbeat['error'] = 'exception: %s' % e
            logging.debug('status check response %s', heartbeat)

            # legacy
            sio.emit('sendStatus', heartbeat)

            # this return value is delivered as the acknowledgement to the
            # server. note: cannot return a tuple. must return a single val
            return heartbeat

        @sio.on('*')
        def onCatchAll(data=None):
            self.onCatchAll(data)

        while self.running:
            if (not self.connected):
                try:
                    sio.connect(self.fullSyncServerURL)
                    self.connected = True
                    sio.wait()
                # TODO(sam): handle the "Already Connected" exception better
                except Exception as e:
                    logging.error('connection error: %s', e)
                    time.sleep(5)
                    pass
            else:
                logging.debug("already connected. looping...")
                time.sleep(5)
