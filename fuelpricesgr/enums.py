"""The project enums
"""
from collections.abc import Iterable, Generator
import datetime
import enum


class ApplicationStatus(enum.Enum):
    """Enumeration for the application status.
    """
    OK = 'ok'
    ERROR = 'error'


class FuelType(enum.Enum):
    """Enumeration for the different fuel types
    """
    UNLEADED_95 = 'UNLEADED_95', "Αμόλυβδη 95"
    UNLEADED_100 = 'UNLEADED_100', "Αμόλυβδη 100"
    SUPER = 'SUPER', "Super"
    DIESEL = 'DIESEL', "Diesel"
    DIESEL_HEATING = 'DIESEL_HEATING', "Diesel Θέρμανσης"
    GAS = 'GAS', "Υγραέριο"

    def __new__(cls, value: str, description: str):
        """Creates the enum.

        :param value: The enum value.
        :param description: The description.
        """
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description

        return obj


class Prefecture(enum.Enum):
    """Enumeration for greek prefectures
    """
    ATTICA = 'ATTICA', "ΑΤΤΙΚΗΣ"
    AETOLIA_ACARNANIA = 'AETOLIA_ACARNANIA', "ΑΙΤΩΛΙΑΣ ΚΑΙ ΑΚΑΡΝΑΝΙΑΣ"
    ARGOLIS = 'ARGOLIS', "ΑΡΓΟΛΙΔΟΣ"
    ARKADIAS = 'ARKADIAS', "ΑΡΚΑΔΙΑΣ"
    ARTA = 'ARTA', "ΑΡΤΗΣ"
    ACHAEA = 'ACHAEA', "ΑΧΑΪΑΣ"
    BOEOTIA = 'BOEOTIA', "ΒΟΙΩΤΙΑΣ"
    GREVENA = 'GREVENA', "ΓΡΕΒΕΝΩΝ"
    DRAMA = 'DRAMA', "ΔΡΑΜΑΣ"
    DODECANESE = 'DODECANESE', "ΔΩΔΕΚΑΝΗΣΟΥ"
    EVROS = 'EVROS', "ΕΒΡΟΥ"
    EUBOEA = 'EUBOEA', "ΕΥΒΟΙΑΣ"
    EVRYTANIA = 'EVRYTANIA', "ΕΥΡΥΤΑΝΙΑΣ"
    ZAKYNTHOS = 'ZAKYNTHOS', "ΖΑΚΥΝΘΟΥ"
    ELIS = 'ELIS', "ΗΛΕΙΑΣ"
    IMATHIA = 'IMATHIA', "ΗΜΑΘΙΑΣ"
    HERAKLION = 'HERAKLION', "ΗΡΑΚΛΕΙΟΥ"
    THESPROTIA = 'THESPROTIA', "ΘΕΣΠΡΩΤΙΑΣ"
    THESSALONIKI = 'THESSALONIKI', "ΘΕΣΣΑΛΟΝΙΚΗΣ"
    IOANNINA = 'IOANNINA', "ΙΩΑΝΝΙΝΩΝ"
    KAVALA = 'KAVALA', "ΚΑΒΑΛΑΣ"
    KARDITSA = 'KARDITSA', "ΚΑΡΔΙΤΣΗΣ"
    KASTORIA = 'KASTORIA', "ΚΑΣΤΟΡΙΑΣ"
    KERKYRA = 'KERKYRA', "ΚΕΡΚΥΡΑΣ"
    CEPHALONIA = 'CEPHALONIA', "ΚΕΦΑΛΛΗΝΙΑΣ"
    KILKIS = 'KILKIS', "ΚΙΛΚΙΣ"
    KOZANI = 'KOZANI', "ΚΟΖΑΝΗΣ"
    CORINTHIA = 'CORINTHIA', "ΚΟΡΙΝΘΙΑΣ"
    CYCLADES = 'CYCLADES', "ΚΥΚΛΑΔΩΝ"
    LACONIA = 'LACONIA', "ΛΑΚΩΝΙΑΣ"
    LARISSA = 'LARISSA', "ΛΑΡΙΣΗΣ"
    LASITHI = 'LASITHI', "ΛΑΣΙΘΙΟΥ"
    LESBOS = 'LESBOS', "ΛΕΣΒΟΥ"
    LEFKADA = 'LEFKADA', "ΛΕΥΚΑΔΟΣ"
    MAGNESIA = 'MAGNESIA', "ΜΑΓΝΗΣΙΑΣ"
    MESSENIA = 'MESSENIA', "ΜΕΣΣΗΝΙΑΣ"
    XANTHI = 'XANTHI', "ΞΑΝΘΗΣ"
    PELLA = 'PELLA', "ΠΕΛΛΗΣ"
    PIERIA = 'PIERIA', "ΠΙΕΡΙΑΣ"
    PREVEZA = 'PREVEZA', "ΠΡΕΒΕΖΗΣ"
    RETHYMNO = 'RETHYMNO', "ΡΕΘΥΜΝΗΣ"
    RHODOPE = 'RHODOPE', "ΡΟΔΟΠΗΣ"
    SAMOS = 'SAMOS', "ΣΑΜΟΥ"
    SERRES = 'SERRES', "ΣΕΡΡΩΝ"
    TRIKALA = 'TRIKALA', "ΤΡΙΚΑΛΩΝ"
    PHTHIOTIS = 'PHTHIOTIS', "ΦΘΙΩΤΙΔΟΣ"
    FLORINA = 'FLORINA', "ΦΛΩΡΙΝΗΣ"
    PHOCIS = 'PHOCIS', "ΦΩΚΙΔΟΣ"
    CHALKIDIKI = 'CHALKIDIKI', "ΧΑΛΚΙΔΙΚΗΣ"
    CHANIA = 'CHANIA', "ΧΑΝΙΩΝ"
    CHIOS = 'CHIOS', "ΧΙΟΥ"

    def __new__(cls, value: str, description: str):
        """Creates the prefecture enum.

        :param value: The enum value.
        :param description: The prefecture description.
        """
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description

        return obj


