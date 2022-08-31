"""Module used to fetch data
"""
import argparse
import datetime
import io
import logging
import re
import sys
import typing
import urllib.parse

import bs4
import PyPDF2
import PyPDF2.errors
import requests

from fuelpricesgr import database, enums, extract, settings


# The module logger
logger = logging.getLogger(__name__)


def pdf_to_text(pdf_file: bytes) -> typing.Optional[str]:
    """Extract text from a PDF file.

    :param pdf_file: The PRF file.
    :return: The text, or None if the file cannot be parsed.
    """
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))

        return ''.join(page.extract_text() for page in reader.pages)
    except PyPDF2.errors.PdfReadError:
        logger.error("Error parsing PDF data", exc_info=True)


def extract_data(fuel_data_type: enums.FuelDataType, date: datetime.date, data: bytes) -> typing.List[dict]:
    """Extract fuel data from a PDF file.

    :param fuel_data_type: The type of fuel data.
    :param date: The date of the file.
    :param data: The PDF file data.
    :return: The extracted data.
    """
    logger.info("Processing data for fuel data type %s and date %s", fuel_data_type, date)
    extractor = extract.get_extractor(fuel_data_type=fuel_data_type)
    if extractor is None:
        logger.warning("Extractor for type %s has not been implemented", fuel_data_type)
        return []

    text = pdf_to_text(data)
    if not text:
        logger.error("Cannot extract text for fuel data type %s and date %s", fuel_data_type, date)
        return []

    return extractor(text)


def process_link(file_link: str, fuel_data_type: enums.FuelDataType, use_file_cache: bool = True, update: bool = False,
                 start_date: datetime.date = None, end_date: datetime.date = None):
    """Process a file link. This function downloads the PDF file if needed, extracts the data from it, and inserts the
    data to the database.

    :param file_link: The file link.
    :param fuel_data_type: The fuel data type.
    :param use_file_cache: True if we are to save the data file to the local storage
    :param update: True if we want to update existing data from the database.
    :param start_date: The start date for the data to process. Can be None.
    :param end_date: The end date for the data to process. Can be None.
    """
    file_name = file_link[file_link.rfind('/') + 1:]
    result = re.search(r'(\d{2})_(\d{2})_(\d{4})', file_name)
    if not result:
        logger.error("Could not find date in file name")
        return
    date = datetime.date(day=int(result[1]), month=int(result[2]), year=int(result[3]))
    if start_date is not None and date > start_date:
        return
    if end_date is not None and date < end_date:
        return

    try:
        if use_file_cache:
            file_path = settings.DATA_PATH / fuel_data_type.name / file_name
            if file_path.exists():
                logger.debug("Loading from local cache")
                with file_path.open('rb') as f:
                    file_data = f.read()
            else:
                logger.info("Fetching file")
                response = requests.get(file_link, stream=True)
                response.raise_for_status()
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_data = response.raw.read()
                with file_path.open('wb') as f:
                    f.write(file_data)
        else:
            logger.info("Fetching file")
            response = requests.get(file_link, stream=True)
            response.raise_for_status()
            file_data = response.raw.read()
    except requests.HTTPError:
        logger.error("Could not fetch link %s", file_link, exc_info=True)
        return

    with database.Database(read_only=False) as db:
        if update or not db.data_exists(fuel_data_type=fuel_data_type, date=date):
            data = extract_data(fuel_data_type=fuel_data_type, date=date, data=file_data)
            for row in data:
                db.insert_fuel_data(fuel_data_type=fuel_data_type, date=date, data=row)
            db.save()


def fetch(fuel_data_types: typing.List[enums.FuelDataType], use_file_cache: bool = True, update: bool = True,
          start_date: datetime.date = None, end_date: datetime.date = None):
    """Fetch the data from the site and insert to the database.

    :param fuel_data_types: The fuel data types to parse.
    :param use_file_cache: True to use the local file cache.
    :param update: True to update the existing data.
    :param start_date: The start date for the data to process. Can be None.
    :param end_date: The end date for the data to process. Can be None.
    """
    logger.info("Fetching missing data from the site")
    for fuel_data_type in enums.FuelDataType:
        if fuel_data_type not in fuel_data_types:
            continue
        page_url = urllib.parse.urljoin(settings.FETCH_URL, fuel_data_type.page)
        logger.info("Processing page %s", page_url)
        response = requests.get(f"{settings.FETCH_URL}/{fuel_data_type.page}")
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('a'):
            if link.has_attr('href') and link['href'].startswith('./files'):
                file_link = link['href'].replace(' ', '')
                file_link = re.sub(r'\(\d\)', '', file_link)
                file_link = re.sub(r'-\?+', '', file_link)
                file_link = urllib.parse.urljoin(settings.FETCH_URL, file_link)
                process_link(
                    file_link=file_link, fuel_data_type=fuel_data_type, use_file_cache=use_file_cache, update=update,
                    start_date=start_date, end_date=end_date
                )


def main():
    """Entry point of the script.
    """
    logging.basicConfig(
        stream=sys.stdout, level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    parser = argparse.ArgumentParser(description='Fetch the data from the site and insert them to the database.')
    parser.add_argument('--types', help=f"Comma separated fuel data types to fetch. Available types are "
                                        f"{','.join(fdt.name for fdt in enums.FuelDataType)}")
    parser.add_argument('--start-date', type=datetime.date.fromisoformat,
                        help="The start date for the data to fetch. The date must be in ISO date format (YYYY-MM-DD)")
    parser.add_argument('--end-date', type=datetime.date.fromisoformat,
                        help="The end date for the data to fetch. The date must be in ISO date format (YYYY-MM-DD)")
    parser.add_argument('--use_file_cache', default=True, action=argparse.BooleanOptionalAction,
                        help="Use the file cache. By default, the file cache is used.")
    parser.add_argument('--update', default=False, action=argparse.BooleanOptionalAction,
                        help="Update existing data. By default existing data are not updated.")
    args = parser.parse_args()
    if args.types:
        try:
            fuel_data_types = [enums.FuelDataType[fdt] for fdt in args.types.split(',')]
        except KeyError:
            print("Could not parse fuel data types")
            return
    else:
        fuel_data_types = enums.FuelDataType
    fetch(
        fuel_data_types=fuel_data_types, use_file_cache=args.use_file_cache, update=args.update,
        start_date=args.start_date, end_date=args.end_date
    )


if __name__ == '__main__':
    main()
