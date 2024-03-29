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

# Months that can contain diesel heading data
DIESEL_HEATING_MONTHS = {10, 11, 12, 1, 2, 3, 4, 5}

# The final date for Super data
SUPER_FINAL_DATE = datetime.date(2022, 8, 12)


class Parser(abc.ABC):
    """Class to parse data files
    """
    # Regex to get date from file name
    DATE_PARSING_REGEX = re.compile(r'(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2}).pdf$')
    # The regular expressions used to find the prefectures from the PDF text.
    PREFECTURE_REGEXES = {
        enums.Prefecture.ATTICA: re.compile(r'Α ?[ΤΣ] ?[ΤΣ] ?[ΙΗ] ?Κ ?[ΗΖ] ?[Σ\u03a2]', re.MULTILINE),
        enums.Prefecture.AETOLIA_ACARNANIA: re.compile(
            r'Α ?[ΙΗ] ?[ΤΣ] ?Ω ?Λ ?[ΙΗ] ?Α ?[Σ\u03a2] {1,2}Κ ?Α ?[ΙΗ]\s{1,2}Α ?Κ ?Α ?Ρ ?Ν ?Α ?Ν ?[ΙΗ] ?Α ?[Σ\u03a2]',
            re.MULTILINE),
        enums.Prefecture.ARGOLIS: re.compile(r'Α ?Ρ ?Γ ?Ο ?Λ ?[ΙΗ] ?[ΔΓ] ?Ο ?[Σ\u03a2]', re.MULTILINE),
        enums.Prefecture.ARKADIAS: re.compile(r'Α ?Ρ ?Κ ?Α ?[ΔΓ] ?[ΙΗ] ?Α ?[Σ\u03a2]', re.MULTILINE),
        enums.Prefecture.ARTA: re.compile(r'Α ?Ρ ?[ΤΣ] ?[ΗΖ] ?[Σ\u03a2]', re.MULTILINE),
        enums.Prefecture.ACHAEA: re.compile(r'Α ?[ΧΥ] ?Α ?Ϊ ?Α ?[Σ\u03a2]', re.MULTILINE),
        enums.Prefecture.BOEOTIA: re.compile(r'Β ?Ο ?[ΙΗ] ?Ω ?[ΤΣ] ?[ΙΗ] ?Α ?[Σ\u03a2]', re.MULTILINE),
        enums.Prefecture.DRAMA: re.compile(r'[ΔΓ] ?Ρ ?Α ?Μ ?Α ?[Σ\u03a2]', re.MULTILINE),
        enums.Prefecture.GREVENA: re.compile(r'Γ ?Ρ ?[ΕΔ] ?Β ?[ΕΔ] ?Ν ?Ω ?Ν', re.MULTILINE),
        enums.Prefecture.DODECANESE: re.compile(r'[ΔΓ] ?Ω ?[ΔΓ] ?[ΕΔ] ?Κ ?Α ?Ν ?[ΗΖ] ?[Σ\u03a2] ?Ο ?[ΤΥ]',
                                                re.MULTILINE),
        enums.Prefecture.EVROS: re.compile(r'[ΕΔ] ?Β ?Ρ ?Ο ?[ΥΤ]', re.MULTILINE),
        enums.Prefecture.EUBOEA: re.compile(r'[ΕΔ] ?[ΥΤ] ?Β ?Ο ?[ΙΗ] ?Α ?[Σ\u03a2]', re.MULTILINE),
        enums.Prefecture.EVRYTANIA: re.compile(r'[ΕΔ] ?[ΥΤ] ?Ρ ?[ΥΤ] ?[ΤΣ] ?Α ?Ν ?[ΙΗ] ?Α ?[Σ\u03a2]', re.MULTILINE),
        enums.Prefecture.ZAKYNTHOS: re.compile(r'[ΖΕ] ?Α ?Κ ?[ΥΤ] ?Ν ?Θ ?Ο ?[ΥΤ]', re.MULTILINE),
        enums.Prefecture.ELIS: re.compile(r'[ΗΖ] ?Λ ?[ΕΔ] ?[ΙΗ] ?Α ?[Σ\u03a2]', re.MULTILINE),
        enums.Prefecture.IMATHIA: re.compile(r'[ΗΖ] ?Μ ?Α ?Θ ?[ΙΗ] ?Α ?[Σ\u03a2]', re.MULTILINE),
        enums.Prefecture.HERAKLION: re.compile(r'[ΗΖ] ?Ρ ?Α ?Κ ?Λ ?[ΕΔ] ?[ΙΗ] ?Ο ?[ΥΤ]', re.MULTILINE),
        enums.Prefecture.THESPROTIA: re.compile(r'Θ ?[ΕΔ] ?[Σ\u03a2] ?Π ?Ρ ?Ω ?[ΤΣ] ?[ΙΗ] ?Α ?[Σ\u03a2]', re.MULTILINE),
        enums.Prefecture.THESSALONIKI: re.compile(
            r'Θ ?[ΕΔ] ?[Σ\u03a2] ?[Σ|\u03a2] ?Α ?Λ ?Ο ?Ν ?[ΙΗ] ?Κ ?[ΗΖ] ?[Σ\u03a2]', re.MULTILINE),
        enums.Prefecture.IOANNINA: re.compile(r'[ΙΗ] ?Ω ?Α ?Ν ?Ν ?[ΙΗ] ?Ν ?Ω ?Ν', re.MULTILINE),
        enums.Prefecture.KAVALA: re.compile(r'Κ ?Α ?Β ?Α ?Λ ?Α ?[Σ|\u03a2]', re.MULTILINE),
        enums.Prefecture.KARDITSA: re.compile(r'Κ ?Α ?Ρ ?[ΔΓ] ?[ΙΗ] ?Τ? ?Σ ?[ \u03a2]?[ΗΖ] ?[Σ|\u03a2]', re.MULTILINE),
        enums.Prefecture.KASTORIA: re.compile(r'Κ ?Α ?[Σ\u03a2] ?[ΤΣ] ?Ο ?Ρ ?[ΙΗ] ?Α ?[Σ\u03a2]', re.MULTILINE),
        enums.Prefecture.KERKYRA: re.compile(r'Κ ?[ΕΔ] ?Ρ ?Κ ?[ΥΤ] ?Ρ ?Α ?[Σ\u03a2]', re.MULTILINE),
        enums.Prefecture.CEPHALONIA: re.compile(r'Κ ?[ΕΔ] ?Φ ?Α ?Λ ?Λ ?[ΗΖ] ?Ν ?[ΙΗ] ?Α ?[Σ\u03a2]', re.MULTILINE),
        enums.Prefecture.KILKIS: re.compile(r'Κ ?[ΙΗ] ?Λ ?Κ ?[ΙΗ] ?[Σ\u03a2]', re.MULTILINE),
        enums.Prefecture.KOZANI: re.compile(r'Κ ?Ο ?[ΖΕ] ?Α ?Ν ?[ΗΖ] ?[Σ\u03a2]', re.MULTILINE),
        enums.Prefecture.CORINTHIA: re.compile(r'Κ ?Ο ?Ρ ?[ΙΗ] ?Ν ?Θ ?[ΙΗ] ?Α ?[Σ\u03a2]', re.MULTILINE),
        enums.Prefecture.CYCLADES: re.compile(r'Κ ?[ΥΤ] ?Κ ?Λ ?Α ?[ΔΓ] ?Ω ?Ν', re.MULTILINE),
        enums.Prefecture.LACONIA: re.compile(r'Λ ?Α ?Κ ?Ω ?Ν ?[ΙΗ] ?Α ?[Σ\u03a2]', re.MULTILINE),
        enums.Prefecture.LARISSA: re.compile(r'Λ ?Α ?Ρ ?[ΙΗ] ?[Σ\u03a2] ?[ΗΖ] ?[Σ\u03a2]', re.MULTILINE),
        enums.Prefecture.LASITHI: re.compile(r'Λ ?Α ?[Σ\u03a2] ?[ΙΗ] ?Θ ?[ΙΗ] ?Ο ?[ΥΤ]', re.MULTILINE),
        enums.Prefecture.LESBOS: re.compile(r'Λ ?[ΕΔ] ?[Σ\u03a2]Β ?Ο ?[ΥΤ]', re.MULTILINE),
        enums.Prefecture.LEFKADA: re.compile(r'Λ ?[ΕΔ] ?[ΥΤ] ?Κ ?Α ?[ΔΓ] ?Ο ?[Σ\u03a2]', re.MULTILINE),
        enums.Prefecture.MAGNESIA: re.compile(r'Μ ?Α ?Γ ?Ν ?[ΗΖ] ?[Σ\u03a2] ?[ΙΗ] ?Α ?[Σ\u03a2]', re.MULTILINE),
        enums.Prefecture.MESSENIA: re.compile(r'Μ ?[ΕΔ] ?[Σ\u03a2] ?[Σ\u03a2] ?[ΗΖ] ?Ν ?[ΙΗ] ?Α ?[Σ\u03a2]',
                                              re.MULTILINE),
        enums.Prefecture.XANTHI: re.compile(r'Ξ ?Α ?Ν ?Θ ?[ΗΖ] ?[Σ\u03a2]', re.MULTILINE),
        enums.Prefecture.PELLA: re.compile(r'Π ?[ΕΔ] ?Λ ?Λ ?[ΗΖ] ?[Σ\u03a2]', re.MULTILINE),
        enums.Prefecture.PIERIA: re.compile(r'Π ?[ΙΗ] ?[ΕΔ] ?Ρ ?[ΙΗ] ?Α ?[Σ\u03a2]', re.MULTILINE),
        enums.Prefecture.PREVEZA: re.compile(r'Π ?Ρ ?[ΕΔ] ?Β ?[ΕΔ] ?[ΖΕ] ?[ΗΖ] ?[Σ\u03a2]', re.MULTILINE),
        enums.Prefecture.RETHYMNO: re.compile(r'Ρ ?[ΕΔ] ?Θ ?[ΥΤ] ?Μ ?Ν ?[ΗΖ] ?[Σ\u03a2]', re.MULTILINE),
        enums.Prefecture.RHODOPE: re.compile(r'Ρ ?Ο ?[ΔΓ] ?Ο ?Π ?[ΗΖ] ?[Σ\u03a2]', re.MULTILINE),
        enums.Prefecture.SAMOS: re.compile(r'[Σ\u03a2] ?Α ?Μ ?Ο ?[ΥΤ]', re.MULTILINE),
        enums.Prefecture.SERRES: re.compile(r'[Σ\u03a2] ?[ΕΔ] ?Ρ ?Ρ ?Ω ?Ν', re.MULTILINE),
        enums.Prefecture.TRIKALA: re.compile(r'[ΤΣ] ?Ρ ?[ΙΗ] ?Κ ?Α ?Λ ?Ω ?Ν', re.MULTILINE),
        enums.Prefecture.PHTHIOTIS: re.compile(r'Φ ?Θ ?[ΙΗ] ?Ω ?[ΤΣ] ?[ΙΗ]? ?[ΔΓ] ?Ο ?[Σ\u03a2]', re.MULTILINE),
        enums.Prefecture.FLORINA: re.compile(r'Φ ?Λ ?Ω ?Ρ ?[ΙΗ] ?Ν ?[ΗΖ] ?[Σ\u03a2]', re.MULTILINE),
        enums.Prefecture.PHOCIS: re.compile(r'Φ ?Ω ?Κ ?[ΙΗ] ?[ΔΓ] ?Ο ?[Σ\u03a2]', re.MULTILINE),
        enums.Prefecture.CHALKIDIKI: re.compile(r'[ΧΥ] ?Α ?Λ ?Κ ?[ΙΗ] ?[ΔΓ] ?[ΙΗ] ?Κ ?[ΗΖ] ?[Σ\u03a2]', re.MULTILINE),
        enums.Prefecture.CHANIA: re.compile(r'[ΧΥ] ?Α ?Ν ?[ΙΗ] ?Ω ?Ν', re.MULTILINE),
        enums.Prefecture.CHIOS: re.compile(r'[ΧΥ] ?[ΙΗ] ?Ο ?[ΥΤ]', re.MULTILINE),
    }

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
        logger.info("Parsing file %s", file)
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

    @classmethod
    def extract_prefecture(cls, prefecture_text: str) -> enums.Prefecture:
        """Extract the prefecture from the PDF text.

        :param prefecture_text: The prefecture text.
        :return: The prefecture.
        :raises ValueError: If the prefecture text cannot be parsed.
        """
        for prefecture, prefecture_regex in cls.PREFECTURE_REGEXES.items():
            if prefecture_regex.match(prefecture_text):
                return prefecture

        raise ValueError(f"Could not parse prefecture text: {prefecture_text}")

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

    @abc.abstractmethod
    def extract_data(self, text: str, date: datetime.date) -> dict[enums.DataType, list[dict]] | None:
        """Extract weekly country and prefecture data.

        :param text: The file text.
        :param date: The date for the file.
        :return: The data.
        """


