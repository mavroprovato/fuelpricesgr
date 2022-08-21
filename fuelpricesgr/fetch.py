"""Module used to fetch data
"""
import datetime
import decimal
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

from fuelpricesgr import database, enums, settings

# The base URL
BASE_URL = 'http://www.fuelprices.gr'

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
    if fuel_data_type != enums.FuelDataType.DAILY_COUNTRY:
        logger.warning("Parsing files of type %s not implemented yet", fuel_data_type)
        return []

    text = pdf_to_text(data)
    if not text:
        logger.warning("Cannot extract text for fuel data type %s and date %s", fuel_data_type, date)
        return []

    data = []
    for line in text.splitlines():
        line = ' '.join(line.strip().split())

        if match := re.search(r'^Αμόλ[υσ]βδ[ηθ] 95 οκ[τη]\.', line):
            fuel_type = enums.FuelType.UNLEADED_95
        elif match := re.search(r'^Αμόλ[υσ]βδ[ηθ] 100 ο ?κ ?[τη]\.', line):
            fuel_type = enums.FuelType.UNLEADED_100
        elif match := re.search(r'^Super', line):
            fuel_type = enums.FuelType.SUPER
        elif match := re.search(r'^Diesel Κί ?ν[ηθ][σζς][ηθ] ?[ςσ]', line):
            fuel_type = enums.FuelType.DIESEL
        elif match := re.search(r'^Diesel Θ[έζ]ρμαν[ζσς][ηθ][ςσ] Κα[τη]΄οίκον', line):
            fuel_type = enums.FuelType.DIESEL_HEATING
        elif match := re.search(r'^Υγρα[έζ]ριο κί ?ν[ηθ] ?[σςζ] ?[ηθ][ςσ]', line):
            fuel_type = enums.FuelType.GAS
        else:
            continue

        line = line[match.span(0)[1] + 1:]
        parts = line.strip().split()
        if len(parts) == 2:
            number_of_stations_str = parts[0]
            price_str = parts[1]
        elif len(parts) == 3:
            if parts[1].find(','):
                number_of_stations_str = parts[0]
                price_str = parts[1] + parts[2]
            elif parts[1].find('.'):
                number_of_stations_str = parts[0] + parts[1]
                price_str = parts[2]
            else:
                logger.error("Could not get prices for fuel data type %s, %s and fuel type %s", fuel_data_type, date,
                             fuel_type)
                continue
        else:
            logger.error("No price data for fuel data type %s, %s and fuel type %s", fuel_data_type, date, fuel_type)
            continue

        try:
            number_of_stations = int(number_of_stations_str.replace('.', ''))
            price = decimal.Decimal(price_str.replace(',', '.'))
            data.append({
                'fuel_type': fuel_type, 'number_of_stations': number_of_stations, 'price': price
            })
        except (ValueError, decimal.DecimalException):
            logger.error("Could not parse prices for fuel data type %s, %s and fuel type %s", fuel_data_type, date,
                         fuel_type)

    return data


def process_link(file_link: str, fuel_data_type: enums.FuelDataType, use_file_cache: bool = True):
    """Process a file link. This function downloads the PDF file if needed, extracts the data from it, and inserts the
    data to the database.

    :param file_link: The file link.
    :param fuel_data_type: The fuel data type.
    :param use_file_cache: True if we are to save the data file to the local storage
    :return:
    """
    file_name = file_link[file_link.rfind('/') + 1:]
    result = re.search(r'(\d{2})_(\d{2})_(\d{4})', file_name)
    if not result:
        logger.warning("Could not find date in file name")
        return
    date = datetime.date(day=int(result[1]), month=int(result[2]), year=int(result[3]))
    try:
        if use_file_cache:
            file_path = settings.DATA_PATH / fuel_data_type.name / file_name
            if file_path.exists():
                logger.info("Loading from local cache")
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

    data = extract_data(fuel_data_type=fuel_data_type, date=date, data=file_data)
    with database.Database(read_only=False) as db:
        for row in data:
            db.insert_fuel_data(fuel_data_type=fuel_data_type, date=date, data=row)
        db.save()


def main():
    """Entry point of the script.
    """
    logging.basicConfig(
        stream=sys.stdout, level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    logger.info("Fetching missing data from the site")
    for fuel_data_type in enums.FuelDataType:
        page_url = urllib.parse.urljoin(BASE_URL, fuel_data_type.page)
        logger.info("Processing page %s", page_url)
        response = requests.get(f"{BASE_URL}/{fuel_data_type.page}")
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('a'):
            if link.has_attr('href') and link['href'].startswith('./files'):
                file_link = link['href'].replace(' ', '')
                file_link = re.sub(r'\(\d\)', '', file_link)
                file_link = re.sub(r'-\?+', '', file_link)
                file_link = urllib.parse.urljoin(BASE_URL, file_link)
                process_link(file_link=file_link, fuel_data_type=fuel_data_type)


if __name__ == '__main__':
    main()
