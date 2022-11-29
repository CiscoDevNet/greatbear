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

from threading import Thread
import socketio
import logging
import time


class SampleAppAgent:
  def __init__(self, config):
      logging.info(' === Sample App Agent === ')

      self.connection = Thread(target=self.run_connection, daemon=False)
      self.running = False
      self.connected = False
      self.config = config


  def run_connection(self):
    logging.info('Sample App Agent running...')

    while self.running:

      sio = socketio.Client(logger=False, engineio_logger=False, ssl_verify=False)

      @sio.event
      def connect():
        logging.info('Sample App Agent connected')

      @sio.event
      def connect_error(data):
        logging.info('Sample App Agent connection failed with ' + self.config['sync_server_url'])

      @sio.on('newData')
      def onNewData(message):
        logging.info('Sample App Agent received a new data message')
        logging.info(message)

      
      @sio.on('removeContent')
      def onRemoveContent():
        logging.info('Sample App Agent received a remove content message')


      @sio.on('checkStatus')
      def onCheckStatus():
        logging.info('Sample App Agent send status to sync-server')
        sio.emit('sendStatus', { 'status': 1, 'appId': self.config['app_id'] })


      if(not self.connected):
        try:
          sio.connect(self.config['sync_server_url'] + '?nodeId='+ self.config['gb_node_id'] + '&appName=' + self.config['app_name'] + '&appId=' + self.config['app_id'])
          self.connected = True
          sio.wait()
        except:
          # Wait 5sec and try to connect again
          time.sleep(5)
          pass


  def start(self):
    self.running = True
    self.connection.start()
    self.connection.join()


  def stop(self):
    self.running = False
    self.connected = False
