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


class ParameterException(Exception):
    """Exception raised when the parameters are invalid.
    """


class DownloaderException(Exception):
    """Exception raised when the download fails.
    """
    def __init__(self, message: str, not_found: bool = False):
        """Create the exception.

        :param message: The exception message.
        :param not_found: If the file was not found.
        """
        super().__init__(message)
        self.message = message
        self.not_found = not_found


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
    except botocore.exceptions.ClientError as ex:
        # The file does not exist in the bucket, try to download it
        try:
            with urllib.request.urlopen(url) as response:
                if response.headers['content-type'].startswith('text/html'):
                    raise DownloaderException(message="File not found", not_found=True) from ex
                if response.headers['content-type'] != 'application/pdf':
                    raise DownloaderException(message="File is not a PDF") from ex

                data = response.read()
                s3_client.put_object(Bucket=bucket_name, Key=key, Body=data)

                return False
        except urllib.error.HTTPError as http_ex:
            raise DownloaderException(message=f"Could not download file: {http_ex}") from ex


def get_parameters(event: Mapping) -> Parameters:
    """Get the parameters from the event.

    :param event: The event.
    :return: The parameters.
    """
    required_keys = ['bucket_name', 'url', 'key']
    parameters = {}
    missing_keys = []
    for key in required_keys:
        if key in event:
            parameters[key] = event[key]
        else:
            missing_keys.append(key)

    if missing_keys:
        raise ParameterException(f"Missing required parameters: {', '.join(missing_keys)}")

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
    except ParameterException as ex:
        return {'status': 400, 'message': str(ex)}
    except DownloaderException as ex:
        return {'status': 404 if ex.not_found else 500, 'message': ex.message}
