"""Module for fetching the PDF data to a local file system
"""
import datetime
import logging
import requests

from fuelpricesgr import enums, settings
from .base import BaseFetcher, FetcherException

# The module logger
logger = logging.getLogger(__name__)


class LocalFileFetcher(BaseFetcher):
    """Class for fetching the PDF data files to the local file system.
    """
    # The timeout for fetching data in seconds
    REQUESTS_TIMEOUT = 5

    def __init__(self, data_file_type: enums.DataFileType, date: datetime.date):
        """Create the data fetcher.

        :param data_file_type: The data file type.
        :param date: The date of the file to fetch.
        """
        super().__init__(data_file_type, date)
        self.base_directory = settings.DATA_PATH / 'cache'

    def exists(self) -> bool:
        """Check if the data file exists.

        :return: True if the data file exists, False otherwise.
        """
        file = self.base_directory / self.path()

        return file.exists()

    def fetch(self) -> bytes:
        """Download a file to the local cache directory and return its contents.

        :return: The file contents.
        """
        file = self.base_directory / self.path()
        file.parent.mkdir(parents=True, exist_ok=True)
        with file.open('wb') as f:
            contents = self.download()
            f.write(contents)

            return contents

    def read(self) -> bytes:
        """Read a file from the local cache directory.

        :return: The file contents.
        :raises FetcherException: If the file could not be downloaded.
        """
        file = self.base_directory / self.path()

        try:
            return file.read_bytes()
        except OSError as ex:
            raise FetcherException(message=f"Could not read file {file}") from ex

    def download(self) -> bytes:
        """Download a file from the site to the local cache directory.

        :return: The file contents.
        :raises FetcherException: If the file could not be downloaded.
        """
        # Download the file
        file_url = self.data_file_type.link(self.date)
        logger.info("Downloading file from %s", file_url)
        try:
            response = requests.get(file_url, stream=True, timeout=self.REQUESTS_TIMEOUT)
            response.raise_for_status()
        except requests.RequestException as ex:
            raise FetcherException(message=f"Could not download file from {file_url}") from ex

        # Check if response is a PDF file
        if response.headers['content-type'].startswith('text/html'):
            raise FetcherException(message=f"File not found at {file_url}")
        if response.headers['content-type'] != 'application/pdf':
            raise FetcherException(message=f"File is not a PDF file at {file_url}")

        # Return the file contents
        return response.raw.read()
