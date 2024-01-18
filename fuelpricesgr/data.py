"""Module for fetching data
"""
import datetime
import logging
import pathlib
import re
import urllib.parse
from collections.abc import Generator

import requests
import bs4

from fuelpricesgr import enums, settings

# The module logger
logger = logging.getLogger(__name__)

# The link parsing regex
_LINK_PARSING_REGEX = re.compile(
    r'\./files/deltia/(?P<prefix>[A-Z_]+)_(?P<day>\d{1,2})_(?P<month>\d{2})_(?P<year>\d{4})[ =.?\-()\d]*.(pdf|doc)$'
)


class DataFetcher:
    """Class for fetching data files
    """
    def __init__(self, data_file_type: enums.DataFileType):
        """Create the data fetcher.

        :param data_file_type: The data file type for the fetcher.
        """
        self.data_file_type = data_file_type
        self.cache_dir = settings.DATA_PATH / 'cache'
        self.cache_dir.mkdir(exist_ok=True)

    def fetch_data(
            self, start_date: datetime.date = None, end_date: datetime.date = None
    ) -> Generator[datetime.date, pathlib.Path]:
        """Fetch the data files.

        :param start_date: The date from which to start fetching data.
        :param end_date: The date until
        :return: Yields the date for the file and the file itself.
        """
        # Make sure that the data file type exists
        data_file_type_dir = self.cache_dir / self.data_file_type.value
        data_file_type_dir.mkdir(exist_ok=True)

        # Fetch all the page URLs
        page_url = urllib.parse.urljoin(settings.FETCH_URL, self.data_file_type.page)
        logger.info("Processing page %s", page_url)
        response = requests.get(f"{settings.FETCH_URL}/{self.data_file_type.page}", timeout=settings.REQUESTS_TIMEOUT)
        soup = bs4.BeautifulSoup(response.text, 'html.parser')

        # Process all file links
        for link in reversed(soup.find_all('a')):
            if link.has_attr('href') and link['href'].startswith('./files'):
                match = _LINK_PARSING_REGEX.match(link['href'])
                if not match:
                    logger.warning("Cannot parse link %s", link['href'])
                    continue
                date = datetime.date(
                    year=int(match.group('year')), month=int(match.group('month')), day=int(match.group('day')))
                if (start_date is not None and date < start_date) or (end_date is not None and date > end_date):
                    continue
                file = data_file_type_dir / f"{date.isoformat()}.pdf"

                # Download the file if not exists
                if not file.exists():
                    file_url = urllib.parse.urljoin(
                        settings.FETCH_URL,
                        f"{match.group('prefix')}_{match.group('day')}_{match.group('month')}_{match.group('year')}"
                        f".pdf"
                    )
                    logger.info("Fetching file from %s", file_url)
                    try:
                        response = requests.get(file_url, stream=True, timeout=settings.REQUESTS_TIMEOUT)
                        response.raise_for_status()
                    except requests.RequestException as ex:
                        logger.error("Could not fetch URL", exc_info=ex)
                        continue
                    file_data = response.raw.read()
                    with file.open('wb') as file:
                        file.write(file_data)

                yield date, file
