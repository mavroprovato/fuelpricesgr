"""Module for fetching data
"""
import datetime
import logging
import requests

from fuelpricesgr import enums, settings

# The module logger
logger = logging.getLogger(__name__)


class LocalFileFetcher:
    """Class for fetching data files to the local file system.
    """
    # The timeout for fetching data in seconds
    REQUESTS_TIMEOUT = 5

    def __init__(self, data_file_type: enums.DataFileType, date: datetime.date):
        """Create the data fetcher.

        :param data_file_type: The data file type.
        :param date: The date of the file to fetch.
        """
        self.directory = settings.DATA_PATH / 'cache' / data_file_type.value
        self.directory.mkdir(parents=True, exist_ok=True)
        self.data_file_type = data_file_type
        self.date = date

    def fetch_data(self, skip_cache: bool = False):
        """Fetch the data for the specified date and file type.

        :param skip_cache: Do not use file cache.
        :return: The data text, if it can be fetched successfully.
        """
        if self.exists():
            if skip_cache:
                logger.info(
                    "Downloading %s file for date %s again because cache is skipped", self.data_file_type, self.date
                )

                return self.fetch()
            else:
                logger.info("File %s for date %s exists in cache", self.data_file_type, self.date)

                return self.read()
        else:
            logger.info("Downloading %s file for date %s because it does not exist", self.data_file_type, self.date)

            return self.fetch()

    def exists(self) -> bool:
        file = self.directory / f"{self.date.isoformat()}.pdf"

        return file.exists()

    def fetch(self):
        """Download a file to the local cache directory.
        """
        file = self.directory / f"{self.date.isoformat()}.pdf"
        with file.open('wb') as f:
            contents = self.download()
            if contents is not None:
                f.write(contents)

    def read(self) -> bytes:
        file = self.directory / f"{self.date.isoformat()}.pdf"

        return file.read_bytes()

    def download(self) -> bytes | None:
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