class WeeklyParser(Parser):
    """Parser for weekly data files
    """
    def extract_data(self, text: str, date: datetime.date) -> dict[enums.DataType, list[dict]] | None:
        """Extract weekly country and prefecture data.

        :param text: The file text.
        :param date: The date for the file.
        :return: The data.
        """
        logger.info("Extracting weekly data from file %s", date.isoformat())
        unleaded_95_match = re.search(
            r'Απ ?λ ?[ήι] +Αμ ?όλ ?υβδ ?[ηθ] Β ?ε ?ν ?[ζη] ?ί ?ν[ηθ] +9 ?5 οκ ?τα ?ν ?ίω ?ν', text)
        if not unleaded_95_match:
            logger.error("Could not find weekly data for %s and date %s", enums.FuelType.UNLEADED_95.description,
                         date.isoformat())
            return None

        diesel_match = re.search(
            r'Π ?ε[τη][ρξ] ?[έζ] ?[λι] ?α ?[ιη] ?[ον] +Κ ?ί ?[νλ] ?[ηθε] ?[σςζ] ?[ηθε] ?[ςσο] +'
            r'\( ?B ?i ?o ?d ?i ?e ?s ?e ?l ?\)', text)
        if not diesel_match:
            logger.warning("Could not find weekly data for %s and date %s", enums.FuelType.DIESEL.description,
                           date.isoformat())

        diesel_heating_match = re.search(
            r'Π ?ετ ?ρ ?[έζ] ?λ ?α ?ι ?ο +Θ ?[έζ]? ?ρμ ?αν[σς] ?[ηθ] ?[ςσ] +\(Κα ?τ ?΄ ?ο ?ί ?κ ?ον ?\)', text)
        if not diesel_heating_match:
            logger.warning("Could not find weekly data for %s and date %s", enums.FuelType.DIESEL_HEATING.description,
                           date.isoformat())

        matches = {
            enums.FuelType.UNLEADED_95: text[
                unleaded_95_match.span()[0]:diesel_match.span()[0] if diesel_match else None
            ]
        }
        if diesel_match:
            matches[enums.FuelType.DIESEL] = text[
                diesel_match.span()[1]:(diesel_heating_match.span()[0] if diesel_heating_match else None)
            ]
        if diesel_heating_match:
            matches[enums.FuelType.DIESEL_HEATING] = text[diesel_heating_match.span()[1]:]

        country_data, prefecture_data = [], []
        for fuel_type, prices_text in matches.items():
            # Parse country data
            result = re.search(
                r'[Σ\u03a2][ΤΣ]Α ?Θ ?Μ ?Ι ?[Σ\u03a2] ?Μ ?Ε ?Ν ?Ο ?[Σ\u03a2] *Μ\.? ?\. ?Ο ?\.? ?\*{0,2} ([0-9,\-\s]+)',
                prices_text)
            if not result:
                logger.error("Could not find country data for %s and date %s", fuel_type.description, date.isoformat())
                continue
            lowest_price, highest_price, median_price = self.extract_daily_prices(result[1].strip())
            if any((lowest_price is None, highest_price is None, median_price is None)):
                logger.error("Could not extract daily prices for %s and date %s", fuel_type.description,
                             date.isoformat())
                continue
            country_data.append({
                'fuel_type': fuel_type, 'lowest_price': lowest_price, 'highest_price': highest_price,
                'median_price': median_price
            })

            # Parse prefecture data
            prices_text = re.sub(
                r'ΝΟ ?Μ ?Ο ?[Σ\u03a2]\s+'
                r'ΜΕ ?[Σ\u03a2] ?Η\s+ΚΑ ?[ΤΣ] ?Ω ?[ΤΣ] ?Α ?[ΤΣ] ?Η\s+ΜΕ\s+Φ ?Π ?Α\s+'
                r'ΜΕ ?[Σ\u03a2] ?Η\s+Α ?Ν ?Ω ?[ΤΣ] ?Α ?[ΤΣ] ?Η\s+ΜΕ\s+Φ ?Π ?Α\s+'
                r'(ΔΙΑ ?Μ ?Ε ?[Σ\u03a2] ?Ο ?[Σ\u03a2]|MΕ ?[Σ\u03a2] ?Η)\s+[ΤΣ] ?Ι ?Μ ?Η', '', prices_text, re.MULTILINE)
            results = re.findall(
                r'ΝΟ ?Μ ?Ο ?[Σ\u03a2] +(\D+) ([0-9,\-\s]+)', prices_text, re.MULTILINE)
            if len(results) != len(enums.Prefecture):
                logger.error("Could not find all prefectures for %s and date %s", fuel_type.description,
                             date.isoformat())
                continue
            for result in results:
                prefecture = self.extract_prefecture(result[0])
                lowest_price, highest_price, median_price = self.extract_daily_prices(result[1].strip())
                if any((lowest_price is None, highest_price is None, median_price is None)):
                    logger.error("Could not extract daily prices for %s and date %s", fuel_type.description,
                                 date.isoformat())
                    continue
                prefecture_data.append({
                    'prefecture': prefecture, 'fuel_type': fuel_type, 'lowest_price': lowest_price,
                    'highest_price': highest_price, 'median_price': median_price
                })

        return {enums.DataType.WEEKLY_COUNTRY: country_data, enums.DataType.WEEKLY_PREFECTURE: prefecture_data}

    @staticmethod
    def extract_daily_prices(
            prices: str) -> tuple[decimal.Decimal | None, decimal.Decimal | None, decimal.Decimal | None]:
        """Extract the prices for daily data.

        :param prices: The prices string.
        :return: A tuple with the lowest, highest and median daily price.
        """
        price_matches = re.findall(r'\d[,.][\d ]{3}', prices, re.MULTILINE)
        if len(price_matches) != 3:
            return None, None, None

        return (
            decimal.Decimal(price_matches[0].replace(' ', '').replace(',', '.')),
            decimal.Decimal(price_matches[1].replace(' ', '').replace(',', '.')),
            decimal.Decimal(price_matches[2].replace(' ', '').replace(',', '.'))
        )


