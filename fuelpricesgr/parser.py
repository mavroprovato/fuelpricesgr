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
    enums.FuelType.DIESEL: r'Diesel +Κ ?ίν[ηθ][σς][ηθ][ςσ]',
    enums.FuelType.DIESEL_HEATING: r'Diesel Θ[έζ]ρμαν[σς][ηθ][ςσ] (?:Κατ΄ο ?ίκο ?ν)?',
    enums.FuelType.GAS: r'[ΥΤ]γρα[έζ]ρ ?ιο +κίν ?[ηθ][σς][ηθ][ςσ] \(Auto ?g ?a ?s ?\)',
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
        country_data = self.get_country_data(text[:weekly_country_end_data.start(0)], date)

        # Extract weekly country data
        # Try to find "2. Απλή Αμόλυβδη Βενζίνη 95 οκτανίων"
        weekly_prefecture_end_data = re.search(
            r'2\. *Απλ[ήι] +Αμ ?όλ ?υβδ ?[ηθ] Β ?ε ?ν ?[ζη] ?ί ?ν ?[ηθ] +9 ?5 οκ ?τα ?ν ?ίω ?ν', text)
        if not weekly_prefecture_end_data:
            raise ValueError(f"Could not find weekly prefecture data for date {date.isoformat()}")
        prefecture_data = self.get_prefecture_data(
            text[weekly_country_end_data.end(0):weekly_prefecture_end_data.start(0)], date)

        return {enums.DataType.WEEKLY_COUNTRY: country_data, enums.DataType.WEEKLY_PREFECTURE: prefecture_data}

    @staticmethod
    def get_country_data(text: str, date: datetime.date):
        """Get the weekly country data.

        :param text: The weekly country data text.
        :param date: The date.
        :return: The weekly country data.
        """
        data = []
        if match := re.search(
                _FUEL_TYPE_REGEXES[enums.FuelType.UNLEADED_95] +
                r'\s*(?P<number_of_stations>\d\.\d{3})? +(?P<price>\d,[\d ]{3,4})', text):
            data.append({
                'fuel_type': enums.FuelType.UNLEADED_95.value,
                'number_of_stations': WeeklyParser.get_number_of_stations(match.group('number_of_stations')),
                'price': WeeklyParser.get_price(match.group('price')),
            })
        else:
            logger.error("Could not find Unleaded 95 data for date %s", date)

        if match := re.search(
                _FUEL_TYPE_REGEXES[enums.FuelType.UNLEADED_100] +
                r'\s*(?P<number_of_stations>\d\.\d{3})? +(?P<price>\d,[\d ]{3,4})', text):
            data.append({
                'fuel_type': enums.FuelType.UNLEADED_100.value,
                'number_of_stations': WeeklyParser.get_number_of_stations(match.group('number_of_stations')),
                'price': WeeklyParser.get_price(match.group('price')),
            })
        else:
            logger.error("Could not find Unleaded 100 data for date %s", date)

        if match := re.search(
                _FUEL_TYPE_REGEXES[enums.FuelType.DIESEL] +
                r'\s*(?P<number_of_stations>(?:\d\.)?\d{3})? +(?P<price>\d,[\d ]{3,4})',
                text):
            data.append({
                'fuel_type': enums.FuelType.DIESEL.value,
                'number_of_stations': WeeklyParser.get_number_of_stations(match.group('number_of_stations')),
                'price': WeeklyParser.get_price(match.group('price')),
            })
        else:
            logger.warning("Could not find Diesel data for date %s", date)

        if match := re.search(
                _FUEL_TYPE_REGEXES[enums.FuelType.GAS] +
                r'\s*(?P<number_of_stations>(?:\d\.)?\d{3})? +(?P<price>\d,[\d ]{3,4})', text):
            data.append({
                'fuel_type': enums.FuelType.GAS.value,
                'number_of_stations': WeeklyParser.get_number_of_stations(match.group('number_of_stations')),
                'price': WeeklyParser.get_price(match.group('price')),
            })
        elif data_should_exist(enums.FuelType.GAS, date):
            logger.warning("Could not find Gas data for date %s", date)

        if match := re.search(
                _FUEL_TYPE_REGEXES[enums.FuelType.DIESEL_HEATING] +
                r'\s*(?P<number_of_stations>(?:\d\.)?\d{3})? +(?P<price>\d,[\d ]{3,4})', text):
            data.append({
                'fuel_type': enums.FuelType.DIESEL_HEATING.value,
                'number_of_stations': WeeklyParser.get_number_of_stations(match.group('number_of_stations')),
                'price': WeeklyParser.get_price(match.group('price')),
            })
        elif data_should_exist(enums.FuelType.DIESEL_HEATING, date):
            logger.error("Could not find Diesel heating data for date %s", date)

        if match := re.search(
                _FUEL_TYPE_REGEXES[enums.FuelType.SUPER] +
                r'\s*(?P<number_of_stations>(?:\d\.)?\d{1,3})? +(?P<price>\d,[\d ]{3,4})', text):
            data.append({
                'fuel_type': enums.FuelType.SUPER.value,
                'number_of_stations': WeeklyParser.get_number_of_stations(match.group('number_of_stations')),
                'price': WeeklyParser.get_price(match.group('price')),
            })
        elif data_should_exist(enums.FuelType.SUPER, date):
            logger.error("Could not find Super data for date %s", date)

        return data

    @staticmethod
    def get_prefecture_data(text: str, date: datetime.date):
        """Get the weekly prefecture data.

        :param text: The weekly prefecture data text.
        :param date: The date.
        :return: The weekly prefecture data.
        """
        # The standard fuel types included
        fuel_types = [
            enums.FuelType.UNLEADED_95, enums.FuelType.UNLEADED_100, enums.FuelType.DIESEL, enums.FuelType.GAS
        ]
        regexes = [r' +(\d,\d ?\d ?\d)', r' +(\d,\d ?\d ?\d)', r' +(\d,\d ?\d ?\d)', r' +((?:\d,\d ?\d ?\d|-))']
        # Check if super is included
        if re.search(r'Super', text):
            regexes.insert(2, r' +((?:\d,\d ?\d ?\d|-|\s+))')
            fuel_types.insert(2, enums.FuelType.SUPER)
        # Check if diesel heating included
        if data_should_exist(enums.FuelType.DIESEL_HEATING, date):
            regexes.append(r' +((?:\d,\d ?\d ?\d|-))')
            fuel_types.append(enums.FuelType.DIESEL_HEATING)

        data = []
        for prefecture in enums.Prefecture:
            # Parse the prices
            regex = r'Ν ?Ο ?Μ ?Ο ?Σ\s{1,2}' + prefecture.regex + ''.join(regexes)
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
                raise ValueError(f"Could not find weekly prefecture data for {prefecture} and date {date}")

        return data

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
        elif data_should_exist(enums.FuelType.SUPER, date):
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
        elif data_should_exist(enums.FuelType.DIESEL_HEATING, date):
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
