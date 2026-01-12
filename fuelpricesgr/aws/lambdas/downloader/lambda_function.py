"""The downloader lambda function.
"""
import dataclasses
from typing import Mapping, Any
import urllib.request
import urllib.error

import boto3
import botocore.exceptions


@dataclasses.dataclass
class Parameters:
    """The parameters for the downloader.
    """
    bucket_name: str  # The bucket name
    url: str  # The URL to download
    key: str  # The S3 key where the file will be saved


class DownloaderException(Exception):
    """Exception raised when the download fails.
    """
    def __init__(self, message: str, client_error: bool = False, detail: dict = None):
        """Create the exception.

        :param message: The exception message.
        :param detail:
        """
        self.message = message
        self.client_error = client_error
        self.detail = detail


def download_file(bucket_name: str, url: str, key: str) -> bool:
    """Download a file and save it to the S3 bucket.

    :param bucket_name: The name of the s3 bucket.
    :param url: The URL of the file to download.
    :param key: The S3 key where the file is to be downloaded.
    :return True if the file existed in cache, False otherwise.
    """
    s3_client = boto3.client('s3')
    try:
        # Check if file exists
        s3_client.head_object(Bucket=bucket_name, Key=key)

        return True
    except botocore.exceptions.ClientError:
        # The file does not exist in the bucket, try to download it
        try:
            response = urllib.request.urlopen(url)
            if response.headers['content-type'].startswith('text/html'):
                raise DownloaderException(message="File not found")
            if response.headers['content-type'] != 'application/pdf':
                raise DownloaderException(message="File is not a PDF")

            data = response.read()
            s3_client.put_object(Bucket=bucket_name, Key=key, Body=data)

            return False
        except urllib.error.HTTPError as ex:
            raise DownloaderException(message="Could not download file", detail={"detail": str(ex)})


def get_parameters(event: Mapping) -> Parameters:
    """Get the parameters from the event.

    :param event: The event.
    :return: The parameters.
    """
    required_keys = ['bucket_name', 'url', 'key']
    parameters = {}
    errors = {}
    for key in required_keys:
        if key in event:
            parameters[key] = event[key]
        else:
            errors[key] = f"Missing required parameter: {key}"

    if errors:
        raise DownloaderException(message='Parameters missing', client_error=True, detail=errors)

    return Parameters(**parameters)


def lambda_handler(event: Mapping, _) -> Mapping[str, Any]:
    """Entry point for the lambda function.

    :param event: The event.
    :param _: The lambda context.
    :return: The response.
    """
    try:
        params = get_parameters(event)
        exists = download_file(bucket_name=params.bucket_name, url=params.url, key=params.key)

        return {'status': 200, 'message': 'File exists' if exists else 'File downloaded', 'key': params.key}
    except DownloaderException as ex:
        return {'status': 400 if ex.client_error else 500, 'message': ex.message, 'detail': ex.detail}