class DailyCountryParser(Parser):
    """Parser for daily country data files
    """
    def extract_data(self, text: str, date: datetime.date) -> dict[enums.DataType, list[dict]] | None:
        """Extract daily country data.

        :param text: The file text.
        :param date: The date for the file.
        :return: The data.
        """
        data = []

        matches = {}
        if match := re.search(r'Αμόλ[υσ]βδ[ηθ] 95 οκ ?[τη]\. +([\d.,\- ]+)', text):
            matches[enums.FuelType.UNLEADED_95] = match[1]
        else:
            logger.warning("Cannot find daily country data for %s and date %s", enums.FuelType.UNLEADED_95.description,
                           date.isoformat())
        if match := re.search(r'Αμόλ?[υσ]β ?δ ?[ηθ] +10 ?0 +ο ?κ ?[τη]\. +([\d.,\- ]+)', text):
            matches[enums.FuelType.UNLEADED_100] = match[1]
        else:
            logger.warning("Cannot find daily country data for %s and date %s", enums.FuelType.UNLEADED_100.description,
                           date.isoformat())
        if match := re.search(r'Super +([\d.,\- #ΔΙΑΡ/0!]+)', text):
            matches[enums.FuelType.SUPER] = match[1]
        elif date < SUPER_FINAL_DATE:
            logger.warning("Cannot find daily country data for %s and date %s", enums.FuelType.SUPER.description,
                           date.isoformat())
        if match := re.search(r'Die ?s ?e ?l +Κ ?ί ?ν ?[ηθ] ?[σζς] ?[ηθ] ?[ςσ] +([\d.,\- ]+)', text):
            matches[enums.FuelType.DIESEL] = match[1]
        else:
            logger.warning("Cannot find daily country data for %s and date %s", enums.FuelType.DIESEL.description,
                           date.isoformat())
        if match := re.search(
                r'Die ?s ?e ?l +Θ ?[έζ] ?ρ ?μ ?α ?ν ?[σζς] ?[ηθ] ?[ςσ] +Κ ?α ?[τη] ?΄ ?ο ?ί ?κ ?ο ?ν +([\d.,\- ]+)',
                text):
            matches[enums.FuelType.DIESEL_HEATING] = match[1]
        elif date.month in DIESEL_HEATING_MONTHS:
            logger.warning("Cannot find daily country data for %s and date %s",
                           enums.FuelType.DIESEL_HEATING.description, date.isoformat())
        if match := re.search(
                r'[ΥT]γρ ?α[έσζ] ?ριο\s+κί ?ν[ηθ] ?[σζς] ?[ηθ][ςσ]\s+\(A ?ut ?o ?g ?a ?s ?\) +([\d.,\- ]+)', text):
            matches[enums.FuelType.GAS] = match[1]
        else:
            logger.warning("Cannot find daily country data for %s and date %s", enums.FuelType.GAS.description,
                           date.isoformat())

        for fuel_type, fuel_type_text in matches.items():
            if fuel_type_text.strip():
                matches = re.match(
                    r'(\d? ?\.?\d ?\d ?\d|\d? ?\d? ?\d?|-) +(\d?[,.] ?\d ?\d ?\d|-|#ΔΙΑΙΡ\./0!)', fuel_type_text)
                if not matches or len(matches.groups()) != 2:
                    logger.error("Cannot parse country data for %s and date %s", fuel_type.description,
                                 date.isoformat())
                    continue
                number_of_stations = None
                if matches.group(1) != '-':
                    number_of_stations = int(matches.group(1).replace(' ', '').replace('.', ''))
                price = None
                if matches.group(2) != '-' and matches.group(2) != '#ΔΙΑΙΡ./0!':
                    price = decimal.Decimal(matches.group(2).replace(' ', '').replace(',', '.'))
                if number_of_stations is not None and price is not None:
                    data.append({
                        'fuel_type': fuel_type, 'number_of_stations': number_of_stations, 'price': price
                    })

        return {enums.DataType.DAILY_COUNTRY: data}


