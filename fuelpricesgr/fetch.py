"""Module used to fetch data
"""
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
DATA_PATH = pathlib.Path('../var')

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
    for data_file in pathlib.Path(DATA_PATH).rglob('*.pdf'):
        logger.info("Parsing PDF file %s", data_file.name)
        try:
            reader = PyPDF2.PdfReader(data_file)
            lines = 0
            for page in reader.pages:
                for line in page.extract_text().splitlines():
                    lines += 1
            logger.info("Parsed %d lines", lines)
        except PyPDF2.errors.PdfReadError:
            logger.error("Error parsing PDF file %s", data_file.name, exc_info=True)


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    parse_files()
