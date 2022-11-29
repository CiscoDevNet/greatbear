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
from flask import Flask

_HTTP_PORT: int = int(os.getenv('HTTP_PORT') or '11777')
_BASE_URL: str = os.getenv('BASE_URL') or '/'
_ECHO_TEXT: str = os.getenv('ECHO_TEXT') or 'Hello World'

app = Flask(__name__)

@app.route(_BASE_URL, methods=['GET'])
def echo():
    return(f'<hr><center><h1>{_ECHO_TEXT}</h1><center><hr>')

def _main():
    print('ECHO_TEXT: ' + _ECHO_TEXT)
    print(f'Started on 0.0.0.0:{_HTTP_PORT}{_BASE_URL}')
    app.run(host='0.0.0.0', port=_HTTP_PORT)

if __name__ == '__main__':
    _main()