class DailyPrefectureParser(Parser):
    """Parser for daily prefecture data files
    """
    def extract_data(self, text: str, date: datetime.date) -> dict[enums.DataType, list[dict]] | None:
        """Extract daily prefecture data.

        :param text: The file text.
        :param date: The date for the file.
        :return: The data.
        """
        fuel_types, last_index = self.extract_fuel_types(text, date)
        if fuel_types is None:
            return None

        # Only search the text after the fuel types
        prices_text = text[last_index:]

        data = []
        results = re.findall(r'ΝΟ ?Μ ?Ο ?[Σ\u03a2] ? (\D+) ([0-9,.\-\s]+)', prices_text, re.MULTILINE)
        if len(results) < len(enums.Prefecture):
            logger.error("Could not find all prefectures for daily prefecture data and date %s", date)
            return None

        for result in results:
            prefecture = self.extract_prefecture(result[0])

            prices = re.findall(r'(\d[,.]\d ?\d ?\d)|-|\n', result[1].strip(), re.MULTILINE)
            if len(fuel_types) - len(prices) == 1 and enums.FuelType.SUPER in fuel_types:
                prices.insert(fuel_types.index(enums.FuelType.SUPER), '-')
            elif len(fuel_types) != len(prices):
                logger.error("Could not parse prices for daily prefecture data and date %s", date)
                return None
            data += [
                {
                    'fuel_type': fuel_type,
                    'prefecture': prefecture,
                    'price': decimal.Decimal(prices[index].replace(' ', '').replace(',', '.'))
                }
                for index, fuel_type in enumerate(fuel_types)
                if prices[index] and prices[index] != '-' and
                decimal.Decimal(prices[index].replace(' ', '').replace(',', '.'))
            ]

        return {enums.DataType.DAILY_PREFECTURE: data}

    @staticmethod
    def extract_fuel_types(text: str, date: datetime.date) -> tuple[list[enums.FuelType] | None, int | None]:
        """Get the fuel types from the PDF text. The fuel types are ordered in the order they appear in the text.

        :param text: The PDF file text.
        :param date: The date.
        :return: A tuple with the ordered fuel types, and the index in the text in which the last fuel type appears.
        """
        # Try to find the fuel type data contained in the file
        fuel_types = []
        if match := re.search(r'Αμόλ[υσ] ?β\s?δ\s?η\s+95\s+ο ?κτ.', text):
            fuel_types.append((enums.FuelType.UNLEADED_95, match.span()))
        else:
            logger.error("Cannot find data for %s and date %s in daily prefecture data",
                         enums.FuelType.UNLEADED_95.description, date.isoformat())
            return None, None

        if match := re.search(r'Αμό ?λ ?[υσ]\s?β\s?δ\s?η\s+100\s+ο ?κ ?τ\s?.', text):
            fuel_types.append((enums.FuelType.UNLEADED_100, match.span()))
        else:
            logger.error("Cannot find data for %s and date %s in daily prefecture data",
                         enums.FuelType.UNLEADED_100.description, date.isoformat())
            return None, None

        if match := re.search(r'Super', text):
            fuel_types.append((enums.FuelType.SUPER, match.span()))
        else:
            logger.warning("Cannot find data for %s and date %s in daily prefecture data",
                           enums.FuelType.SUPER.description, date.isoformat())

        if match := re.search(r'Dies ?e ?l\s+Κίν ?η ?[σς] ?η ?[ςσ]', text):
            fuel_types.append((enums.FuelType.DIESEL, match.span()))
        else:
            logger.error("Cannot find data for %s and date %s in daily prefecture data",
                         enums.FuelType.DIESEL.description, date.isoformat())
            return None, None

        if match := re.search(r'Die ?s ?e ?l\s+Θ[έζ] ?ρ ?μ ?α\s?ν\s?σ\s?η\s*ς\s+Κα ?τ ?΄ ?ο ?ί\s?κ ?ο\s?ν', text):
            fuel_types.append((enums.FuelType.DIESEL_HEATING, match.span()))
        else:
            logger.warning("Cannot find data for %s and date %s in daily prefecture data",
                           enums.FuelType.DIESEL_HEATING.description, date)

        if match := re.search(r'[ΥΤ]γρα ?[έζ] ?ρ\s*ι\s*ο\s+κί ?νη\s?[σς]η[ςσ]\s+\(Aut ?o ?g ?a\s*s\s*\)', text):
            fuel_types.append((enums.FuelType.GAS, match.span()))
        else:
            logger.error("Cannot find data for %s and date %s in daily prefecture data",
                         enums.FuelType.GAS.description, date.isoformat())
            return None, None

        # Sort the fuel types
        fuel_types.sort(key=lambda x: x[1][0])

        return [fuel_type[0] for fuel_type in fuel_types], fuel_types[-1][1][-1] + 1
