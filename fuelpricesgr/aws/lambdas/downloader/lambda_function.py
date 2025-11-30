"""The downloader lambda function.
"""
from typing import Mapping, Any
import urllib.request
import urllib.error

import boto3
import botocore.exceptions

# The bucket name
BUCKET_NAME = 'fuelpricesgr-data'

# The S3 client
s3_client = boto3.client('s3')


def download_file(url: str, key: str) -> Mapping[str, Any]:
    """Download a file and save it to the S3 bucket.

    :param url: The URL of the file to download.
    :param key: The S3 key where the file is to be downloaded.
    :return :A dictionary with the following keys:
        * status: 200 if the download was successful, 500 if the download failed.
        * message: The message. If the file was downloaded successfully, it provides information whether the file was
        downloaded or it already existed. In case of an error, the error message is returned.
        * bucket: The S3 bucket where the file was downloaded when successful.
        * key: The S3 key where the file was downloaded when successful.
    """
    try:
        s3_client.head_object(Bucket=BUCKET_NAME, Key=key)

        result = {
            'status': 200,
            'message': 'File exists',
            'bucket': BUCKET_NAME,
            'key': key
        }
    except botocore.exceptions.ClientError:
        try:
            response = urllib.request.urlopen(url)
            data = response.read()
            s3_client.put_object(Bucket=BUCKET_NAME, Key=key, Body=data)

            result = {
                'status': 200,
                'message': 'File downloaded',
                'bucket': BUCKET_NAME,
                'key': key
            }
        except urllib.error.HTTPError as ex:
            result = {
                'status': 500,
                'message': f"Could not download file: ${ex}"
            }

    return result


def lambda_handler(event: Mapping, _) -> Mapping[str, Any]:
    """Entry point for the lambda function.

    :param event: The event.
    :param _: The lambda context.
    :return: The response.
    """
    url = event.get('url')
    if url is None:
        result = {
            'status': 400,
            'message': 'No url provided'
        }
        return result
    key = event.get('key')
    if key is None:
        result = {
            'status': 400,
            'message': 'No S3 key provided'
        }
        return result

    return download_file(url, key)
