"""The various project enums
"""
import collections.abc
import datetime
import enum

from fuelpricesgr import settings


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
    ATTICA = "ΑΤΤΙΚΗΣ"
    AETOLIA_ACARNANIA = "ΑΙΤΩΛΙΑΣ ΚΑΙ ΑΚΑΡΝΑΝΙΑΣ"
    ARGOLIS = "ΑΡΓΟΛΙΔΟΣ"
    ARKADIAS = "ΑΡΚΑΔΙΑΣ"
    ARTA = "ΑΡΤΗΣ"
    ACHAEA = "ΑΧΑΪΑΣ"
    BOEOTIA = "ΒΟΙΩΤΙΑΣ"
    GREVENA = "ΓΡΕΒΕΝΩΝ"
    DRAMA = "ΔΡΑΜΑΣ"
    DODECANESE = "ΔΩΔΕΚΑΝΗΣΟΥ"
    EVROS = "ΕΒΡΟΥ"
    EUBOEA = "ΕΥΒΟΙΑΣ"
    EVRYTANIA = "ΕΥΡΥΤΑΝΙΑΣ"
    ZAKYNTHOS = "ΖΑΚΥΝΘΟΥ"
    ELIS = "ΗΛΕΙΑΣ"
    IMATHIA = "ΗΜΑΘΙΑΣ"
    HERAKLION = "ΗΡΑΚΛΕΙΟΥ"
    THESPROTIA = "ΘΕΣΠΡΩΤΙΑΣ"
    THESSALONIKI = "ΘΕΣΣΑΛΟΝΙΚΗΣ"
    IOANNINA = "ΙΩΑΝΝΙΝΩΝ"
    KAVALA = "ΚΑΒΑΛΑΣ"
    KARDITSA = "ΚΑΡΔΙΤΣΗΣ"
    KASTORIA = "ΚΑΣΤΟΡΙΑΣ"
    KERKYRA = "ΚΕΡΚΥΡΑΣ"
    CEPHALONIA = "ΚΕΦΑΛΛΗΝΙΑΣ"
    KILKIS = "ΚΙΛΚΙΣ"
    KOZANI = "ΚΟΖΑΝΗΣ"
    CORINTHIA = "ΚΟΡΙΝΘΙΑΣ"
    CYCLADES = "ΚΥΚΛΑΔΩΝ"
    LACONIA = "ΛΑΚΩΝΙΑΣ"
    LARISSA = "ΛΑΡΙΣΗΣ"
    LASITHI = "ΛΑΣΙΘΙΟΥ"
    LESBOS = "ΛΕΣΒΟΥ"
    LEFKADA = "ΛΕΥΚΑΔΟΣ"
    MAGNESIA = "ΜΑΓΝΗΣΙΑΣ"
    MESSENIA = "ΜΕΣΣΗΝΙΑΣ"
    XANTHI = "ΞΑΝΘΗΣ"
    PELLA = "ΠΕΛΛΗΣ"
    PIERIA = "ΠΙΕΡΙΑΣ"
    PREVEZA = "ΠΡΕΒΕΖΗΣ"
    RETHYMNO = "ΡΕΘΥΜΝΗΣ"
    RHODOPE = "ΡΟΔΟΠΗΣ"
    SAMOS = "ΣΑΜΟΥ"
    SERRES = "ΣΕΡΡΩΝ"
    TRIKALA = "ΤΡΙΚΑΛΩΝ"
    PHTHIOTIS = "ΦΘΙΩΤΙΔΟΣ"
    FLORINA = "ΦΛΩΡΙΝΗΣ"
    PHOCIS = "ΦΩΚΙΔΟΣ"
    CHALKIDIKI = "ΧΑΛΚΙΔΙΚΗΣ"
    CHANIA = "ΧΑΝΙΩΝ"
    CHIOS = "ΧΙΟΥ"

    def __init__(self, display_name: str):
        """Creates the enum.

        :param display_name: The name of the prefecture in Greek.
        """
        self.display_name = display_name
