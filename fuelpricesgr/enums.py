"""The various project enums
"""
import enum


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

