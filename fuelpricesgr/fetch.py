"""Module used to fetch data
"""
import datetime
import io
import logging
import re
import urllib.parse

import bs4
import PyPDF2
import PyPDF2.errors
import requests

from fuelpricesgr import enums, extract, settings

# The module logger
logger = logging.getLogger(__name__)


def pdf_to_text(pdf_file: bytes) -> str | None:
    """Extract text from a PDF file.

    :param pdf_file: The PRF file.
    :return: The text, or None if the file cannot be parsed.
    """
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))

        return ''.join(page.extract_text() for page in reader.pages)
    except PyPDF2.errors.PdfReadError:
        logger.error("Error parsing PDF data", exc_info=True)

        return None


def extract_data(
        data_file_type: enums.DataFileType, date: datetime.date, data: bytes) -> dict[enums.DataType, list[dict]]:
    """Extract fuel data from a PDF file.

    :param data_file_type: The type of fuel data.
    :param date: The date of the file.
    :param data: The PDF file data.
    :return: The extracted data.
    """
    logger.info("Processing data for data file type %s and date %s", data_file_type, date)
    extractor = extract.get_extractor(data_file_type=data_file_type)
    if extractor is None:
        logger.warning("Extractor for data file type %s has not been implemented", data_file_type)
        return {}

    text = pdf_to_text(data)
    if not text:
        logger.error("Cannot extract text for data file type %s and date %s", data_file_type, date)
        return {}

    return extractor(text)


def get_date_from_file_name(file_name: str) -> datetime.date | None:
    """Return the date from a file name.

    :param file_name: The file name.
    :return: The date if found.
    """
    result = re.search(r'(\d{2})_(\d{2})_(\d{4})', file_name)
    if not result:
        logger.error("Could not find date in file name")
        return None

    return datetime.date(day=int(result[1]), month=int(result[2]), year=int(result[3]))


def fetch_data(file_link: str, data_file_type: enums.DataFileType, skip_file_cache: bool = False) -> bytes | None:
    """Fetch data from a file link.

    :param file_link: The file link.
    :param data_file_type: The data file type.
    :param skip_file_cache: True if we are going to skip the local storage for
    """
    file_name = file_link[file_link.rfind('/') + 1:]
    try:
        if skip_file_cache:
            logger.info("Fetching file %s", file_link)
            response = requests.get(file_link, stream=True, timeout=settings.REQUESTS_TIMEOUT)
            response.raise_for_status()
            file_data = response.raw.read()
        else:
            file_path = settings.DATA_PATH / data_file_type.name / file_name
            if file_path.exists():
                logger.debug("Loading from local cache")
                with file_path.open('rb') as file:
                    file_data = file.read()
            else:
                logger.info("Fetching file %s", file_link)
                response = requests.get(file_link, stream=True, timeout=settings.REQUESTS_TIMEOUT)
                response.raise_for_status()
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_data = response.raw.read()
                with file_path.open('wb') as file:
                    file.write(file_data)

        return file_data
    except requests.HTTPError:
        logger.error("Could not fetch link %s", file_link, exc_info=True)
        return


def fetch_link(
        data_file_type: enums.DataFileType, start_date: datetime.date = None, end_date: datetime.date = None
) -> (datetime.date, str):
    """Fetch the data from the site and insert to the database.

    :param start_date: The start date for the data to process. Can be None.
    :param end_date: The end date for the data to process. Can be None.
    :param data_file_type: The data file type to parse.
    """
    page_url = urllib.parse.urljoin(settings.FETCH_URL, data_file_type.page)
    logger.info("Processing page %s", page_url)
    response = requests.get(f"{settings.FETCH_URL}/{data_file_type.page}", timeout=settings.REQUESTS_TIMEOUT)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    for link in soup.find_all('a'):
        if link.has_attr('href') and link['href'].startswith('./files'):
            file_link = link['href'].replace(' ', '')
            file_link = re.sub(r'\(\d\)', '', file_link)
            file_link = re.sub(r'-\?+', '', file_link)
            file_link = urllib.parse.urljoin(settings.FETCH_URL, file_link)
            file_name = file_link[file_link.rfind('/') + 1:]
            date = get_date_from_file_name(file_name)

            if start_date is not None and date < start_date:
                continue
            if end_date is not None and date > end_date:
                continue
            yield date, file_link
