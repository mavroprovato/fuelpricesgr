"""The project enums
"""
import collections.abc
import datetime
import enum
import importlib
from collections.abc import Generator

from fuelpricesgr import settings


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

    def model(self):
        """Return the database model for the data type.

        :return: The database model for the data type.
        """
        module = importlib.import_module("fuelpricesgr.services.sql")

        match self:
            case self.WEEKLY_COUNTRY:
                return getattr(module, 'WeeklyCountry')
            case self.WEEKLY_PREFECTURE:
                return getattr(module, 'WeeklyPrefecture')
            case self.DAILY_COUNTRY:
                return getattr(module, 'DailyCountry')
            case self.DAILY_PREFECTURE:
                return getattr(module, 'DailyPrefecture')


class DataFileType(enum.Enum):
    """Enumeration for the different data file types.
    """
    WEEKLY = 'weekly', 'deltia.view', (DataType.WEEKLY_COUNTRY, DataType.WEEKLY_PREFECTURE), 'EBDOM_DELTIO'
    DAILY_COUNTRY = 'daily_country', 'deltia_d.view', (DataType.DAILY_COUNTRY, ), 'IMERISIO_DELTIO_PANELLINIO'
    DAILY_PREFECTURE = 'daily_prefecture', 'deltia_dn.view', (DataType.DAILY_PREFECTURE, ), 'IMERISIO_DELTIO_ANA_NOMO'

    def __new__(cls, value: str, page: str, data_types: collections.abc.Iterable[DataType], prefix: str):
        """Creates the enum.

        :param value: The enum value.
        :param page: The path, relative to the base URL, from which we will fetch the data.
        :param data_types: The data types that this page contains.
        :param prefix: The prefix for the data link.
        """
        obj = object.__new__(cls)
        obj._value_ = value
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

    def link(self, date: datetime.date) -> str | None:
        """Return the link of the file from which we got the data for the specified date.

        :param date: The date.
        :return: The file link.
        """
        return f'{settings.FETCH_URL}/files/deltia/{self.prefix}_{date:%d_%m_%Y}.pdf'
