"""Module for parsing data
"""
import abc
import datetime
import decimal
import logging
import pathlib
import re

import pypdf
import pypdf.errors

from fuelpricesgr import enums

# The module logger
logger = logging.getLogger(__name__)

# The fuel type regexes
_FUEL_TYPE_REGEXES = {
    enums.FuelType.UNLEADED_95: r'Αμόλ ?[υσ]βδ ?[ηθ] +9 ?5 +ο ?κ ?τ ?\.',
    enums.FuelType.UNLEADED_100: r'Αμόλ[υσ] ?β ?δ[ηθ] 100 οκτ\.',
    enums.FuelType.SUPER: r'Super',
    enums.FuelType.DIESEL: r'Diesel +Κ ?ί ?ν ?[ηθ] ?[σς] ?[ηθ] ?[ςσ]',
    enums.FuelType.DIESEL_HEATING: r'Dies ?e ?l +Θ ?[έζ] ?ρ ?μ ?α ?ν ?[σς] ?[ηθ] ?[ςσ] +Κ ?α ?τ ?΄ ?ο ?ί ?κ ?ο ?ν',
    enums.FuelType.GAS: r'[ΥΤ]γρα[έζ]ρ ?ιο +κί ?ν ?[ηθ] ?[σς] ?[ηθ][ςσ] +\( ?A ?ut ?o ?g ?a ?s ?\)',
}

# The fuel type values regexes
_FUEL_TYPE_VALUES_REGEXES = {
    enums.FuelType.UNLEADED_95: r'\s*(?P<number_of_stations>\d\.\d{3})? +(?P<price>\d,[\d ]{3,4})',
    enums.FuelType.UNLEADED_100: r'\s*(?P<number_of_stations>\d\.\d{3})? +(?P<price>\d,[\d ]{3,4})',
    enums.FuelType.DIESEL: r'\s*(?P<number_of_stations>(?:\d\.)?\d{3})? +(?P<price>\d,[\d ]{3,4})',
    enums.FuelType.GAS: r'\s*(?P<number_of_stations>(?:\d\.)?\d{3})? +(?P<price>\d,[\d ]{3,4})',
    enums.FuelType.DIESEL_HEATING: r'\s*(?P<number_of_stations>(?:\d\.)?\d{3})? +(?P<price>\d,[\d ]{3,4})',
    enums.FuelType.SUPER: r'\s*(?P<number_of_stations>(?:\d\.)?\d{1,3})? +(?P<price>\d[,.][\d ]{3,4})'
}

