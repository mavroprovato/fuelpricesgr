"""The various project enums
"""
import enum
import re


class FuelDataType(enum.Enum):
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
    """Enumeration for the different fuel types
    """
    UNLEADED_95 = 'Αμόλυβδη 95'
    UNLEADED_100 = 'Αμόλυβδη 100'
    SUPER = 'Super'
    DIESEL = 'Diesel'
    DIESEL_HEATING = 'Diesel Θέρμανσης'
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

    @classmethod
    def from_text(cls, text):
        if re.match(r'Α ?Τ ?Τ ?Ι ?Κ ?Η ?Σ', text):
            return cls.ATTICA
        elif re.match(r'Α ?Ι ?Τ ?Ω ?Λ ?Ι ?Α ?Σ {1,2}Κ ?Α ?Ι {1,2}Α ?Κ ?Α ?Ρ ?Ν ?Α ?Ν ?Ι ?Α ?Σ', text):
            return cls.AETOLIA_ACARNANIA
        elif re.match(r'ΑΡΓΟ ?Λ ?ΙΔ ?Ο ?Σ', text):
            return cls.ARGOLIS
        elif re.match(r'ΑΡΚΑΔΙΑΣ', text):
            return cls.ARKADIAS
        elif re.match(r'Α ?Ρ ?Τ ?ΗΣ', text):
            return cls.ARTA
        elif re.match(r'Α ?Χ ?Α ?Ϊ ?Α ?Σ', text):
            return cls.ACHAEA
        elif re.match(r'Β ?Ο ?Ι ?Ω ?Τ ?Ι ?Α ?Σ', text):
            return cls.BOEOTIA
        elif re.match(r'ΔΡΑΜΑ ?Σ', text):
            return cls.DRAMA
        elif re.match(r'Γ ?Ρ ?Ε ?Β ?Ε ?Ν ?Ω ?Ν', text):
            return cls.GREVENA
        elif re.match(r'Δ ?ΩΔ ?Ε ?ΚΑΝΗ ?ΣΟΥ', text):
            return cls.DODECANESE
        elif re.match(r'Ε ?Β ?Ρ ?Ο ?Υ', text):
            return cls.EVROS
        elif re.match(r'Ε ?ΥΒ ?Ο ?Ι ?Α ?Σ', text):
            return cls.EUBOEA
        elif re.match(r'ΕΥΡ ?Υ ?ΤΑ ?Ν ?ΙΑ ?Σ', text):
            return cls.EVRYTANIA
        elif re.match(r'Ζ ?Α ?Κ ?ΥΝ ?Θ ?Ο ?Υ', text):
            return cls.ZAKYNTHOS
        elif re.match(r'Η ?ΛΕ ?ΙΑ ?Σ', text):
            return cls.ELIS
        elif re.match(r'Η ?Μ ?Α ?Θ ?Ι ?Α ?Σ', text):
            return cls.IMATHIA
        elif re.match(r'Η ?Ρ ?Α ?Κ ?Λ ?Ε ?Ι ?Ο ?Υ', text):
            return cls.HERAKLION
        elif re.match(r'ΘΕ ?ΣΠ ?ΡΩ ?ΤΙΑ ?Σ', text):
            return cls.THESPROTIA
        elif re.match(r'ΘΕ ?ΣΣ ?Α ?ΛΟΝΙ ?Κ ?ΗΣ', text):
            return cls.THESSALONIKI
        elif re.match(r'Ι ?Ω ?Α ?Ν ?Ν ?Ι ?Ν ?Ω ?Ν', text):
            return cls.IOANNINA
        elif re.match(r'ΚΑ ?Β ?Α ?Λ ?Α ?Σ', text):
            return cls.KAVALA
        elif re.match(r'Κ ?Α ?Ρ ?Δ ?Ι ?Τ ?Σ ?Η ?Σ', text):
            return cls.KARDITSA
        elif re.match(r'Κ ?Α ?ΣΤ ?ΟΡ ?ΙΑ ?Σ', text):
            return cls.KASTORIA
        elif re.match(r'ΚΕΡΚΥΡΑΣ', text):
            return cls.KERKYRA
        elif re.match(r'ΚΕΦΑΛΛΗ ?ΝΙΑ ?Σ', text):
            return cls.CEPHALONIA
        elif re.match(r'Κ ?Ι ?Λ ?Κ ?Ι ?Σ', text):
            return cls.KILKIS
        elif re.match(r'Κ ?Ο ?Ζ ?Α ?Ν ?Η ?Σ', text):
            return cls.KOZANI
        elif re.match(r'Κ ?Ο ?Ρ ?Ι ?Ν ?Θ ?Ι ?Α ?Σ', text):
            return cls.CORINTHIA
        elif re.match(r'ΚΥΚΛΑΔΩΝ', text):
            return cls.CYCLADES
        elif re.match(r'ΛΑΚ ?ΩΝ ?ΙΑΣ', text):
            return cls.LACONIA
        elif re.match(r'ΛΑΡ ?Ι ?ΣΗ ?Σ', text):
            return cls.LARISSA
        elif re.match(r'Λ ?Α ?Σ ?Ι ?Θ ?Ι ?Ο ?Υ', text):
            return cls.LASITHI
        elif re.match(r'Λ ?Ε ?ΣΒ ?Ο ?Υ', text):
            return cls.LESBOS
        elif re.match(r'ΛΕΥΚΑΔΟΣ', text):
            return cls.LEFKADA
        elif re.match(r'ΜΑΓ ?ΝΗΣΙΑΣ', text):
            return cls.MAGNESIA
        elif re.match(r'ΜΕΣ ?ΣΗΝΙΑ ?Σ', text):
            return cls.MESSENIA
        elif re.match(r'Ξ ?Α ?Ν ?Θ ?Η ?Σ', text):
            return cls.XANTHI
        elif re.match(r'Π ?Ε ?Λ ?Λ ?Η ?Σ', text):
            return cls.PELLA
        elif re.match(r'Π ?Ι ?Ε ?ΡΙ ?ΑΣ', text):
            return cls.PIERIA
        elif re.match(r'ΠΡΕΒΕΖΗΣ', text):
            return cls.PREVEZA
        elif re.match(r'ΡΕΘΥΜ ?ΝΗΣ', text):
            return cls.RETHYMNO
        elif re.match(r'ΡΟ ?ΔΟ ?Π ?Η ?Σ', text):
            return cls.RHODOPE
        elif re.match(r'ΣΑΜ ?Ο ?Υ', text):
            return cls.SAMOS
        elif re.match(r'Σ ?Ε ?Ρ ?Ρ ?Ω ?Ν', text):
            return cls.SERRES
        elif re.match(r'Τ ?Ρ ?Ι ?Κ ?Α ?Λ ?Ω ?Ν', text):
            return cls.TRIKALA
        elif re.match(r'Φ ?Θ ?Ι ?Ω ?Τ ?ΙΔ ?Ο ?Σ', text):
            return cls.PHTHIOTIS
        elif re.match(r'ΦΛΩΡΙΝΗ ?Σ', text):
            return cls.FLORINA
        elif re.match(r'Φ ?Ω ?Κ ?Ι ?Δ ?Ο ?Σ', text):
            return cls.PHOCIS
        elif re.match(r'Χ ?Α ?Λ ?Κ ?Ι ?Δ ?Ι ?Κ ?Η ?Σ', text):
            return cls.CHALKIDIKI
        elif re.match(r'ΧΑΝ ?Ι ?Ω ?Ν', text):
            return cls.CHANIA
        elif re.match(r'Χ ?Ι ?Ο ?Υ', text):
            return cls.CHIOS
