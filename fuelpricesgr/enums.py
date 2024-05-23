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
    ATTICA = 'ATTICA', "ΑΤΤΙΚΗΣ", r'ΝΟΜΟΣ ΑΤΤΙΚ\s?ΗΣ'
    AETOLIA_ACARNANIA = 'AETOLIA_ACARNANIA', "ΑΙΤΩΛΙΑΣ ΚΑΙ ΑΚΑΡΝΑΝΙΑΣ", r'ΝΟΜΟΣ ΑΙΤΩ\s?ΛΙΑΣ ΚΑΙ ΑΚΑΡΝΑΝ\s?ΙΑ\s?Σ'
    ARGOLIS = 'ARGOLIS', "ΑΡΓΟΛΙΔΟΣ", r'ΝΟΜΟΣ ΑΡΓΟΛΙΔΟΣ'
    ARKADIAS = 'ARKADIAS', "ΑΡΚΑΔΙΑΣ", r'ΝΟΜΟΣ ΑΡΚΑΔΙΑΣ'
    ARTA = 'ARTA', "ΑΡΤΗΣ", r'ΝΟΜΟΣ ΑΡΤΗΣ'
    ACHAEA = 'ACHAEA', "ΑΧΑΪΑΣ", r'ΝΟΜΟΣ ΑΧΑΪΑΣ'
    BOEOTIA = 'BOEOTIA', "ΒΟΙΩΤΙΑΣ", r'ΝΟΜΟΣ ΒΟΙΩΤΙΑΣ'
    GREVENA = 'GREVENA', "ΓΡΕΒΕΝΩΝ", r'ΝΟΜΟ\s?Σ\s{1,2}ΓΡΕ\s?ΒΕΝΩΝ'
    DRAMA = 'DRAMA', "ΔΡΑΜΑΣ", r'ΝΟΜΟΣ ΔΡΑΜΑΣ'
    DODECANESE = 'DODECANESE', "ΔΩΔΕΚΑΝΗΣΟΥ", r'ΝΟΜΟΣ ΔΩΔΕΚΑΝΗΣΟΥ'
    EVROS = 'EVROS', "ΕΒΡΟΥ", r'ΝΟΜ\s?Ο\s?Σ ΕΒΡΟΥ'
    EUBOEA = 'EUBOEA', "ΕΥΒΟΙΑΣ", r'ΝΟΜΟΣ ΕΥΒ\s?ΟΙΑΣ'
    EVRYTANIA = 'EVRYTANIA', "ΕΥΡΥΤΑΝΙΑΣ", r'ΝΟΜΟΣ ΕΥ\s?ΡΥΤΑΝΙΑΣ'
    ZAKYNTHOS = 'ZAKYNTHOS', "ΖΑΚΥΝΘΟΥ", r'ΝΟΜΟΣ ΖΑΚΥΝΘΟΥ'
    ELIS = 'ELIS', "ΗΛΕΙΑΣ", r'ΝΟΜΟΣ ΗΛΕΙΑΣ'
    IMATHIA = 'IMATHIA', "ΗΜΑΘΙΑΣ", r'ΝΟΜΟΣ ΗΜΑΘΙΑΣ'
    HERAKLION = 'HERAKLION', "ΗΡΑΚΛΕΙΟΥ", r'ΝΟΜΟΣ ΗΡΑΚΛΕΙΟΥ'
    THESPROTIA = 'THESPROTIA', "ΘΕΣΠΡΩΤΙΑΣ", r'ΝΟΜΟΣ Θ\s?ΕΣΠΡΩΤΙΑΣ'
    THESSALONIKI = 'THESSALONIKI', "ΘΕΣΣΑΛΟΝΙΚΗΣ", r'ΝΟΜΟ\s?Σ ΘΕ\s?ΣΣΑ\s?Λ\s?ΟΝΙΚ\s?ΗΣ'
    IOANNINA = 'IOANNINA', "ΙΩΑΝΝΙΝΩΝ", r'ΝΟΜΟΣ ΙΩΑΝΝΙΝΩΝ'
    KAVALA = 'KAVALA', "ΚΑΒΑΛΑΣ", r'ΝΟΜΟΣ ΚΑΒΑΛΑΣ'
    KARDITSA = 'KARDITSA', "ΚΑΡΔΙΤΣΗΣ", r'ΝΟΜΟΣ ΚΑΡΔΙΤΣΗΣ'
    KASTORIA = 'KASTORIA', "ΚΑΣΤΟΡΙΑΣ", r'ΝΟΜΟΣ ΚΑΣ\s?ΤΟΡΙΑΣ'
    KERKYRA = 'KERKYRA', "ΚΕΡΚΥΡΑΣ", r'ΝΟΜΟΣ ΚΕΡΚΥΡΑΣ'
    CEPHALONIA = 'CEPHALONIA', "ΚΕΦΑΛΛΗΝΙΑΣ", r'ΝΟΜΟΣ ΚΕΦΑΛΛΗΝΙΑΣ'
    KILKIS = 'KILKIS', "ΚΙΛΚΙΣ", r'ΝΟΜΟΣ ΚΙΛΚΙΣ'
    KOZANI = 'KOZANI', "ΚΟΖΑΝΗΣ", r'ΝΟΜΟΣ ΚΟΖΑΝΗΣ'
    CORINTHIA = 'CORINTHIA', "ΚΟΡΙΝΘΙΑΣ", r'ΝΟΜΟΣ ΚΟΡΙΝΘΙΑΣ'
    CYCLADES = 'CYCLADES', "ΚΥΚΛΑΔΩΝ", r'ΝΟΜΟΣ ΚΥΚΛΑΔΩΝ'
    LACONIA = 'LACONIA', "ΛΑΚΩΝΙΑΣ", r'ΝΟΜ\s?ΟΣ Λ\s?ΑΚΩ\s?Ν\s?ΙΑΣ'
    LARISSA = 'LARISSA', "ΛΑΡΙΣΗΣ", r'ΝΟΜΟΣ ΛΑΡΙΣΗΣ'
    LASITHI = 'LASITHI', "ΛΑΣΙΘΙΟΥ", r'ΝΟΜΟΣ ΛΑΣΙΘΙΟΥ'
    LESBOS = 'LESBOS', "ΛΕΣΒΟΥ", r'ΝΟΜΟΣ ΛΕΣΒΟΥ'
    LEFKADA = 'LEFKADA', "ΛΕΥΚΑΔΟΣ", r'ΝΟΜΟΣ ΛΕΥΚΑΔΟΣ'
    MAGNESIA = 'MAGNESIA', "ΜΑΓΝΗΣΙΑΣ", r'ΝΟΜΟΣ ΜΑΓΝΗΣΙΑ\s?Σ'
    MESSENIA = 'MESSENIA', "ΜΕΣΣΗΝΙΑΣ", r'ΝΟΜ\s?ΟΣ ΜΕΣΣΗΝΙΑΣ'
    XANTHI = 'XANTHI', "ΞΑΝΘΗΣ", r'ΝΟΜΟΣ ΞΑΝΘΗΣ'
    PELLA = 'PELLA', "ΠΕΛΛΗΣ", r'ΝΟΜΟΣ ΠΕΛΛΗΣ'
    PIERIA = 'PIERIA', "ΠΙΕΡΙΑΣ", r'ΝΟΜΟΣ ΠΙΕΡΙΑΣ'
    PREVEZA = 'PREVEZA', "ΠΡΕΒΕΖΗΣ", r'ΝΟΜΟΣ ΠΡΕΒΕΖΗΣ'
    RETHYMNO = 'RETHYMNO', "ΡΕΘΥΜΝΗΣ", r'ΝΟΜΟΣ ΡΕΘΥΜΝΗ\s?Σ'
    RHODOPE = 'RHODOPE', "ΡΟΔΟΠΗΣ", r'ΝΟΜΟΣ ΡΟΔΟΠΗΣ'
    SAMOS = 'SAMOS', "ΣΑΜΟΥ", r'ΝΟΜΟΣ\s+ΣΑΜΟΥ'
    SERRES = 'SERRES', "ΣΕΡΡΩΝ", r'ΝΟΜΟΣ ΣΕΡΡΩΝ'
    TRIKALA = 'TRIKALA', "ΤΡΙΚΑΛΩΝ", r'ΝΟΜΟΣ ΤΡΙΚΑΛΩΝ'
    PHTHIOTIS = 'PHTHIOTIS', "ΦΘΙΩΤΙΔΟΣ", r'ΝΟΜΟΣ ΦΘΙΩΤΙΔΟΣ'
    FLORINA = 'FLORINA', "ΦΛΩΡΙΝΗΣ", r'ΝΟΜΟ\s?Σ Φ\s?Λ\s?ΩΡΙΝ\s?ΗΣ'
    PHOCIS = 'PHOCIS', "ΦΩΚΙΔΟΣ", r'ΝΟΜΟΣ ΦΩΚΙΔΟΣ'
    CHALKIDIKI = 'CHALKIDIKI', "ΧΑΛΚΙΔΙΚΗΣ", r'ΝΟΜΟΣ ΧΑΛΚΙΔΙΚΗΣ'
    CHANIA = 'CHANIA', "ΧΑΝΙΩΝ", r'ΝΟΜΟΣ ΧΑΝΙΩΝ'
    CHIOS = 'CHIOS', "ΧΙΟΥ", r'ΝΟΜΟΣ ΧΙΟΥ'

    def __new__(cls, value: str, description: str, regex: str):
        """Creates the prefecture enum.

        :param value: The enum value.
        :param description: The prefecture description.
        """
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        obj.regex = regex

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

    def link(self, date: datetime.date) -> str:
        """Return the link of the file for which we should the data for the specified date.

        :param date: The date.
        :return: The file link.
        """
        return f'{settings.FETCH_URL}/files/deltia/{self._get_file_name(date)}'

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