# The prefecture regexes
_PREFECTURE_REGEXES = {
    enums.Prefecture.ATTICA: r'Α\s?Τ\s?Τ\s?Ι\s?Κ\s?Η\s?Σ',
    enums.Prefecture.AETOLIA_ACARNANIA:
        r'Α\s?Ι\s?Τ\s?Ω\s?Λ\s?Ι\s?Α\s?Σ\s{1,2}Κ\s?Α\s?Ι\s{1,2}Α\s?Κ\s?Α\s?Ρ\s?Ν\s?Α\s?Ν\s?Ι\s?Α\s?Σ',
    enums.Prefecture.ARGOLIS: r'Α\s?Ρ\s?Γ\s?Ο\s?Λ\s?Ι\s?Δ\s?Ο\s?Σ',
    enums.Prefecture.ARKADIAS: r'ΑΡΚ\s?Α\s?ΔΙΑ\s?Σ',
    enums.Prefecture.ARTA: r'Α\s?Ρ\s?Τ\s?ΗΣ',
    enums.Prefecture.ACHAEA: r'Α\s?Χ\s?Α\s?Ϊ\s?Α\s?Σ',
    enums.Prefecture.BOEOTIA: r'Β\s?Ο\s?Ι\s?Ω\s?Τ\s?Ι\s?Α\s?Σ',
    enums.Prefecture.GREVENA: r'Γ\s?Ρ\s?Ε\s?Β\s?Ε\s?Ν\s?Ω\s?Ν',
    enums.Prefecture.DRAMA: r'Δ\s?Ρ\s?Α\s?Μ\s?Α\s?Σ',
    enums.Prefecture.DODECANESE: r'Δ\s?Ω\s?Δ\s?Ε\s?ΚΑ\s?Ν\s?Η\s?ΣΟ\s?Υ',
    enums.Prefecture.EVROS: r'Ε\s?Β\s?Ρ\s?Ο\s?Υ',
    enums.Prefecture.EUBOEA: r'Ε\s?Υ\s?Β\s?Ο\s?Ι\s?Α\s?Σ',
    enums.Prefecture.EVRYTANIA: r'ΕΥ\s?Ρ\s?Υ\s?Τ\s?Α\s?Ν\s?ΙΑΣ',
    enums.Prefecture.ZAKYNTHOS: r'Ζ\s?Α\s?Κ\s?Υ\s?Ν\s?Θ\s?Ο\s?Υ',
    enums.Prefecture.ELIS: r'Η\s?Λ\s?Ε\s?ΙΑ\s?Σ',
    enums.Prefecture.IMATHIA: r'Η\s?Μ\s?Α\s?Θ\s?Ι\s?Α\s?Σ',
    enums.Prefecture.HERAKLION: r'Η\s?Ρ\s?Α\s?Κ\s?Λ\s?Ε\s?Ι\s?Ο\s?Υ',
    enums.Prefecture.THESPROTIA: r'Θ\s?Ε\s?Σ\s?Π\s?Ρ\s?ΩΤ\s?Ι\s?Α\s?Σ',
    enums.Prefecture.THESSALONIKI: r'Θ\s?Ε\s?Σ\s?Σ\s?Α\s?Λ\s?Ο\s?Ν\s?Ι\s?Κ\s?Η\s?Σ',
    enums.Prefecture.IOANNINA: r'Ι\s?Ω\s?Α\s?Ν\s?Ν\s?Ι\s?Ν\s?Ω\s?Ν',
    enums.Prefecture.KAVALA: r'ΚΑ\s?Β\s?Α\s?Λ\s?Α\s?Σ',
    enums.Prefecture.KARDITSA: r'Κ\s?Α\s?Ρ\s?Δ\s?Ι\s?Τ\s?Σ\s?Η\s?Σ',
    enums.Prefecture.KASTORIA: r'Κ\s?Α\s?Σ\s?Τ\s?Ο\s?Ρ\s?Ι\s?Α\s?Σ',
    enums.Prefecture.KERKYRA: r'Κ\s?Ε\s?Ρ\s?ΚΥ\s?ΡΑΣ',
    enums.Prefecture.CEPHALONIA: r'Κ\s?ΕΦ\s?Α\s?Λ\s?ΛΗ\s?ΝΙ\s?Α\s?Σ',
    enums.Prefecture.KILKIS: r'Κ\s?Ι\s?Λ\s?Κ\s?Ι\s?Σ',
    enums.Prefecture.KOZANI: r'Κ\s?Ο\s?Ζ\s?Α\s?Ν\s?Η\s?Σ',
    enums.Prefecture.CORINTHIA: r'Κ\s?Ο\s?Ρ\s?Ι\s?Ν\s?Θ\s?Ι\s?Α\s?Σ',
    enums.Prefecture.CYCLADES: r'Κ\s?Υ\s?Κ\s?Λ\s?Α\s?Δ\s?Ω\s?Ν',
    enums.Prefecture.LACONIA: r'Λ\s?Α\s?Κ\s?Ω\s?Ν\s?Ι\s?Α\s?Σ',
    enums.Prefecture.LARISSA: r'ΛΑ\s?Ρ\s?Ι\s?ΣΗ\s?Σ',
    enums.Prefecture.LASITHI: r'Λ\s?Α\s?Σ\s?Ι\s?Θ\s?Ι\s?Ο\s?Υ',
    enums.Prefecture.LESBOS: r'Λ\s?Ε\s?ΣΒ\s?Ο\s?Υ',
    enums.Prefecture.LEFKADA: r'Λ\s?Ε\s?Υ\s?Κ\s?Α\s?Δ\s?Ο\s?Σ',
    enums.Prefecture.MAGNESIA: r'Μ\s?Α\s?Γ\s?Ν\s?Η\s?Σ\s?Ι\s?Α\s?Σ',
    enums.Prefecture.MESSENIA: r'ΜΕ\s?ΣΣ\s?Η\s?ΝΙΑ\s?Σ',
    enums.Prefecture.XANTHI: r'Ξ\s?Α\s?Ν\s?Θ\s?Η\s?Σ',
    enums.Prefecture.PELLA: r'Π\s?Ε\s?Λ\s?Λ\s?Η\s?Σ',
    enums.Prefecture.PIERIA: r'Π\s?Ι\s?Ε\s?Ρ\s?Ι\s?Α\s?Σ',
    enums.Prefecture.PREVEZA: r'Π\s?Ρ\s?Ε\s?Β\s?ΕΖ\s?Η\s?Σ',
    enums.Prefecture.RETHYMNO: r'Ρ\s?Ε\s?Θ\s?Υ\s?Μ\s?Ν\s?Η\s?Σ',
    enums.Prefecture.RHODOPE: r'ΡΟ\s?ΔΟ\s?Π\s?Η\s?Σ',
    enums.Prefecture.SAMOS: r'Σ\s?Α\s?Μ\s?Ο\s?Υ',
    enums.Prefecture.SERRES: r'Σ\s?Ε\s?Ρ\s?Ρ\s?Ω\s?Ν',
    enums.Prefecture.TRIKALA: r'Τ\s?Ρ\s?Ι\s?Κ\s?Α\s?Λ\s?Ω\s?Ν',
    enums.Prefecture.PHTHIOTIS: r'Φ\s?Θ\s?Ι\s?Ω\s?Τ\s?Ι\s?Δ\s?Ο\s?Σ',
    enums.Prefecture.FLORINA: r'Φ\s?Λ\s?ΩΡ\s?Ι\s?Ν\s?Η\s?Σ',
    enums.Prefecture.PHOCIS: r'Φ\s?Ω\s?Κ\s?Ι\s?Δ\s?Ο\s?Σ',
    enums.Prefecture.CHALKIDIKI: r'Χ\s?Α\s?Λ\s?Κ\s?Ι\s?Δ\s?Ι\s?Κ\s?Η\s?Σ',
    enums.Prefecture.CHANIA: r'Χ\s?ΑΝ\s?Ι\s?Ω\s?Ν',
    enums.Prefecture.CHIOS: r'Χ\s?Ι\s?Ο\s?Υ',
}


