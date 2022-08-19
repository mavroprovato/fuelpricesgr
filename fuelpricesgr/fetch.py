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

from fuelpricesgr import database, enums, settings

# The base URL
BASE_URL = 'http://www.fuelprices.gr'

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
                file_path = settings.DATA_PATH / fuel_data.name / file_link[file_link.rfind('/') + 1:]
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
    with database.Database() as db:
        for data_file in pathlib.Path(settings.DATA_PATH).rglob('*.pdf'):
            logger.info("Processing PDF file %s", data_file.name)
            fuel_data = enums.FuelData[data_file.parent.name]
            result = re.search(r'(\d{2})_(\d{2})_(\d{4})', data_file.stem)
            if not result:
                logger.warning("Could not find date in file name")
                continue
            date = datetime.date(day=int(result[1]), month=int(result[2]), year=int(result[3]))
            file_data = extract_data(fuel_data=fuel_data, date=date, data_file=data_file)
            for row in file_data:
                db.insert_daily_country_data(
                    date=date, fuel_type=row['fuel_type'], number_of_stations=row['number_of_stations'],
                    price=row['price']
                )
            db.save()

    logger.info("Data parsed")


def extract_data(
        fuel_data: enums.FuelData, date: datetime.date, data_file: pathlib.Path) -> typing.List[dict]:
    """Extract fuel data from a PDF file.

    :param fuel_data: The type of fuel data.
    :param date: The date of the file.
    :param data_file: The file.
    :return: The extracted data.
    """
    logger.info("Parsing file %s", data_file)
    if fuel_data != enums.FuelData.DAILY_COUNTRY:
        logger.warning("Parsing files of type %s not implemented yet", fuel_data)
        return []

    text = pdf_to_text(data_file)
    if not text:
        logger.warning("Cannot extract text from PDF file %s", data_file)
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
                logger.error("Could not get prices for file %s and fuel type %s", data_file, fuel_type)
                continue
        else:
            logger.error("No price data for file %s and fuel type %s", data_file, fuel_type)
            continue

        try:
            number_of_stations = int(number_of_stations_str.replace('.', ''))
            price = decimal.Decimal(price_str.replace(',', '.'))
            data.append({
                'date': date, 'fuel_type': fuel_type, 'number_of_stations': number_of_stations, 'price': price
            })
        except (ValueError, decimal.DecimalException):
            logger.error("Could not parse prices for file %s and fuel type %s", data_file, fuel_type)

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
