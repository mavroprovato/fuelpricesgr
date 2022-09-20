"""The various project enums
"""
import collections.abc
import datetime
import enum

from fuelpricesgr import settings


class ApplicationStatus(enum.Enum):
    """Enumeration for the application status.
    """
    OK = 'ok'
    ERROR = 'error'


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
    WEEKLY = 'weekly', 'deltia.view', (DataType.WEEKLY_COUNTRY, DataType.WEEKLY_PREFECTURE)
    DAILY_COUNTRY = 'daily_country', 'deltia_d.view', (DataType.DAILY_COUNTRY, )
    DAILY_PREFECTURE = 'daily_prefecture', 'deltia_dn.view', (DataType.DAILY_PREFECTURE, )

    def __new__(cls, value: str, page: str, data_types: collections.abc.Iterable[DataType]):
        """Creates the enum.

        :param value: The enum value.
        :param page: The path, relative to the base URL, from which we will fetch the data.
        :param data_types: The data types that this page contains.
        """
        obj = object.__new__(cls)
        obj._value_ = value
        obj.page = page
        obj.data_types = data_types

        return obj

    def link(self, date: datetime.date) -> str | None:
        """Return the link of the file from which we got the data for the specified date.

        :param date: The date.
        :return: The file link.
        """
        if self == self.WEEKLY:
            return f'{settings.FETCH_URL}/files/deltia/EBDOM_DELTIO_{date:%d_%m_%Y}.pdf'
        if self == self.DAILY_COUNTRY:
            return f'{settings.FETCH_URL}/files/deltia/IMERISIO_DELTIO_PANELLINIO_{date:%d_%m_%Y}.pdf'
        if self == self.DAILY_PREFECTURE:
            return f'{settings.FETCH_URL}/files/deltia/IMERISIO_DELTIO_ANA_NOMO_{date:%d_%m_%Y}.pdf'

        return None


class FuelType(enum.Enum):
    """Enumeration for the different fuel types
    """
    UNLEADED_95 = "Αμόλυβδη 95"
    UNLEADED_100 = "Αμόλυβδη 100"
    SUPER = "Super"
    DIESEL = "Diesel"
    DIESEL_HEATING = "Diesel Θέρμανσης"
    GAS = "Υγραέριο"


class Prefecture(enum.Enum):
    """Enumeration for greek prefectures
    """
    ATTICA = "ATTICA", "ΑΤΤΙΚΗΣ"
    AETOLIA_ACARNANIA = "AETOLIA_ACARNANIA", "ΑΙΤΩΛΙΑΣ ΚΑΙ ΑΚΑΡΝΑΝΙΑΣ"
    ARGOLIS = "ARGOLIS", "ΑΡΓΟΛΙΔΟΣ"
    ARKADIAS = "ARKADIAS", "ΑΡΚΑΔΙΑΣ"
    ARTA = "ARTA", "ΑΡΤΗΣ"
    ACHAEA = "ACHAEA", "ΑΧΑΪΑΣ"
    BOEOTIA = "BOEOTIA", "ΒΟΙΩΤΙΑΣ"
    GREVENA = "GREVENA", "ΓΡΕΒΕΝΩΝ"
    DRAMA = "DRAMA", "ΔΡΑΜΑΣ"
    DODECANESE = "DODECANESE", "ΔΩΔΕΚΑΝΗΣΟΥ"
    EVROS = "EVROS", "ΕΒΡΟΥ"
    EUBOEA = "EUBOEA", "ΕΥΒΟΙΑΣ"
    EVRYTANIA = "EVRYTANIA", "ΕΥΡΥΤΑΝΙΑΣ"
    ZAKYNTHOS = "ZAKYNTHOS", "ΖΑΚΥΝΘΟΥ"
    ELIS = "ELIS", "ΗΛΕΙΑΣ"
    IMATHIA = "IMATHIA", "ΗΜΑΘΙΑΣ"
    HERAKLION = "HERAKLION", "ΗΡΑΚΛΕΙΟΥ"
    THESPROTIA = "THESPROTIA", "ΘΕΣΠΡΩΤΙΑΣ"
    THESSALONIKI = "THESSALONIKI", "ΘΕΣΣΑΛΟΝΙΚΗΣ"
    IOANNINA = "IOANNINA", "ΙΩΑΝΝΙΝΩΝ"
    KAVALA = "KAVALA", "ΚΑΒΑΛΑΣ"
    KARDITSA = "KARDITSA", "ΚΑΡΔΙΤΣΗΣ"
    KASTORIA = "KASTORIA", "ΚΑΣΤΟΡΙΑΣ"
    KERKYRA = "KERKYRA", "ΚΕΡΚΥΡΑΣ"
    CEPHALONIA = "CEPHALONIA", "ΚΕΦΑΛΛΗΝΙΑΣ"
    KILKIS = "KILKIS", "ΚΙΛΚΙΣ"
    KOZANI = "KOZANI", "ΚΟΖΑΝΗΣ"
    CORINTHIA = "CORINTHIA", "ΚΟΡΙΝΘΙΑΣ"
    CYCLADES = "CYCLADES", "ΚΥΚΛΑΔΩΝ"
    LACONIA = "LACONIA", "ΛΑΚΩΝΙΑΣ"
    LARISSA = "LARISSA", "ΛΑΡΙΣΗΣ"
    LASITHI = "LASITHI", "ΛΑΣΙΘΙΟΥ"
    LESBOS = "LESBOS", "ΛΕΣΒΟΥ"
    LEFKADA = "LEFKADA", "ΛΕΥΚΑΔΟΣ"
    MAGNESIA = "MAGNESIA", "ΜΑΓΝΗΣΙΑΣ"
    MESSENIA = "MESSENIA", "ΜΕΣΣΗΝΙΑΣ"
    XANTHI = "XANTHI", "ΞΑΝΘΗΣ"
    PELLA = "PELLA", "ΠΕΛΛΗΣ"
    PIERIA = "PIERIA", "ΠΙΕΡΙΑΣ"
    PREVEZA = "PREVEZA", "ΠΡΕΒΕΖΗΣ"
    RETHYMNO = "RETHYMNO", "ΡΕΘΥΜΝΗΣ"
    RHODOPE = "RHODOPE", "ΡΟΔΟΠΗΣ"
    SAMOS = "SAMOS", "ΣΑΜΟΥ"
    SERRES = "SERRES", "ΣΕΡΡΩΝ"
    TRIKALA = "TRIKALA", "ΤΡΙΚΑΛΩΝ"
    PHTHIOTIS = "PHTHIOTIS", "ΦΘΙΩΤΙΔΟΣ"
    FLORINA = "FLORINA", "ΦΛΩΡΙΝΗΣ"
    PHOCIS = "PHOCIS", "ΦΩΚΙΔΟΣ"
    CHALKIDIKI = "CHALKIDIKI", "ΧΑΛΚΙΔΙΚΗΣ"
    CHANIA = "CHANIA", "ΧΑΝΙΩΝ"
    CHIOS = "CHIOS", "ΧΙΟΥ"

    def __new__(cls, value: str, display_name: str):
        """Creates the enum.

        :param value: The enum value.
        :param page: The path, relative to the base URL, from which we will fetch the data.
        :param data_types: The data types that this page contains.
        """
        obj = object.__new__(cls)
        obj._value_ = value
        obj.display_name = display_name

        return obj