def data_should_exist(fuel_type: enums.FuelType, date: datetime.date) -> bool:
    """Returns true if the data should exist for the specified fuel type and date.

    :param fuel_type: The fuel type.
    :param date: The date.
    :return: True if the data should exist.
    """
    if fuel_type == enums.FuelType.SUPER and date >= datetime.date(2022, 8, 5):
        # Last date with SUPER data
        return False
    elif fuel_type == enums.FuelType.GAS and date <= datetime.date(2012, 6, 1):
        # There are no data for GAS for these old dates
        return False
    elif (
        fuel_type == enums.FuelType.DIESEL_HEATING and
        not ((date.month >= 10 and date.day >= 15) or (date.month <= 4))
    ):
        # No DIESEL_HEATING for this period
        return False

    return True


class Parser(abc.ABC):
    """Class to parse data files
    """
    # Regex to get date from file name
    DATE_PARSING_REGEX = re.compile(r'(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2}).pdf$')

    @staticmethod
    def get(data_file_type: enums.DataFileType) -> 'Parser':
        """Get the parser object.
        """
        match data_file_type:
            case enums.DataFileType.WEEKLY:
                return WeeklyParser()
            case enums.DataFileType.DAILY_COUNTRY:
                return DailyCountryParser()
            case enums.DataFileType.DAILY_PREFECTURE:
                return DailyPrefectureParser()
            case _:
                raise NotImplementedError()

    @staticmethod
    def read_text(file: pathlib.Path) -> str | None:
        """Extract the text from the file.

        :param file: The file.
        :return: The extracted text.
        """
        logger.debug("Parsing file %s", file)
        try:
            reader = pypdf.PdfReader(file)
        except pypdf.errors.PdfReadError:
            logger.error("Could not extract text from file %s", file, exc_info=True)
            return None

        text = ''.join(page.extract_text() for page in reader.pages)
        if not text:
            logger.error("No text found in file %s", file)
            return None

        return text

    def parse(self, file: pathlib.Path) -> dict[enums.DataType, list[dict]] | None:
        """Parse the file to get the data.

        :param file: The file.
        :return: The file data.
        """
        text = self.read_text(file=file)
        match = self.DATE_PARSING_REGEX.match(file.name)
        if not match:
            logger.error("Could not parse file name %s", file.name)
            return None
        date = datetime.date(
            year=int(match.group('year')), month=int(match.group('month')), day=int(match.group('day')))

        if text:
            return self.extract_data(text=text, date=date)

    @staticmethod
    def get_number_of_stations(number_of_stations_text: str) -> int | None:
        """Get the number of stations from the matched text.

        :param number_of_stations_text: The number of stations text.
        :return: The number of stations, if they can be found.
        """
        if number_of_stations_text:
            return int(number_of_stations_text.replace('.', ''))

    @staticmethod
    def get_price(price_text: str) -> decimal.Decimal | None:
        """Get the price from the matched text.

        :param price_text: The price text.
        :return: The price.
        """
        price_text = price_text.replace(' ', '').replace(',', '.').replace('-', '').strip()
        if price_text:
            return decimal.Decimal(price_text)

    @abc.abstractmethod
    def extract_data(self, text: str, date: datetime.date) -> dict[enums.DataType, list[dict]] | None:
        """Extract weekly country and prefecture data.

        :param text: The file text.
        :param date: The date for the file.
        :return: The data.
        """

    @staticmethod
    def extract_country_data(text: str, date: datetime.date, weekly: bool):
        """Extract the country data.

        :param text: The country data text.
        :param date: The date.
        :param weekly: True if the data are weekly.
        :return: The weekly country data.
        """
        data = []

        for fuel_type in enums.FuelType:
            regex = _FUEL_TYPE_REGEXES[fuel_type] + _FUEL_TYPE_VALUES_REGEXES[fuel_type]
            if match := re.search(regex, text):
                data.append({
                    'fuel_type': fuel_type.value,
                    'number_of_stations': Parser.get_number_of_stations(match.group('number_of_stations')),
                    'price': Parser.get_price(match.group('price')),
                })
            elif data_should_exist(fuel_type, date):
                logger.error("Could not find %s %s country data for date %s", fuel_type.description,
                             "weekly" if weekly else "daily", date)

        return data

    @staticmethod
    def extract_prefecture_data(text: str, date: datetime.date, weekly: bool):
        """Extract the weekly prefecture data.

        :param text: The weekly prefecture data text.
        :param date: The date.
        :param weekly: The date.
        :return: The weekly prefecture data.
        """
        # The standard fuel types included
        fuel_types = [
            enums.FuelType.UNLEADED_95, enums.FuelType.UNLEADED_100, enums.FuelType.DIESEL, enums.FuelType.GAS
        ]
        regexes = [r' +(\d,\d ?\d ?\d)', r' +((?:\d,\d ?\d ?\d|-))', r' +(\d,\d ?\d ?\d)', r' +((?:\d,\d ?\d ?\d|-))']
        # Check if super is included
        if re.search(r'Super', text):
            regexes.insert(2, r' +((?:\d(?:,|\.)\d ?\d ?\d|-|\s+))')
            fuel_types.insert(2, enums.FuelType.SUPER)
        # Check if diesel heating is included
        if data_should_exist(enums.FuelType.DIESEL_HEATING, date):
            regexes.append(r' +((?:\d,\d ?\d ?\d|-))')
            fuel_types.append(enums.FuelType.DIESEL_HEATING)

        data = []
        for prefecture in enums.Prefecture:
            # Parse the prices
            regex = r'Ν ?Ο ?Μ ?Ο ?Σ\s{1,2}' + _PREFECTURE_REGEXES[prefecture] + ''.join(regexes)
            if match := re.search(regex, text):
                for index, fuel_type in enumerate(fuel_types):
                    price = WeeklyParser.get_price(match.group(index + 1))
                    if price:
                        data.append({
                            'prefecture': prefecture.value,
                            'fuel_type': fuel_type.value,
                            'price': price,
                        })
            else:
                logger.error("Could not find %s prefecture data for %s and date %s", 'weekly' if weekly else 'daily',
                             prefecture.description, date)

        return data


