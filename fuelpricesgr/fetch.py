"""Module used to fetch data
"""
import csv
import datetime
import decimal
import enum
import logging
import pathlib
import re
import shutil
import sys

import bs4
import PyPDF2
import PyPDF2.errors
import requests

# The base URL
BASE_URL = 'http://www.fuelprices.gr'
# The base path where the files will be stored
DATA_PATH = pathlib.Path(__file__).parent.parent / 'var'

# The module logger
logger = logging.getLogger(__name__)


class FuelData(enum.Enum):
    """Enumeration for the different types of fuel data.
    """
    WEEKLY = 'deltia.view',
    DAILY_COUNTRY = 'deltia_d.view',
    DAILY_PREFECTURE = 'deltia_dn.view',

    def __init__(self, page: str):
        """Creates the enum.

        :param page: The page path, relative to the base URL, from which we will fetch the data.
        """
        self.page = page


class FuelType(enum.Enum):
    UNLEADED_95 = 'Αμόλυβδη 95'
    UNLEADED_100 = 'Αμόλυβδη 100'
    SUPER = 'Super'
    DIESEL = 'Diesel'
    DIESEL_HEATING = 'Diesel'
    GAS = 'Υγραέριο'


class Prefecture(enum.Enum):
    """Enumeration for greek prefectures
    """
    ATTICA = "ΑΤΤΙΚΗΣ",
    AETOLIA_ACARNANIA = "ΑΙΤΩΛΙΑΣ ΚΑΙ ΑΚΑΡΝΑΝΙΑΣ",
    ARGOLIS = "ΑΡΓΟΛΙΔΟΣ",
    ARKADIAS = "ΑΡΚΑΔΙΑΣ",
    ARTA = "ΑΡΤΗΣ",
    ACHAEA = "ΑΧΑΪΑΣ",
    BOEOTIA = "ΒΟΙΩΤΙΑΣ",
    GREVENA = "ΓΡΕΒΕΝΩΝ",
    DRAMA = "ΔΡΑΜΑΣ",
    DODECANESE = "ΔΩΔΕΚΑΝΗΣΟΥ",
    EVROS = "ΕΒΡΟΥ",
    EUBOEA = "ΕΥΒΟΙΑΣ",
    EVRYTANIA = "ΕΥΡΥΤΑΝΙΑΣ",
    ZAKYNTHOS = "ΖΑΚΥΝΘΟΥ",
    ELIS = "ΗΛΕΙΑΣ",
    IMATHIA = "ΗΜΑΘΙΑΣ",
    HERAKLION = "ΗΡΑΚΛΕΙΟΥ",
    THESPROTIA = "ΘΕΣΠΡΩΤΙΑΣ",
    THESSALONIKI = "ΘΕΣΣΑΛΟΝΙΚΗΣ",
    IOANNINA = "ΙΩΑΝΝΙΝΩΝ",
    KAVALA = "ΚΑΒΑΛΑΣ",
    KARDITSA = "ΚΑΡΔΙΤΣΗΣ",
    KASTORIA = "ΚΑΣΤΟΡΙΑΣ",
    KERKYRA = "ΚΕΡΚΥΡΑΣ",
    CEPHALONIA = "ΚΕΦΑΛΛΗΝΙΑΣ",
    KILKIS = "ΚΙΛΚΙΣ",
    KOZANI = "ΚΟΖΑΝΗΣ",
    CORINTHIA = "ΚΟΡΙΝΘΙΑΣ",
    CYCLADES = "ΚΥΚΛΑΔΩΝ",
    LACONIA = "ΛΑΚΩΝΙΑΣ",
    LARISSA = "ΛΑΡΙΣΗΣ",
    LASITHI = "ΛΑΣΙΘΙΟΥ",
    LESBOS = "ΛΕΣΒΟΥ",
    LEFKADA = "ΛΕΥΚΑΔΟΣ",
    MAGNESIA = "ΜΑΓΝΗΣΙΑΣ",
    MESSENIA = "ΜΕΣΣΗΝΙΑΣ",
    XANTHI = "ΞΑΝΘΗΣ",
    PELLA = "ΠΕΛΛΗΣ",
    PIERIA = "ΠΙΕΡΙΑΣ",
    PREVEZA = "ΠΡΕΒΕΖΗΣ",
    RETHYMNO = "ΡΕΘΥΜΝΗΣ",
    RHODOPE = "ΡΟΔΟΠΗΣ",
    SAMOS = "ΣΑΜΟΥ",
    SERRES = "ΣΕΡΡΩΝ",
    TRIKALA = "ΤΡΙΚΑΛΩΝ",
    PHTHIOTIS = "ΦΘΙΩΤΙΔΟΣ",
    FLORINA = "ΦΛΩΡΙΝΗΣ",
    PHOCIS = "ΦΩΚΙΔΟΣ",
    CHALKIDIKI = "ΧΑΛΚΙΔΙΚΗΣ",
    CHANIA = "ΧΑΝΙΩΝ",
    CHIOS = "ΧΙΟΥ",

    def __init__(self, display_name: str):
        """Creates the enum.

        :param display_name: The name of the prefecture in Greek.
        """
        self.display_name = display_name


def fetch_data():
    """Fetch data from the site.
    """
    for fuel_data in FuelData:
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


def parse_files():
    """Parse the files and extract fuel prices
    """
    data = []
    for data_file in pathlib.Path(DATA_PATH).rglob('*.pdf'):
        logger.info("Processing PDF file %s", data_file.name)
        fuel_data = FuelData[data_file.parent.name]
        # TODO: remove this
        if fuel_data != FuelData.DAILY_COUNTRY:
            continue
        result = re.search(r'(\d{2})_(\d{2})_(\d{4})', data_file.stem)
        if not result:
            logger.warning("Could not find date in file name")
            continue
        date = datetime.date(day=int(result[1]), month=int(result[2]), year=int(result[3]))
        try:
            reader = PyPDF2.PdfReader(data_file)
            text = ''.join(page.extract_text() for page in reader.pages)
            for line in text.splitlines():
                fuel_type = None
                if line.startswith('Αμόλυβδη 95 οκτ.'):
                    fuel_type = FuelType.UNLEADED_95
                elif line.startswith('Αμόλυβδη 100 οκτ.'):
                    fuel_type = FuelType.UNLEADED_100
                elif line.startswith('Super'):
                    fuel_type = FuelType.SUPER
                elif line.startswith('Diesel Κίνησης'):
                    fuel_type = FuelType.DIESEL
                elif line.startswith('Diesel Θέρμανσης Κατ΄οίκον'):
                    fuel_type = FuelType.DIESEL_HEATING
                elif line.startswith('Υγραέριο κίνησης (Autogas)'):
                    fuel_type = FuelType.GAS
                if fuel_type:
                    try:
                        number_of_stations, price = line.strip().split()[-2:]
                        price = decimal.Decimal(price.replace(',', '.'))
                        number_of_stations = int(number_of_stations.replace('.', ''))
                        data.append((date, fuel_type, number_of_stations, price))
                    except (ValueError, decimal.DecimalException):
                        continue
        except PyPDF2.errors.PdfReadError:
            logger.error("Error parsing PDF file %s", data_file.name, exc_info=True)

        with (DATA_PATH / 'data.csv').open('wt') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(('date', 'fuel_type', 'number_of_stations', 'price'))
            for date, fuel_type, number_of_stations, price in data:
                csv_writer.writerow((date.isoformat(), fuel_type.name, number_of_stations, price))


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    parse_files()
