"""Module for fetching the PDF data to a local file system
"""
import datetime
import logging
import requests

from fuelpricesgr import enums, settings
from .base import BaseFetcher

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
            if contents is not None:
                f.write(contents)

            return contents

    def read(self) -> bytes:
        """Read a file from the local cache directory.

        :return: The file contents.
        """
        file = self.base_directory / self.path()

        return file.read_bytes()

    def download(self) -> bytes | None:
        """Download a file from the site to the local cache directory.

        :return: The file contents.
        """
        # Download the file
        file_url = self.data_file_type.link(self.date)
        logger.info("Downloading file from %s", file_url)
        try:
            response = requests.get(file_url, stream=True, timeout=self.REQUESTS_TIMEOUT)
            response.raise_for_status()
        except requests.RequestException as ex:
            logger.error("Could not download URL for date %s", self.date.isoformat(), exc_info=ex)
            return None

        # Check if response is a PDF file
        if response.headers['content-type'].startswith('text/html'):
            logger.error("File not found for date %s", self.date.isoformat())
            return None
        if response.headers['content-type'] != 'application/pdf':
            logger.error("File is not PDF for date %s", self.date.isoformat())
            return None

        # Return the file contents
        return response.raw.read()