class WeeklyParser(Parser):
    """Parser for weekly data files
    """
    def extract_data(self, text: str, date: datetime.date) -> dict[enums.DataType, list[dict]] | None:
        """Extract weekly country and prefecture data.

        :param text: The file text.
        :param date: The date for the file.
        :return: The data.
        """
        # Extract weekly country data
        # Try to find "Μέσες τιμές λιανικής πώλησης καυσίμων ανά Νομό"
        weekly_country_end_data = re.search(
            r'Μέσες τιμές λ ?ιανι ?κή ?ς +πώ ?λη ?σης ?κ ?α ?υ ?σ ?ί ?μ ?ω ?ν +α ?ν ?ά [Νν] ?ο ?μ ?ό', text,
            re.MULTILINE)
        if not weekly_country_end_data:
            # Try to find "Η μέση τιμή πανελλαδικά υπολογίζεται απο τον σταθμισμένο μέσο όρο"
            weekly_country_end_data = re.search(
                r'\* *Η [μκ][έζ] ?[σςζ][ηθε] +[τη][ιη][μκ] *[ήι] πα ?[νλ] ?ε[λι] ?[λι] ?αδ ?[ιη][κθ] ?ά +'
                r'[υπ] ?π ?[ον] ?[λι] ?[ον] ?γ ?ί ?[ζηδ] ?ε ?[τη] ?α ?[ιη] +α ?π ?ό +[τη] ?[ον][νλ]\s+'
                r'[σςζ][τη] ?α[θκζ] ?[μκ] ?[ιη] ?[ιζσς] ?[μκ] ?[έζ][νλ][ον]\s+[μκ] ?[έζ] ?[σςζ] ?[ον]\s+ό[ρξ][ον]',
                text, re.MULTILINE)
        if not weekly_country_end_data:
            raise ValueError(f"Could not find weekly country data for date %s", date.isoformat())
        country_data = self.extract_country_data(text[:weekly_country_end_data.start(0)], date, True)

        # Extract weekly country data
        # Try to find "2. Απλή Αμόλυβδη Βενζίνη 95 οκτανίων"
        weekly_prefecture_end_data = re.search(
            r'2\. *Απλ[ήι] +Αμ ?όλ ?υβδ ?[ηθ] Β ?ε ?ν ?[ζη] ?ί ?ν ?[ηθ] +9 ?5 οκ ?τα ?ν ?ίω ?ν', text)
        if not weekly_prefecture_end_data:
            raise ValueError(f"Could not find weekly prefecture data for date {date.isoformat()}")
        prefecture_data = self.extract_prefecture_data(
            text[weekly_country_end_data.end(0):weekly_prefecture_end_data.start(0)], date, True)

        return {enums.DataType.WEEKLY_COUNTRY: country_data, enums.DataType.WEEKLY_PREFECTURE: prefecture_data}


class DailyCountryParser(Parser):
    """Parser for daily country data files
    """
    def extract_data(self, text: str, date: datetime.date) -> dict[enums.DataType, list[dict]] | None:
        """Extract daily country data.

        :param text: The file text.
        :param date: The date for the file.
        :return: The data.
        """
        return {enums.DataType.DAILY_COUNTRY: self.extract_country_data(text, date, False)}


class DailyPrefectureParser(Parser):
    """Parser for daily prefecture data files
    """
    def extract_data(self, text: str, date: datetime.date) -> dict[enums.DataType, list[dict]] | None:
        """Extract daily prefecture data.

        :param text: The file text.
        :param date: The date for the file.
        :return: The data.
        """
        return {enums.DataType.DAILY_PREFECTURE: self.extract_prefecture_data(text, date, False)}
