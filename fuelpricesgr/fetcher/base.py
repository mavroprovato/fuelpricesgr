"""Base module for fetching PDF files.
"""
import abc
import datetime
import logging

from fuelpricesgr import enums

# The module logger
logger = logging.getLogger(__name__)


class BaseFetcher(abc.ABC):
    """Base class for fetching PDF files.
    """
    def __init__(self, data_file_type: enums.DataFileType, date: datetime.date):
        """Create the data fetcher.

        :param data_file_type: The data file type.
        :param date: The date of the file to fetch.
        """
        self.data_file_type = data_file_type
        self.date = date

    def data(self, skip_cache: bool = False) -> bytes:
        """Get the file data for the specified date and file type.

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

    def path(self) -> str:
        """Return the path of the data file.

        :return: The path of the data file.
        """
        return f"{self.data_file_type.value}/{self.date.isoformat()}.pdf"

    @abc.abstractmethod
    def exists(self) -> bool:
        """Check if the data file exists.

        :return: True if the data file exists, False otherwise.
        """

    @abc.abstractmethod
    def read(self) -> bytes:
        """Read the data file from the storage.

        :return: The data file content.
        """

    @abc.abstractmethod
    def fetch(self) -> bytes | None:
        """Fetch the data file from the site, and save it to storage.

        :return: The data file content.
        """
