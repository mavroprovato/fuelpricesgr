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
        if re.match(r'Α ?[ΤΣ] ?[ΤΣ] ?[ΙΗ] ?Κ ?[ΗΖ] ?[Σ\u03a2]', text):
            return cls.ATTICA
        elif re.match(
                r'Α ?[ΙΗ] ?[ΤΣ] ?Ω ?Λ ?[ΙΗ] ?Α ?[Σ\u03a2] {1,2}Κ ?Α ?[ΙΗ]\s{1,2}Α ?Κ ?Α ?Ρ ?Ν ?Α ?Ν ?[ΙΗ] ?Α ?[Σ\u03a2]',
                text, re.MULTILINE):
            return cls.AETOLIA_ACARNANIA
        elif re.match(r'ΑΡΓΟ ?Λ ?[ΙΗ][ΔΓ] ?Ο ?[Σ\u03a2]', text):
            return cls.ARGOLIS
        elif re.match(r'Α ?Ρ ?ΚΑ ?[ΔΓ][ΙΗ]Α[Σ\u03a2]', text):
            return cls.ARKADIAS
        elif re.match(r'Α ?Ρ ?[ΤΣ] ?[ΗΖ][Σ\u03a2]', text):
            return cls.ARTA
        elif re.match(r'Α ?[ΧΥ] ?Α ?Ϊ ?Α ?[Σ\u03a2]', text):
            return cls.ACHAEA
        elif re.match(r'Β ?Ο ?[ΙΗ] ?Ω ?[ΤΣ] ?[ΙΗ] ?Α ?[Σ\u03a2]', text):
            return cls.BOEOTIA
        elif re.match(r'[ΔΓ]ΡΑΜΑ ?[Σ\u03a2]', text):
            return cls.DRAMA
        elif re.match(r'Γ ?Ρ ?[ΕΔ] ?Β ?[ΕΔ] ?Ν ?Ω ?Ν', text):
            return cls.GREVENA
        elif re.match(r'[ΔΓ] ?Ω[ΔΓ] ?[ΕΔ] ?ΚΑΝ[ΗΖ] ?[Σ\u03a2]Ο[ΤΥ]', text):
            return cls.DODECANESE
        elif re.match(r'[ΕΔ] ?Β ?Ρ ?Ο ?[ΥΤ]', text):
            return cls.EVROS
        elif re.match(r'[ΕΔ] ?[ΥΤ] ?Β ?Ο ?[ΙΗ] ?Α ?[Σ\u03a2]', text):
            return cls.EUBOEA
        elif re.match(r'[ΕΔ][ΥΤ]Ρ ?[ΥΤ] ?[ΤΣ]Α ?Ν ?[ΙΗ]Α[Σ\u03a2]', text):
            return cls.EVRYTANIA
        elif re.match(r'[ΖΕ] ?Α ?Κ ?[ΥΤ]Ν ?Θ ?Ο ?[ΥΤ]', text):
            return cls.ZAKYNTHOS
        elif re.match(r'[ΗΖ] ?Λ[ΕΔ] ?[ΙΗ]Α ?[Σ\u03a2]', text):
            return cls.ELIS
        elif re.match(r'[ΗΖ] ?Μ ?Α ?Θ ?[ΙΗ] ?Α ?[Σ\u03a2]', text):
            return cls.IMATHIA
        elif re.match(r'[ΗΖ] ?Ρ ?Α ?Κ ?Λ ?[ΕΔ] ?[ΙΗ] ?Ο ?[ΥΤ]', text):
            return cls.HERAKLION
        elif re.match(r'Θ[ΕΔ] ?[Σ\u03a2]Π ?ΡΩ ?[ΤΣ][ΙΗ]Α ?[Σ\u03a2]', text):
            return cls.THESPROTIA
        elif re.match(r'Θ[ΕΔ] ?[Σ\u03a2][Σ|\u03a2] ?Α ?ΛΟΝ[ΙΗ] ?Κ ?[ΗΖ][Σ|\u03a2]', text):
            return cls.THESSALONIKI
        elif re.match(r'[ΙΗ] ?Ω ?Α ?Ν ?Ν ?[ΙΗ] ?Ν ?Ω ?Ν', text):
            return cls.IOANNINA
        elif re.match(r'ΚΑ ?Β ?Α ?Λ ?Α ?[Σ|\u03a2]', text):
            return cls.KAVALA
        elif re.match(r'Κ ?Α ?Ρ ?[ΔΓ] ?[ΙΗ] ?Τ? ?Σ[ \u03a2]?[ΗΖ] ?[Σ|\u03a2]', text):
            return cls.KARDITSA
        elif re.match(r'Κ ?Α ?[Σ\u03a2] ?[ΤΣ]ΟΡ ?[ΙΗ] ?Α ?[Σ\u03a2]', text):
            return cls.KASTORIA
        elif re.match(r'Κ[ΕΔ]ΡΚ[ΥΤ]ΡΑ[Σ\u03a2]', text):
            return cls.KERKYRA
        elif re.match(r'Κ[ΕΔ]ΦΑΛΛ[ΗΖ] ?Ν ?[ΙΗ]Α ?[Σ\u03a2]', text):
            return cls.CEPHALONIA
        elif re.match(r'Κ ?[ΙΗ] ?Λ ?Κ ?[ΙΗ] ?[Σ\u03a2]', text):
            return cls.KILKIS
        elif re.match(r'Κ ?Ο ?[ΖΕ] ?Α ?Ν ?[ΗΖ] ?[Σ\u03a2]', text):
            return cls.KOZANI
        elif re.match(r'Κ ?Ο ?Ρ ?[ΙΗ] ?Ν ?Θ ?[ΙΗ] ?Α ?[Σ\u03a2]', text):
            return cls.CORINTHIA
        elif re.match(r'Κ[ΥΤ]ΚΛΑ ?[ΔΓ]ΩΝ', text):
            return cls.CYCLADES
        elif re.match(r'ΛΑΚ ?ΩΝ ?[ΙΗ]Α[Σ\u03a2]', text):
            return cls.LACONIA
        elif re.match(r'ΛΑΡ ?[ΙΗ] ?[Σ\u03a2][ΗΖ] ?[Σ\u03a2]', text):
            return cls.LARISSA
        elif re.match(r'Λ ?Α ?[Σ\u03a2] ?[ΙΗ] ?Θ ?[ΙΗ] ?Ο ?[ΥΤ]', text):
            return cls.LASITHI
        elif re.match(r'Λ ?[ΕΔ] ?[Σ\u03a2]Β ?Ο ?[ΥΤ]', text):
            return cls.LESBOS
        elif re.match(r'Λ ?[ΕΔ] ?[ΥΤ]Κ ?Α[ΔΓ]Ο ?[Σ\u03a2]', text):
            return cls.LEFKADA
        elif re.match(r'ΜΑΓ ?Ν[ΗΖ][Σ\u03a2][ΙΗ] ?Α[Σ\u03a2]', text):
            return cls.MAGNESIA
        elif re.match(r'Μ[ΕΔ][Σ\u03a2] ?[Σ\u03a2] ?[ΗΖ]Ν[ΙΗ]Α ?[Σ\u03a2]', text):
            return cls.MESSENIA
        elif re.match(r'Ξ ?Α ?Ν ?Θ ?[ΗΖ] ?[Σ\u03a2]', text):
            return cls.XANTHI
        elif re.match(r'Π ?[ΕΔ] ?Λ ?Λ ?[ΗΖ] ?[Σ\u03a2]', text):
            return cls.PELLA
        elif re.match(r'Π ?[ΙΗ] ?[ΕΔ] ?Ρ ?[ΙΗ] ?Α ?[Σ\u03a2]', text):
            return cls.PIERIA
        elif re.match(r'ΠΡ ?[ΕΔ] ?Β[ΕΔ][ΖΕ][ΗΖ][Σ\u03a2]', text):
            return cls.PREVEZA
        elif re.match(r'Ρ[ΕΔ]Θ[ΥΤ]Μ ?Ν[ΗΖ][Σ\u03a2]', text):
            return cls.RETHYMNO
        elif re.match(r'ΡΟ ?[ΔΓ]Ο ?Π ?[ΗΖ] ?[Σ\u03a2]', text):
            return cls.RHODOPE
        elif re.match(r'[Σ\u03a2]ΑΜ ?Ο ?[ΥΤ]', text):
            return cls.SAMOS
        elif re.match(r'[Σ\u03a2] ?[ΕΔ] ?Ρ ?Ρ ?Ω ?Ν', text):
            return cls.SERRES
        elif re.match(r'[ΤΣ] ?Ρ ?[ΙΗ] ?Κ ?Α ?Λ ?Ω ?Ν', text):
            return cls.TRIKALA
        elif re.match(r'Φ ?Θ ?[ΙΗ] ?Ω ?[ΤΣ] ?[ΙΗ][ΔΓ] ?Ο ?[Σ\u03a2]', text):
            return cls.PHTHIOTIS
        elif re.match(r'ΦΛΩ ?Ρ[ΙΗ]Ν[ΗΖ] ?[Σ\u03a2]', text):
            return cls.FLORINA
        elif re.match(r'Φ ?Ω ?Κ ?[ΙΗ] ?[ΔΓ] ?Ο ?[Σ\u03a2]', text):
            return cls.PHOCIS
        elif re.match(r'[ΧΥ] ?Α ?Λ ?Κ ?[ΙΗ] ?[ΔΓ] ?[ΙΗ] ?Κ ?[ΗΖ] ?[Σ\u03a2]', text):
            return cls.CHALKIDIKI
        elif re.match(r'[ΧΥ]Α ?Ν ?[ΙΗ] ?Ω ?Ν', text):
            return cls.CHANIA
        elif re.match(r'[ΧΥ] ?[ΙΗ] ?Ο ?[ΥΤ]', text):
            return cls.CHIOS
