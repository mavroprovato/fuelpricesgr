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
    AETOLIA_ACARNANIA = 'AETOLIA_ACARNANIA', "ΑΙΤΩΛΙΑΣ ΚΑΙ ΑΚΑΡΝΑΝΙΑΣ", r'ΝΟΜΟΣ ΑΙΤΩ\s?ΛΙΑΣ ΚΑΙ Α\s?ΚΑΡΝΑΝ\s?ΙΑ\s?Σ'
    ARGOLIS = 'ARGOLIS', "ΑΡΓΟΛΙΔΟΣ", r'ΝΟΜΟΣ ΑΡΓΟΛΙΔΟΣ'
    ARKADIAS = 'ARKADIAS', "ΑΡΚΑΔΙΑΣ", r'ΝΟΜ\s?Ο\s?Σ ΑΡΚ\s?ΑΔΙΑΣ'
    ARTA = 'ARTA', "ΑΡΤΗΣ", r'ΝΟΜΟΣ ΑΡΤΗΣ'
    ACHAEA = 'ACHAEA', "ΑΧΑΪΑΣ", r'ΝΟΜΟΣ\s{1,2}ΑΧ\s?ΑΪ\s?Α\s?Σ'
    BOEOTIA = 'BOEOTIA', "ΒΟΙΩΤΙΑΣ", r'ΝΟΜΟ\s?Σ ΒΟ\s?ΙΩΤΙΑΣ'
    GREVENA = 'GREVENA', "ΓΡΕΒΕΝΩΝ", r'ΝΟΜΟ\s?Σ\s{1,2}Γ\s?ΡΕ\s?ΒΕΝΩΝ'
    DRAMA = 'DRAMA', "ΔΡΑΜΑΣ", r'ΝΟΜΟΣ Δ\s?ΡΑΜΑΣ'
    DODECANESE = 'DODECANESE', "ΔΩΔΕΚΑΝΗΣΟΥ", r'ΝΟΜΟΣ ΔΩΔΕΚΑΝΗΣΟΥ'
    EVROS = 'EVROS', "ΕΒΡΟΥ", r'ΝΟΜ\s?Ο\s?Σ ΕΒΡΟΥ'
    EUBOEA = 'EUBOEA', "ΕΥΒΟΙΑΣ", r'ΝΟΜΟΣ ΕΥΒ\s?ΟΙΑΣ'
    EVRYTANIA = 'EVRYTANIA', "ΕΥΡΥΤΑΝΙΑΣ", r'ΝΟΜ\s?Ο\s?Σ ΕΥ\s?ΡΥΤΑΝΙΑΣ'
    ZAKYNTHOS = 'ZAKYNTHOS', "ΖΑΚΥΝΘΟΥ", r'ΝΟΜ\s?ΟΣ Ζ\s?ΑΚΥΝΘΟΥ'
    ELIS = 'ELIS', "ΗΛΕΙΑΣ", r'ΝΟΜΟ\s?Σ\s{1,2}ΗΛΕ\s?ΙΑΣ'
    IMATHIA = 'IMATHIA', "ΗΜΑΘΙΑΣ", r'ΝΟΜΟΣ ΗΜΑΘΙΑΣ'
    HERAKLION = 'HERAKLION', "ΗΡΑΚΛΕΙΟΥ", r'ΝΟΜΟΣ ΗΡΑΚ\s?ΛΕΙΟΥ'
    THESPROTIA = 'THESPROTIA', "ΘΕΣΠΡΩΤΙΑΣ", r'ΝΟΜΟΣ Θ\s?ΕΣΠΡΩΤΙΑΣ'
    THESSALONIKI = 'THESSALONIKI', "ΘΕΣΣΑΛΟΝΙΚΗΣ", r'ΝΟΜ\s?Ο\s?Σ\s{1,2}Θ\s?Ε\s?Σ\s?ΣΑ\s?Λ\s?Ο\s?Ν\s?Ι\s?Κ\s?Η\s?Σ'
    IOANNINA = 'IOANNINA', "ΙΩΑΝΝΙΝΩΝ", r'ΝΟΜΟΣ ΙΩΑΝΝΙΝΩΝ'
    KAVALA = 'KAVALA', "ΚΑΒΑΛΑΣ", r'ΝΟΜΟΣ ΚΑΒΑΛΑΣ'
    KARDITSA = 'KARDITSA', "ΚΑΡΔΙΤΣΗΣ", r'ΝΟΜΟΣ ΚΑΡΔΙΤΣΗΣ'
    KASTORIA = 'KASTORIA', "ΚΑΣΤΟΡΙΑΣ", r'ΝΟΜΟΣ ΚΑΣ\s?Τ\s?ΟΡΙΑΣ'
    KERKYRA = 'KERKYRA', "ΚΕΡΚΥΡΑΣ", r'ΝΟΜΟΣ Κ\s?ΕΡΚΥΡΑΣ'
    CEPHALONIA = 'CEPHALONIA', "ΚΕΦΑΛΛΗΝΙΑΣ", r'ΝΟΜ\s?ΟΣ Κ\s?ΕΦΑ\s?ΛΛΗ\s?ΝΙ\s?Α\s?Σ'
    KILKIS = 'KILKIS', "ΚΙΛΚΙΣ", r'ΝΟΜΟΣ ΚΙ\s?ΛΚ\s?ΙΣ'
    KOZANI = 'KOZANI', "ΚΟΖΑΝΗΣ", r'ΝΟΜΟΣ ΚΟΖΑΝΗΣ'
    CORINTHIA = 'CORINTHIA', "ΚΟΡΙΝΘΙΑΣ", r'ΝΟΜΟΣ ΚΟΡΙ\s?ΝΘΙΑΣ'
    CYCLADES = 'CYCLADES', "ΚΥΚΛΑΔΩΝ", r'ΝΟΜΟΣ ΚΥΚΛΑΔΩΝ'
    LACONIA = 'LACONIA', "ΛΑΚΩΝΙΑΣ", r'ΝΟΜ\s?Ο\s?Σ\s{1,2}Λ\s?Α\s?ΚΩ\s?Ν\s?ΙΑ\s?Σ'
    LARISSA = 'LARISSA', "ΛΑΡΙΣΗΣ", r'ΝΟΜΟΣ ΛΑΡ\s?ΙΣΗΣ'
    LASITHI = 'LASITHI', "ΛΑΣΙΘΙΟΥ", r'ΝΟΜ\s?Ο\s?Σ ΛΑΣΙΘΙΟΥ'
    LESBOS = 'LESBOS', "ΛΕΣΒΟΥ", r'ΝΟΜΟΣ ΛΕΣΒΟΥ'
    LEFKADA = 'LEFKADA', "ΛΕΥΚΑΔΟΣ", r'ΝΟΜΟΣ ΛΕΥΚΑΔΟΣ'
    MAGNESIA = 'MAGNESIA', "ΜΑΓΝΗΣΙΑΣ", r'ΝΟΜΟΣ\s{1,2}ΜΑΓΝΗΣΙΑ\s?Σ'
    MESSENIA = 'MESSENIA', "ΜΕΣΣΗΝΙΑΣ", r'ΝΟΜ\s?ΟΣ ΜΕΣΣ\s?ΗΝΙΑ\s?Σ'
    XANTHI = 'XANTHI', "ΞΑΝΘΗΣ", r'ΝΟΜΟΣ ΞΑΝΘ\s?Η\s?Σ'
    PELLA = 'PELLA', "ΠΕΛΛΗΣ", r'ΝΟΜΟ\s?Σ Π\s?ΕΛ\s?Λ\s?Η\s?Σ'
    PIERIA = 'PIERIA', "ΠΙΕΡΙΑΣ", r'ΝΟΜΟΣ ΠΙΕΡΙΑΣ'
    PREVEZA = 'PREVEZA', "ΠΡΕΒΕΖΗΣ", r'ΝΟΜΟΣ\s{1,2}ΠΡΕΒΕΖΗΣ'
    RETHYMNO = 'RETHYMNO', "ΡΕΘΥΜΝΗΣ", r'ΝΟΜΟΣ Ρ\s?ΕΘΥΜΝΗ\s?Σ'
    RHODOPE = 'RHODOPE', "ΡΟΔΟΠΗΣ", r'ΝΟΜΟΣ ΡΟΔΟΠ\s?ΗΣ'
    SAMOS = 'SAMOS', "ΣΑΜΟΥ", r'ΝΟΜΟ\s?Σ\s{1,2}Σ\s?Α\s?ΜΟ\s?Υ'
    SERRES = 'SERRES', "ΣΕΡΡΩΝ", r'ΝΟΜΟΣ ΣΕΡΡΩ\s?Ν'
    TRIKALA = 'TRIKALA', "ΤΡΙΚΑΛΩΝ", r'ΝΟΜΟ\s?Σ Τ\s?ΡΙΚΑΛΩΝ'
    PHTHIOTIS = 'PHTHIOTIS', "ΦΘΙΩΤΙΔΟΣ", r'ΝΟΜΟΣ ΦΘΙΩΤΙΔΟΣ'
    FLORINA = 'FLORINA', "ΦΛΩΡΙΝΗΣ", r'ΝΟΜ\s?Ο\s?Σ\s{1,2}Φ\s?Λ\s?ΩΡ\s?ΙΝ\s?ΗΣ'
    PHOCIS = 'PHOCIS', "ΦΩΚΙΔΟΣ", r'ΝΟΜΟΣ ΦΩΚΙΔΟΣ'
    CHALKIDIKI = 'CHALKIDIKI', "ΧΑΛΚΙΔΙΚΗΣ", r'ΝΟΜΟ\s?Σ ΧΑΛΚΙΔ\s?ΙΚΗΣ'
    CHANIA = 'CHANIA', "ΧΑΝΙΩΝ", r'ΝΟΜΟΣ ΧΑΝΙΩΝ'
    CHIOS = 'CHIOS', "ΧΙΟΥ", r'ΝΟΜΟΣ\s{1,2}ΧΙ\s?ΟΥ'

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
