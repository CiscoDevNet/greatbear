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

import boto3
import logging
import os
import time

from botocore.exceptions import ClientError
from datetime import datetime
from prometheus_client import Counter, Gauge


class Uploader:
    def __init__(self, camera_name, aws_s3_host, aws_s3_access_key, aws_s3_secret_key, aws_s3_bucket, cache_directory):
        logging.getLogger().setLevel(logging.WARN)

        """AWS parameters
        :param camera_name: Used as the directory in the bucket to upload file to
        :param aws_s3_host: S3 bucket host to upload file to
        :param aws_s3_access_key: Access key to authenticate with host
        :param aws_s3_secret_key: Secret key to authenticate with host
        :param aws_s3_bucket: Bucket to upload to
        :param cache_directory: Location to look for images in
        """
        self.camera_name = camera_name
        self.aws_s3_host = aws_s3_host
        self.aws_s3_access_key = aws_s3_access_key
        self.aws_s3_secret_key = aws_s3_secret_key
        self.aws_s3_bucket = aws_s3_bucket
        self.cache_directory = cache_directory
        self.pause = 5  # seconds to wait if something went wrong or no images present

        # metrics
        self.frame_counter = Counter("num_uploaded_files", "Number uploaded files")
        self.exception_ctr = Counter("num_upload_exceptions", "Number upload exceptions")

        # per camera metrics
        camera = self.camera_name.replace('-', '_')
        self.live_ctr = Gauge(f"live_camera_{camera}", "Number live cameras")
        self.live_ctr.inc()
        self.camera_counter = Counter(f"num_uploaded_files_{camera}",
                                      f"Number uploaded files for camera {self.camera_name}")
        self.camera_exceptions = Counter(f"num_exceptions_{camera}",
                                         f"Number exceptions for camera {self.camera_name}")

    def upload_file(self, client, aws_s3_bucket, file_name, object_name):
        """Upload a file to an S3 bucket
        :param client: Client that should be used to connect to AWS S3 
        :param aws_s3_bucket: S3 Bucket to where files should be uploaded to
        :param file_name: File to upload
        :param object_name: S3 object name
        :return: True if file was uploaded, else False
        """

        try:
            response = client.upload_file(file_name, aws_s3_bucket, object_name)
        except ClientError as e:
            logging.error(e)
            self.exception_ctr.inc()
            return False
        return True

    def parse_image_name(self, file_name):
        site, camera, date_and_ext = file_name.split("___")
        date_time_str = os.path.splitext(date_and_ext)[0]
        date_str = date_time_str.split("_")[0]
        time_str = date_time_str.split("_")[-1]
        iso_time_str = time_str.replace("-", ":")
        date_time_str = "".join([date_str, "_", iso_time_str])
        date = datetime.fromisoformat(date_time_str)
        return site, camera, str(date.year), str(date.month).zfill(2), str(date.day).zfill(2), str(
            date.hour).zfill(2), date_and_ext

    def run(self):

        # Create session and connect to AWS S3 host
        session = boto3.session.Session(aws_access_key_id=self.aws_s3_access_key,
                                        aws_secret_access_key=self.aws_s3_secret_key)
        self.client = session.client("s3", endpoint_url=self.aws_s3_host)

        while True:
            # Retrieve the list of files in the specified directory
            try:
                camera_directory = os.path.join(self.cache_directory)
                list_of_files = [os.path.join(camera_directory, file)
                                 for file in os.listdir(camera_directory)]
                logging.debug(list_of_files)
            except Exception as e:
                logging.error(e)
                time.sleep(self.pause)
                continue

            if not list_of_files:
                self.live_ctr.set(0)
                logging.warning("directory is empty - sleeping for 5 seconds")
                time.sleep(self.pause)

            self.live_ctr.set(1)
            # Upload all listed files
            for file_path in list_of_files:
                # Upload the file, and if successful, delete the file
                parts = self.parse_image_name(os.path.basename(file_path))
                upload_object_path = "/".join(parts)
                if self.upload_file(self.client, self.aws_s3_bucket, file_path, upload_object_path):
                    logging.warning(f"{file_path} uploaded to S3")
                    self.frame_counter.inc()
                    self.camera_counter.inc()
                    try:
                        os.remove(os.path.abspath(file_path))
                        logging.info(f"{file_path} deleted from device")
                    except Exception as e:
                        logging.error(e)
                        self.exception_ctr.inc()
                        self.camera_exceptions.inc()
