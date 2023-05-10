# Image Uploader

The image uploader component uses a simple python script to look for files in a specified directoy, upload these to an S3 bucket, and then delete the uploaded file. It has been developed and tested using Python 3.9 

The files for the simple image uploader application are found inside the `app/image-uploader` directory. If testing locally with python you will need to define the following environment variables:

| Environment Variable | Description |
|---|---|
| CAMERA_NAME | The directory name inside CACHE_DIRECTORY used as the directory to search for files in. Also used as the directory name in the S3 bucket. |
| AWS_S3_HOST | The url of the S3 bucket host |
| AWS_S3_ACCESS_KEY | The access key to authenticate with the S3 host |
| AWS_S3_SECRET_KEY | The secret key to authenticate with the S3 host |
| AWS_S3_BUCKET | The bucket name to upload files to |
| CACHE_DIRECTORY | The directory to search for files in. **BEWARE: Files in this location will be deleted if successfully uploaded to the S3 bucket!** |

The only requirement is boto3, an SDK to create, configure, and manage AWS services, which can be installed with `pip3 install boto3` or `pip3 install -r requirements.txt`.

Which everything setup and configured correctly, the app can be run with the python command:

```
python3 main.py
```
