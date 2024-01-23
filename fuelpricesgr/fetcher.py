"""Module for fetching data
"""
from collections.abc import Generator
import datetime
import logging
import pathlib
import re
import urllib.parse

import requests
import bs4

from fuelpricesgr import enums, parser, settings

# The module logger
logger = logging.getLogger(__name__)


class Fetcher:
    """Class for fetching data files
    """
    # The link parsing regex
    LINK_PARSING_REGEX = re.compile(
        r'\./files/deltia/(?P<prefix>[A-Z_]+)_(?P<day>\d{1,2})_(?P<month>\d{2})_(?P<year>\d{4})[ =.?\-()\d]*.(pdf|doc)$'
    )

    def __init__(self, data_file_type: enums.DataFileType):
        """Create the data fetcher.

        :param data_file_type: The data file type for the fetcher.
        """
        self.data_file_type = data_file_type
        self.cache_dir = settings.DATA_PATH / 'cache'
        self.cache_dir.mkdir(exist_ok=True)
        self.file_parser = parser.Parser(data_file_type=data_file_type)

    def dates(self, start_date: datetime.date = None, end_date: datetime.date = None) -> Generator[datetime.date]:
        """Fetch the available dates for the data files between two dates.

        :param start_date: The date from which to start fetching data.
        :param end_date: The date until which to stop fetching data.
        :return: Yields the date for the file.
        """
        # Fetch all the page URLs
        page_url = urllib.parse.urljoin(settings.FETCH_URL, self.data_file_type.page)
        logger.info("Processing page %s", page_url)
        response = requests.get(f"{settings.FETCH_URL}/{self.data_file_type.page}", timeout=settings.REQUESTS_TIMEOUT)
        soup = bs4.BeautifulSoup(response.text, 'html.parser')

        # Process all file links
        for link in reversed(soup.find_all('a')):
            if not link.has_attr('href') or not link['href'].startswith('./files'):
                continue
            # Extract date from link
            match = self.LINK_PARSING_REGEX.match(link['href'])
            if not match:
                logger.warning("Cannot parse link %s", link['href'])
                continue
            date = datetime.date(
                year=int(match.group('year')), month=int(match.group('month')), day=int(match.group('day')))
            if (start_date is None or date >= start_date) or (end_date is None or date <= end_date):
                yield date

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
            logger.info("Fetching file from %s", file_url)
            try:
                response = requests.get(file_url, stream=True, timeout=settings.REQUESTS_TIMEOUT)
                response.raise_for_status()
            except requests.RequestException as ex:
                logger.error("Could not fetch URL", exc_info=ex)
                return {}

            # Check if response is a PDF file
            if response.headers['content-type'] != 'application/pdf':
                logger.error("File is not PDF")
                return {}

            # Download the file
            file_data = response.raw.read()
            with file.open('wb') as f:
                f.write(file_data)

            # Check if empty
            if file.stat().st_size == 0:
                logger.error("File is empty")
                file.unlink(missing_ok=True)
                return {}

        return self.file_parser.parse(file, date) or {}

    def path_for_date(self, date: datetime.date) -> pathlib.Path:
        """Get the file path for the specified date. The file may not exist.

        :param date: The date.
        :return: The file.
        """
        data_file_type_dir = self.cache_dir / self.data_file_type.value
        data_file_type_dir.mkdir(exist_ok=True)
        file = data_file_type_dir / f"{date.isoformat()}.pdf"

        return file
