"""Module used to fetch data
"""
import datetime
import decimal
import json
import logging
import pathlib
import re
import shutil
import sys
import typing

import bs4
import PyPDF2
import PyPDF2.errors
import requests

from fuelpricesgr import enums

# The base URL
BASE_URL = 'http://www.fuelprices.gr'
# The base path where the files will be stored
DATA_PATH = pathlib.Path(__file__).parent.parent / 'var'

# The module logger
logger = logging.getLogger(__name__)


def fetch_data():
    """Fetch data from the site.
    """
    logger.info("Fetching missing data from the site")
    for fuel_data in enums.FuelData:
        response = requests.get(f"{BASE_URL}/{fuel_data.page}")
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('a'):
            if link.has_attr('href') and link['href'].startswith('./files'):
                file_link = link['href'].replace(' ', '')
                file_link = re.sub(r'\(\d\)', '', file_link)
                file_link = re.sub(r'-\?+', '', file_link)
                file_path = DATA_PATH / fuel_data.name / file_link[file_link.rfind('/') + 1:]
                if not file_path.exists():
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_url = f"{BASE_URL}/{file_link}"
                    logger.info(f"Downloading file %s", file_url)
                    with requests.get(file_url, stream=True) as r, file_path.open('wb') as f:
                        shutil.copyfileobj(r.raw, f)
    logger.info("Missing data fetched")


def parse_files():
    """Parse the files and extract fuel prices
    """
    logger.info("Parsing data")
    data = []
    for data_file in pathlib.Path(DATA_PATH).rglob('*.pdf'):
        logger.info("Processing PDF file %s", data_file.name)
        fuel_data = enums.FuelData[data_file.parent.name]
        result = re.search(r'(\d{2})_(\d{2})_(\d{4})', data_file.stem)
        if not result:
            logger.warning("Could not find date in file name")
            continue
        date = datetime.date(day=int(result[1]), month=int(result[2]), year=int(result[3]))
        file_data = extract_data(fuel_data=fuel_data, date=date, data_file=data_file)
        if file_data:
            data += file_data

    with (pathlib.Path(DATA_PATH) / 'data.json').open('wt') as f:
        f.write(json.dumps(data, default=str))

    logger.info("Data parsed")


def extract_data(
        fuel_data: enums.FuelData, date: datetime.date, data_file: pathlib.Path) -> typing.Optional[typing.List[dict]]:
    """Extract fuel data from a PDF file.

    :param fuel_data: The type of fuel data.
    :param date: The date of the file.
    :param data_file: The file.
    :return: The extracted data.
    """
    logger.info("Parsing file %s", data_file)
    if fuel_data != enums.FuelData.DAILY_COUNTRY:
        logger.warning("Parsing files of type %s not implemented yet", fuel_data)
        return None

    text = pdf_to_text(data_file)
    if not text:
        logger.warning("Cannot extract text from PDF file %s", data_file)
        return None

    data = []
    for line in text.splitlines():
        fuel_type = None
        if line.startswith('Αμόλυβδη 95 οκτ.'):
            fuel_type = enums.FuelType.UNLEADED_95
        elif line.startswith('Αμόλυβδη 100 οκτ.'):
            fuel_type = enums.FuelType.UNLEADED_100
        elif line.startswith('Super'):
            fuel_type = enums.FuelType.SUPER
        elif line.startswith('Diesel Κίνησης'):
            fuel_type = enums.FuelType.DIESEL
        elif line.startswith('Diesel Θέρμανσης Κατ΄οίκον'):
            fuel_type = enums.FuelType.DIESEL_HEATING
        elif line.startswith('Υγραέριο κίνησης (Autogas)'):
            fuel_type = enums.FuelType.GAS
        if fuel_type:
            try:
                number_of_stations, price = line.strip().split()[-2:]
                price = decimal.Decimal(price.replace(',', '.'))
                number_of_stations = int(number_of_stations.replace('.', ''))

                data.append({
                    'date': date, 'fuel_type': fuel_type, 'number_of_stations': number_of_stations, 'price': price
                })
            except (ValueError, decimal.DecimalException):
                continue

    return data


def pdf_to_text(pdf_file: pathlib.Path) -> typing.Optional[str]:
    """Extract text from a PDF file.

    :param pdf_file: The PRF file.
    :return: The text, or None if the file cannot be parsed.
    """
    try:
        reader = PyPDF2.PdfReader(pdf_file)

        return ''.join(page.extract_text() for page in reader.pages)
    except PyPDF2.errors.PdfReadError:
        logger.error("Error parsing PDF file %s", pdf_file.name, exc_info=True)


def main():
    """Entry point of the script.
    """
    logging.basicConfig(
        stream=sys.stdout, level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    fetch_data()
    parse_files()


if __name__ == '__main__':
    main()