class DataType(enum.Enum):
    """Enumeration for the different types of data contained in the data
    """
    WEEKLY_COUNTRY = 'weekly_country'
    WEEKLY_PREFECTURE = 'weekly_prefecture'
    DAILY_COUNTRY = 'daily_country'
    DAILY_PREFECTURE = 'daily_prefecture'


class DataFileType(enum.Enum):
    """Enumeration for the different data file types.
    """
    WEEKLY = 'weekly', 'Weekly', 'deltia.view', (DataType.WEEKLY_COUNTRY, DataType.WEEKLY_PREFECTURE), 'EBDOM_DELTIO'
    DAILY_COUNTRY = (
        'daily_country', 'Daily Country', 'deltia_d.view', (DataType.DAILY_COUNTRY, ), 'IMERISIO_DELTIO_PANELLINIO'
    )
    DAILY_PREFECTURE = (
        'daily_prefecture', 'Daily Prefecture', 'deltia_dn.view', (DataType.DAILY_PREFECTURE, ),
        'IMERISIO_DELTIO_ANA_NOMO'
    )

    def __new__(cls, value: str, description: str, page: str, data_types: Iterable[DataType], prefix: str):
        """Creates the enum.

        :param value: The enum value.
        :param value: The enum description.
        :param page: The path, relative to the base URL, from which we will fetch the data.
        :param data_types: The data types that this page contains.
        :param prefix: The prefix for the data link.
        """
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        obj.page = page
        obj.data_types = data_types
        obj.prefix = prefix

        return obj

    def dates(self, start_date: datetime.date, end_date: datetime.date) -> Generator[datetime.date]:
        """Get the available dates for the file type and the selected dates.

        :param start_date: The start date.
        :param end_date: The end date.
        :return: Yield each available date.
        """
        current_date = start_date
        while current_date <= end_date:
            if self != self.WEEKLY or current_date.weekday() == 4:
                yield current_date
            current_date += datetime.timedelta(days=1)

    def link(self, date: datetime.date) -> str:
        """Return the link of the file for which we should the data for the specified date.

        :param date: The date.
        :return: The file link.
        """
        return f'http://www.fuelprices.gr/files/deltia/{self._get_file_name(date)}'

    def _get_file_name(self, date: datetime.date) -> str:
        """Return the file name for the link, based on the date.

        :param date: The date.
        :return: The file name.
        """
        filename = f"{self.prefix}_{date:%d_%m_%Y}.pdf"
        if self.value == 'weekly':
            if date == datetime.date(2015, 3, 6):
                filename = f"{self.prefix}_{datetime.date(2015, 3, 2):%d_%m_%Y}.pdf"
            elif date == datetime.date(2017, 7, 7):
                filename = f"{self.prefix}_{datetime.date(2017, 7, 10):%d_%m_%Y}.pdf"
            elif date == datetime.date(2018, 1, 5):
                filename = f"{self.prefix}_{date:%d_%m_%Y}..pdf"
            elif date == datetime.date(2022, 12, 23):
                filename = f"{self.prefix}_{datetime.date(2022, 12, 22):%d_%m_%Y}.pdf"
            elif date == datetime.date(2024, 1, 26):
                filename = f"{self.prefix}_{datetime.date(2024, 1, 25):%d_%m_%Y}.pdf"

        return filename
