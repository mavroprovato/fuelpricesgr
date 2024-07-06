"""Module for fetching data
"""
import datetime
import logging
import pathlib

import requests

from fuelpricesgr import enums, parser, settings

# The module logger
logger = logging.getLogger(__name__)


class Fetcher:
    """Class for fetching data files
    """
    # The timeout for fetching data in seconds
    REQUESTS_TIMEOUT = 5

    def __init__(self, data_file_type: enums.DataFileType):
        """Create the data fetcher.

        :param data_file_type: The data file type for the fetcher.
        """
        self.data_file_type = data_file_type
        self.cache_dir = settings.DATA_PATH / 'cache'
        self.cache_dir.mkdir(exist_ok=True)
        self.file_parser = parser.Parser.get(data_file_type=data_file_type)

    def data(self, date: datetime.date, skip_cache: bool = False) -> dict[enums.DataType, list[dict]] | None:
        """Get the data for the specified date.

        :param date: The date.
        :param skip_cache: Do not use file cache.
        :return: The data text, if it can be fetched successfully.
        """
        file = self.path_for_date(date)
        if not file.exists() or skip_cache:
            # Download the file
            file_url = self.data_file_type.link(date)
            logger.debug("Downloading file from %s", file_url)
            try:
                response = requests.get(file_url, stream=True, timeout=self.REQUESTS_TIMEOUT)
                response.raise_for_status()
            except requests.RequestException as ex:
                logger.error("Could not download URL for date %s", date.isoformat(), exc_info=ex)
                return {}

            # Check if response is a PDF file
            if response.headers['content-type'].startswith('text/html'):
                logger.error("File not found for date %s", date.isoformat())
                return {}
            if response.headers['content-type'] != 'application/pdf':
                logger.error("File is not PDF for date %s", date.isoformat())
                return {}

            # Download the file
            file_data = response.raw.read()
            with file.open('wb') as f:
                f.write(file_data)

        return self.file_parser.parse(file=file) or {}

    def path_for_date(self, date: datetime.date) -> pathlib.Path:
        """Get the file path for the specified date. The file may not exist.

        :param date: The date.
        :return: The file.
        """
        data_file_type_dir = self.cache_dir / self.data_file_type.value
        data_file_type_dir.mkdir(exist_ok=True)
        file = data_file_type_dir / f"{date.isoformat()}.pdf"

        return file
