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
from prometheus_client import start_http_server
from file_uploader import Uploader


if __name__ == '__main__':

    METRICS_PORT = int(os.environ.get("METRICS_PORT", "9001"))
    start_http_server(METRICS_PORT)

    camera_name = os.environ.get("CAMERA_NAME")
    aws_s3_host = os.environ.get("AWS_S3_HOST")
    aws_s3_access_key = os.environ.get("AWS_S3_ACCESS_KEY")
    aws_s3_secret_key = os.environ.get("AWS_S3_SECRET_KEY")
    aws_s3_bucket = os.environ.get("AWS_S3_BUCKET")
    cache_directory = os.environ.get("CACHE_DIRECTORY")

    uploader = Uploader(camera_name, aws_s3_host, aws_s3_access_key, aws_s3_secret_key, aws_s3_bucket, cache_directory)
    uploader.run()
