"""Module for fetching PDF data to an AWS S3 bucket.
"""
import datetime
import functools
import json
import logging

import boto3

from fuelpricesgr import enums, settings
from .base import BaseFetcher, FetcherException

# The module logger
logger = logging.getLogger(__name__)


class S3Fetcher(BaseFetcher):
    """Class for fetching the PDF data files to an AWS S3 bucket.
    """
    REQUIRED_SETTINGS = ['AWS_S3_BUCKET_NAME', 'AWS_LAMBDA_REGION_NAME']

    def __init__(self, data_file_type: enums.DataFileType, date: datetime.date):
        """Create the data fetcher.

        :param data_file_type: The data file type.
        :param date: The date of the file to fetch.
        """
        super().__init__(data_file_type, date)
        self.check_configuration()

    @staticmethod
    def check_configuration():
        """Check the configuration for the data fetcher.
        """
        missing_settings = []
        for setting in S3Fetcher.REQUIRED_SETTINGS:
            if getattr(settings, setting) is None:
                missing_settings.append(setting)

        if missing_settings:
            raise RuntimeError(f"Missing required settings: {', '.join(missing_settings)}")

    @classmethod
    @functools.cache
    def s3_client(cls):
        """Return the S3 client. The client is created once per process.

        :return: The S3 client.
        """
        return boto3.client(
            's3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )

    @classmethod
    @functools.cache
    def lambda_client(cls):
        """Return the Lambda client. The client is created once per process.

        :return: The Lambda client.
        """
        return boto3.client(
            'lambda', region_name=settings.AWS_LAMBDA_REGION_NAME, aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )

    def exists(self) -> bool:
        """Check if the data file exists.

        :return: True if the data file exists, False otherwise.
        """
        try:
            self.s3_client().head_object(Bucket=settings.AWS_S3_BUCKET_NAME, Key=self.path())

            return True
        except self.s3_client().exceptions.ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False

            raise e

    def read(self) -> bytes:
        """Read the data file content.

        :return: The data file content.
        """
        return self.s3_client().get_object(Bucket=settings.AWS_S3_BUCKET_NAME, Key=self.path())['Body'].read()

    def fetch(self) -> bytes:
        """Fetch the data file content.

        :return: The data file content.
        """
        response = self.lambda_client().invoke(
            FunctionName='fuelpricesgr-downloader',
            Payload=json.dumps({
                'bucket_name': settings.AWS_S3_BUCKET_NAME, 'url': self.data_file_type.link(date=self.date),
                'key': self.path()
            })
        )
        response_body = json.loads(response['Payload'].read())
        if response_body.get('status') != 200:
            raise FetcherException(f"Could not fetch data file: {response_body}")

        return self.read()
